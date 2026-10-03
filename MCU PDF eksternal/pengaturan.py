"""
Pengaturan pipeline PDF eksternal.

SATU_NRM_SAMPAI_APPROVE:
  True  -> --tulis utk NRM BARU ditolak selama NRM terakhir yang ditulis
           belum di-approve dokter di EHR (dicek langsung ke EHR, bukan
           dari catatan lokal). Dipakai di paket "automation external pdf"
           yang dibagikan ke rekan, supaya setiap hasil pasti dibaca dulu
           sebelum pasien berikutnya.
  False -> tanpa kunci (versi dr. Vidya sendiri).
"""

SATU_NRM_SAMPAI_APPROVE = False
