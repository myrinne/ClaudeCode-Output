#!/bin/bash
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8
while IFS='|' read -r slug topik; do
  [ -s "jawaban3/$slug.md" ] && continue
  q="Berdasarkan HANYA sumber di notebook ini, jawab untuk catatan ujian board Sp.Ok: $topik. Susun ringkas (maksimal sekitar 600 kata) dengan angka dan kriteria eksplisit, sebut nama sumber/penulis/tahun tiap angka penting. Jawab bahasa Indonesia, istilah medis tetap Inggris/Latin. Bila sebagian tidak ada di sumber, tulis persis 'TIDAK ADA DI SUMBER', jangan mengarang."
  notebooklm ask --new -y "$q" > "jawaban3/$slug.tmp" 2>&1 && mv "jawaban3/$slug.tmp" "jawaban3/$slug.md"
  echo "$slug $(wc -c < jawaban3/$slug.md 2>/dev/null)" >> progress3.log
  sleep 3
done < topik3.txt
echo ALLDONE >> progress3.log
