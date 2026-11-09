#!/bin/bash
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8
while IFS='|' read -r slug topik; do
  [ -s "jawaban2/$slug.md" ] && continue
  q="Berdasarkan HANYA sumber di notebook ini, jawab untuk catatan ujian board Sp.Ok: $topik. Susun ringkas (maksimal sekitar 600 kata) dengan angka dan kriteria eksplisit, sebut nama sumber/penulis/tahun tiap angka penting. Jawab bahasa Indonesia, istilah medis tetap Inggris/Latin. Bila sebagian tidak ada di sumber, tulis persis 'TIDAK ADA DI SUMBER', jangan mengarang."
  notebooklm ask --new -y "$q" > "jawaban2/$slug.tmp" 2>&1 && mv "jawaban2/$slug.tmp" "jawaban2/$slug.md"
  echo "$slug $(wc -c < jawaban2/$slug.md 2>/dev/null)" >> progress2.log
  sleep 3
done < topik2.txt
echo ALLDONE >> progress2.log
