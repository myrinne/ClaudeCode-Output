#!/bin/bash
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8
while IFS='|' read -r slug topik; do
  [ -s "jawaban/$slug.md" ] && continue
  q="Berdasarkan HANYA sumber di notebook ini, jelaskan untuk catatan ujian board Sp.Ok: $topik. Susun jawaban dengan sub-judul: (1) Teknik langkah demi langkah, (2) Temuan normal, (3) Interpretasi temuan abnormal dan nilai diagnostik/cut-off bila ada, (4) Relevansi pada pemeriksaan pekerja (PAK/MCU) bila disebut sumber. Jawab bahasa Indonesia, istilah medis tetap Inggris/Latin. Bila sebagian poin tidak ada di sumber, tulis persis 'TIDAK ADA DI SUMBER' pada poin itu, jangan mengarang."
  notebooklm ask --new -y "$q" > "jawaban/$slug.tmp" 2>&1 && mv "jawaban/$slug.tmp" "jawaban/$slug.md"
  echo "$slug done $(wc -c < jawaban/$slug.md 2>/dev/null)" >> progress.log
  sleep 3
done < topik.txt
echo ALLDONE >> progress.log
