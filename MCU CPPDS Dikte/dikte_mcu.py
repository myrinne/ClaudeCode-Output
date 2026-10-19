"""Dikte MCU CPPDS: rekam anamnesis -> transkrip lokal (faster-whisper) -> susun template (claude -p)
-> tambahkan ke hasil/<tanggal>.md dan salin anamnesis ke clipboard.

Jalankan lewat "Jalankan Dikte MCU.bat". F9 (global) = mulai/stop rekam.
"""
import ctypes
import ctypes.wintypes as wt
import datetime as dt
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext

# ---- pengaturan ----
HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "hasil"
AUDIO_DIR = HERE / "hasil" / "_audio"
PROMPT_FILE = HERE / "instruksi_ringkas.md"
WORK_DIR = Path.home() / ".cache" / "mcu-dikte-work"  # cwd netral untuk claude -p (tanpa CLAUDE.md repo)
WHISPER_MODELS = ["large-v3-turbo", "small"]  # dicoba berurutan; small sudah ada di cache
CLAUDE_MODEL = os.environ.get("DIKTE_CLAUDE_MODEL", "sonnet")
CLAUDE_TIMEOUT = 120
KEEP_AUDIO = False  # audio dihapus setelah transkrip berhasil
HOTKEY_VK = 0x78  # F9
INITIAL_PROMPT = (
    "Pemeriksaan kesehatan calon PPDS FKUI. Anamnesis: keluhan, riwayat penyakit, alergi, obat, "
    "rawat inap, operasi, kacamata, minus, silinder, asma, diabetes, hipertensi, kolesterol, maag, GERD, "
    "merokok, alkohol, program studi Sp1, Sp2, PPDS. Pemeriksaan: serumen, tonsil T1, faring hiperemis, karies, "
    "kelenjar getah bening, tiroid, ronki, wheezing, murmur."
)


def ffmpeg_path():
    p = shutil.which("ffmpeg")
    if p:
        return p
    winget = Path(os.environ["LOCALAPPDATA"]) / "Microsoft" / "WinGet"
    found = sorted((winget / "Links").glob("ffmpeg.exe")) + sorted((winget / "Packages").glob("*FFmpeg*/**/ffmpeg.exe"))
    return str(found[0]) if found else "ffmpeg"


FFMPEG = ffmpeg_path()


def find_mic():
    r = subprocess.run([FFMPEG, "-hide_banner", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                       creationflags=subprocess.CREATE_NO_WINDOW)
    mics = re.findall(r'"([^"]+)" \(audio\)', r.stderr)
    return mics[0] if mics else None


class Recorder:
    def __init__(self, mic):
        self.mic = mic
        self.proc = None
        self.path = None

    def start(self, path):
        self.path = path
        self.proc = subprocess.Popen(
            [FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-f", "dshow", "-i", f"audio={self.mic}",
             "-ac", "1", "-ar", "16000", str(path)],
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW)

    def stop(self):
        try:
            self.proc.communicate(b"q", timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        p, self.proc = self.path, None
        return p


def today_md():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    f = OUT_DIR / f"{dt.date.today():%Y-%m-%d}.md"
    if not f.exists():
        f.write_text(f"# Pemkes CPPDS FKUI — {dt.date.today():%d %B %Y}\n\n", encoding="utf-8")
    return f


def next_number():
    return len(re.findall(r"^## #\d+", today_md().read_text(encoding="utf-8"), flags=re.M)) + 1


def claude_cmd(extra):
    claude = shutil.which("claude") or str(Path.home() / ".local" / "bin" / "claude.exe")
    return [claude, "-p", "--model", CLAUDE_MODEL, "--tools", "", "--strict-mcp-config",
            "--setting-sources", "", "--disable-slash-commands", "--system-prompt-file", str(PROMPT_FILE),
            "--no-session-persistence"] + extra


def user_msg(transcript, identitas):
    return f"IDENTITAS YANG DIKETIK DOKTER: {identitas or '-'}\n\nTRANSKRIP:\n<<<\n{transcript}\n>>>"


def parse_json(text):
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        raise RuntimeError("Output claude bukan JSON: " + text[:200])
    return json.loads(m.group(0))


def run_claude(transcript, identitas):
    """Sekali jalan (lambat, ~20 dtk start-up). Dipakai bila sesi hangat gagal."""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(claude_cmd(["--output-format", "text"]), input=user_msg(transcript, identitas),
                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                       cwd=WORK_DIR, timeout=CLAUDE_TIMEOUT, creationflags=subprocess.CREATE_NO_WINDOW)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip()[:300])
    return parse_json(r.stdout)


class WarmClaude:
    """Satu proses claude stream-json yang sudah dipanaskan. Dipakai untuk SATU peserta lalu ditutup,
    jadi konteks antarpeserta tidak tercampur; start-up ~15 dtk dibayar di latar belakang."""

    def __init__(self):
        WORK_DIR.mkdir(parents=True, exist_ok=True)
        self.p = subprocess.Popen(
            claude_cmd(["--input-format", "stream-json", "--output-format", "stream-json", "--verbose"]),
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
            encoding="utf-8", errors="replace", cwd=WORK_DIR, creationflags=subprocess.CREATE_NO_WINDOW)
        self.ready = threading.Event()
        self.failed = False
        threading.Thread(target=self._warm, daemon=True).start()

    def _send(self, text):
        self.p.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n")
        self.p.stdin.flush()
        for line in self.p.stdout:
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            if ev.get("type") == "result":
                if ev.get("is_error"):
                    raise RuntimeError(str(ev.get("result"))[:300])
                return ev.get("result", "")
        raise RuntimeError("proses claude berhenti")

    def _warm(self):
        try:
            self._send("Pemanasan, belum ada peserta. Balas hanya: {}")
        except Exception:
            self.failed = True
        self.ready.set()

    def ask(self, transcript, identitas):
        try:
            if not self.ready.wait(CLAUDE_TIMEOUT) or self.failed:
                raise RuntimeError("sesi Claude tidak siap")
            return parse_json(self._send(user_msg(transcript, identitas)))
        finally:
            self.close()

    def close(self):
        try:
            self.p.stdin.close()
            self.p.wait(timeout=5)
        except Exception:
            self.p.kill()


def render_entry(no, t, identitas, data, transcript, err):
    ident = identitas or (data or {}).get("identitas") or ""
    lines = [f"## #{no} · {t:%H:%M} · {ident or '(identitas belum diisi)'}", ""]
    if data:
        lines += ["**Anamnesis (sudah di clipboard):**", "", "```text", data["anamnesis"].strip(), "```", ""]
        pf = data.get("pf_abnormal") or []
        lines += ["**PF abnormal (ubah di RM):** " + ("; ".join(pf) if pf else "tidak ada"), ""]
        icd = data.get("icd") or []
        if icd:
            lines += ["**Saran ICD-10 sekunder (cek dulu):**"]
            lines += [f"- `{i['kode']}` {i['nama']} — _{i.get('dasar', '')}_" for i in icd]
            lines += [""]
        cek = data.get("perlu_dicek") or []
        if cek:
            lines += ["**⚠ Perlu dicek:** " + "; ".join(cek), ""]
    else:
        lines += [f"**⚠ Penyusunan otomatis gagal** ({err}). Transkrip mentah di bawah.", ""]
    lines += ["<details><summary>Transkrip</summary>", "", transcript.strip() or "(kosong)", "", "</details>", "", "---", ""]
    return "\n".join(lines)


class Hotkey(threading.Thread):
    """F9 global lewat RegisterHotKey; memanggil callback di thread ini."""

    def __init__(self, cb):
        super().__init__(daemon=True)
        self.cb = cb
        self.ok = None

    def run(self):
        user32 = ctypes.windll.user32
        self.ok = bool(user32.RegisterHotKey(None, 1, 0x4000, HOTKEY_VK))  # MOD_NOREPEAT
        msg = wt.MSG()
        while self.ok and user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == 0x0312:  # WM_HOTKEY
                self.cb()


class App:
    def __init__(self, root):
        self.root = root
        self.ui = queue.Queue()
        self.jobs = queue.Queue()
        self.model = None
        self.model_name = None
        self.recording = False
        self.rec_started = None
        self.last_anamnesis = ""
        self.last_pf = ""

        root.title("Dikte MCU CPPDS")
        root.attributes("-topmost", True)
        root.geometry("520x560")
        top = tk.Frame(root)
        top.pack(fill="x", padx=8, pady=6)
        tk.Label(top, text="Identitas (nama / No RM):").pack(side="left")
        self.ident = tk.Entry(top)
        self.ident.pack(side="left", fill="x", expand=True, padx=4)
        self.btn = tk.Button(root, text="⏺  Rekam  (F9)", font=("Segoe UI", 14, "bold"), bg="#d9f2d9",
                             command=self.toggle, state="disabled")
        self.btn.pack(fill="x", padx=8)
        self.status = tk.Label(root, text="Memuat model Whisper…", anchor="w", fg="#555")
        self.status.pack(fill="x", padx=8, pady=(4, 0))
        self.queue_lbl = tk.Label(root, text="", anchor="w", fg="#555")
        self.queue_lbl.pack(fill="x", padx=8)
        self.out = scrolledtext.ScrolledText(root, wrap="word", font=("Consolas", 10))
        self.out.pack(fill="both", expand=True, padx=8, pady=6)
        row = tk.Frame(root)
        row.pack(fill="x", padx=8, pady=(0, 8))
        tk.Button(row, text="Salin anamnesis", command=lambda: self.copy(self.last_anamnesis)).pack(side="left")
        tk.Button(row, text="Salin PF abnormal", command=lambda: self.copy(self.last_pf)).pack(side="left", padx=4)
        tk.Button(row, text="Buka file hari ini", command=lambda: os.startfile(today_md())).pack(side="right")

        self.mic = find_mic()
        if not self.mic:
            self.status.config(text="❌ Mikrofon tidak ditemukan oleh ffmpeg.", fg="red")
            return
        self.rec = Recorder(self.mic)
        self.warm = WarmClaude()
        root.protocol("WM_DELETE_WINDOW", self.quit)
        threading.Thread(target=self.load_model, daemon=True).start()
        threading.Thread(target=self.worker, daemon=True).start()
        self.hk = Hotkey(lambda: self.ui.put(("toggle", None)))
        self.hk.start()
        root.after(100, self.poll)

    # ---- UI thread ----
    def poll(self):
        try:
            while True:
                kind, val = self.ui.get_nowait()
                if kind == "toggle":
                    if str(self.btn["state"]) == "normal":
                        self.toggle()
                elif kind == "status":
                    self.status.config(text=val, fg="#555")
                elif kind == "ready":
                    self.btn.config(state="normal")
                    hk = "" if self.hk.ok else "  (F9 global tidak tersedia, pakai tombol)"
                    self.status.config(text=f"Siap. Whisper: {self.model_name} · Claude: {CLAUDE_MODEL}{hk}")
                elif kind == "result":
                    self.show(val)
                elif kind == "queue":
                    self.queue_lbl.config(text=val)
        except queue.Empty:
            pass
        if self.recording:
            s = int(time.time() - self.rec_started)
            self.btn.config(text=f"⏹  Stop  (F9)   {s // 60:02d}:{s % 60:02d}")
        self.root.after(200, self.poll)

    def toggle(self):
        if not self.recording:
            AUDIO_DIR.mkdir(parents=True, exist_ok=True)
            self.rec.start(AUDIO_DIR / f"{dt.datetime.now():%Y%m%d-%H%M%S}.wav")
            self.recording, self.rec_started = True, time.time()
            self.btn.config(bg="#f6d0d0")
        else:
            wav = self.rec.stop()
            self.recording = False
            self.btn.config(text="⏺  Rekam  (F9)", bg="#d9f2d9")
            self.jobs.put((wav, self.ident.get().strip(), dt.datetime.now()))
            self.ident.delete(0, "end")
            self.update_queue()

    def quit(self):
        if self.recording:
            self.rec.stop()
        self.warm.close()
        self.root.destroy()

    def update_queue(self):
        n = self.jobs.qsize()
        self.ui.put(("queue", f"Antrian proses: {n}" if n else ""))

    def copy(self, text):
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)

    def show(self, r):
        self.last_anamnesis = r["anamnesis"]
        self.last_pf = r["pf"]
        self.copy(self.last_anamnesis)
        self.out.delete("1.0", "end")
        self.out.insert("end", r["view"])
        self.status.config(text=r["msg"], fg="#1a7f37" if r["ok"] else "#b35900")

    # ---- background ----
    def load_model(self):
        from faster_whisper import WhisperModel
        for name in WHISPER_MODELS:
            try:
                self.ui.put(("status", f"Memuat model Whisper {name}…"))
                self.model = WhisperModel(name, device="cpu", compute_type="int8")
                self.model_name = name
                break
            except Exception:
                continue
        self.ui.put(("ready", None) if self.model else ("status", "❌ Model Whisper gagal dimuat."))

    def worker(self):
        while True:
            wav, ident, t = self.jobs.get()
            self.update_queue()
            no = next_number()
            tag = f"#{no} {ident}".strip()
            try:
                self.ui.put(("status", f"{tag}: transkripsi…"))
                t0 = time.time()
                segs, _ = self.model.transcribe(str(wav), language="id", vad_filter=True, beam_size=1,
                                                initial_prompt=INITIAL_PROMPT)
                transcript = " ".join(s.text.strip() for s in segs)
                t_asr = time.time() - t0
            except Exception as e:
                self.ui.put(("result", {"anamnesis": "", "pf": "", "ok": False,
                                        "view": f"Transkripsi gagal: {e}\nAudio disimpan: {wav}",
                                        "msg": f"{tag}: transkripsi gagal, audio disimpan"}))
                continue
            if not KEEP_AUDIO:
                Path(wav).unlink(missing_ok=True)
            data, err = None, ""
            try:
                self.ui.put(("status", f"{tag}: menyusun template (Claude)…"))
                t1 = time.time()
                warm, self.warm = self.warm, WarmClaude()
                try:
                    data = warm.ask(transcript, ident)
                except Exception:
                    data = run_claude(transcript, ident)
                t_llm = time.time() - t1
            except Exception as e:
                err = str(e) or type(e).__name__
                t_llm = 0
            with today_md().open("a", encoding="utf-8") as f:
                f.write(render_entry(no, t, ident, data, transcript, err))
            if data:
                pf = "\n".join(data.get("pf_abnormal") or [])
                icd = "\n".join(f"{i['kode']}  {i['nama']}" for i in data.get("icd") or [])
                cek = "\n".join("• " + c for c in data.get("perlu_dicek") or [])
                view = (data["anamnesis"].strip() + "\n\n— PF abnormal —\n" + (pf or "tidak ada") +
                        "\n\n— Saran ICD-10 —\n" + (icd or "-") + ("\n\n— ⚠ Perlu dicek —\n" + cek if cek else ""))
                msg = f"✅ {tag}: anamnesis sudah di clipboard (ASR {t_asr:.0f}s + Claude {t_llm:.0f}s)"
                self.ui.put(("result", {"anamnesis": data["anamnesis"].strip(), "pf": pf, "view": view,
                                        "ok": True, "msg": msg}))
            else:
                self.ui.put(("result", {"anamnesis": transcript, "pf": "", "ok": False,
                                        "view": f"Penyusunan gagal ({err}).\n\nTranskrip mentah (di clipboard):\n\n{transcript}",
                                        "msg": f"⚠ {tag}: Claude gagal, transkrip mentah di clipboard"}))


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
