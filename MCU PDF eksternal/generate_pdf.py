"""
LANGKAH 4 — entry gabungan -> draft teks 8 field EHR
=====================================================

Memakai fungsi format_* dari fase3a_generate_teks.py lama APA ADANYA.
Satu-satunya beda dari pipeline lama (dikonfirmasi dr. Vidya, 2026-10-03):

  Data belum lengkap (EKG usia >=35 / tanda vital) di pipeline lama ->
  "Saat ini belum dapat diberikan status kelaikan kerja ...". Untuk pasien
  PDF eksternal, kelaikan TETAP diberikan berdasarkan temuan yang ada,
  disambung "... dan melengkapi pemeriksaan X", mis.
      "Laik kerja dengan catatan memerlukan konsultasi dengan dokter terkait
       temuan hasil MCU dan melengkapi pemeriksaan EKG"
  Saran "Mohon segera lengkapi: ..." tetap ada.

Implementasinya ada di MCU automation/kelaikan_final.py. Caranya:
protocol_engine dijalankan DUA kali. Run 1 = data asli (dipakai utk
semua teks: kesimpulan, "EKG : Belum dilakukan", saran). Run 2 = salinan
dengan item yang belum lengkap diisi nilai NETRAL (EKG normal, TD 110/70)
HANYA untuk menghitung jumlah temuan -> kelaikan. Nilai netral itu tidak
pernah muncul di teks mana pun.
"""

import _jalur  # noqa: F401
from kelaikan_final import generate_draft_final

# Logika "kelaikan tetap diberikan walau data belum lengkap" dipindah ke
# MCU automation/kelaikan_final.py (2026-10-03) supaya dipakai bersama
# dengan fase_batch.py --final (MCU yang sudah final).


def generate_draft_pdf(entry):
    """Return dict: nama, nip, draft, catatan_manual, flag, flag_alasan, temuan."""
    return generate_draft_final(entry, sumber="aturan pasien PDF eksternal")
