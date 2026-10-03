"""
Pengaturan pipeline PDF eksternal.

SATU_NRM_SAMPAI_APPROVE:
  True  -> --tulis utk NRM BARU ditolak selama NRM terakhir yang ditulis
           belum di-approve dokter di EHR (dicek langsung ke EHR). Dipakai
           di paket "automation external pdf" untuk rekan.
  False -> tanpa kunci (versi dr. Vidya sendiri).

BOLEH_APPROVE_OTOMATIS:
  True  -> flag --approve diizinkan: setelah semua field tertulis, Approve
           Dokter di-set Ya + Kirim (versi dr. Vidya, dikonfirmasi 2026-10-03).
  False -> --approve ditolak (paket rekan; file ehr_approve.py juga tidak ikut).
"""

SATU_NRM_SAMPAI_APPROVE = False
BOLEH_APPROVE_OTOMATIS = True
