### Latihan hitung yang paling mungkin keluar

Semua angka di bawah sudah diperiksa ulang secara numerik.

#### 1. Tabel 2×2 (soal yang keluar 4×)

Pajanan tinggi: sakit 40, tidak sakit 40. Pajanan rendah: sakit 20, tidak sakit 60.

| Ukuran | Rumus | Hasil |
|---|---|---|
| Risk pajanan tinggi | $a/(a+b) = 40/80$ | 0,50 |
| Risk pajanan rendah | $c/(c+d) = 20/80$ | 0,25 |
| Risk ratio (RR) | $0{,}50/0{,}25$ | **2,0** |
| Odds ratio (OR) | $(a \times d)/(b \times c) = (40 \times 60)/(40 \times 20)$ | **3,0** |
| Risk difference | $0{,}50 - 0{,}25$ | 0,25 (25 per 100) |
| Attributable risk percent | $(RR-1)/RR = (2-1)/2$ | 50% |
| 95% CI RR | $\exp[\ln 2 \pm 1{,}96 \times 0{,}2236]$ | 1,29 sampai 3,10 |
| 95% CI OR | $\exp[\ln 3 \pm 1{,}96 \times 0{,}3416]$ | 1,54 sampai 5,86 |
| 95% CI selisih proporsi | $0{,}25 \pm 1{,}96 \times 0{,}0740$ | 0,105 sampai 0,395 |
| Chi-square | semua expected ≥5 (30; 50; 30; 50) → $\chi^2 = 10{,}67$, df 1 | p ≈ 0,001 |

Pembahasan pilihan jawaban di soal aslinya: **"odds penyakit 3 kali lebih tinggi pada pajanan tinggi" benar** (OR = 3). "50% lebih mungkin" salah karena risikonya 2× (100% lebih tinggi). "Tidak ada perbedaan" dan "risiko 67%" salah. Untuk RR < 1 atau OR < 1, bacalah sebagai efek protektif.

!PEARL Penyakit yang sering (risk 25% sampai 50%) membuat OR menjauh dari RR (di sini 3,0 vs 2,0). OR hanya mendekati RR bila penyakit langka (risk kurang dari kira-kira 10%).

#### 2. Attack rate

175 pekerja hadir di piknik. 99 makan salad kentang dan 30 di antaranya sakit. **Food-specific attack rate = 30/99 = 30,3%.** Untuk menentukan penyebab, hitung juga attack rate pada yang tidak makan salad (76 orang) lalu bandingkan sebagai risk ratio.

#### 3. Sensitivitas, spesifisitas, PPV, NPV

Sebuah tes skrining pada 1.000 pekerja, sensitivitas 90%, spesifisitas 80%.

| Prevalensi | Sakit | TP | FN | FP | TN | PPV | NPV |
|---|---|---|---|---|---|---|---|
| 10% | 100 | 90 | 10 | 180 | 720 | $90/270$ = **33,3%** | $720/730$ = 98,6% |
| 1% | 10 | 9 | 1 | 198 | 792 | $9/207$ = **4,3%** | $792/793$ = 99,9% |

Sensitivitas $= TP/(TP+FN)$ = kemampuan tes mengidentifikasi yang SAKIT. Spesifisitas $= TN/(TN+FP)$ = kemampuan mengidentifikasi yang TIDAK sakit. Prevalensi turun, PPV turun tajam, NPV naik.

#### 4. Batas 95% distribusi normal

Acetylcholinesterase eritrosit: mean 7,20 dan SD 1,10 U/g hematokrit. Batas 95% individu $= 7{,}20 \pm 1{,}96 \times 1{,}10$ = **5,04 sampai 9,36**, jawaban terdekat di soal asli: 5,00 dan 9,40. Jangan memakai SE (itu untuk CI rata-rata).

#### 5. SMR dan healthy worker effect

SMR = observed/expected $\times 100$. Contoh: 30 kematian teramati, 20 diharapkan dari populasi umum → SMR = 150. Bila kohort pekerja sehat menunjukkan SMR 80 untuk semua penyebab, itu pola khas healthy worker effect, dan SMR penyakit tertentu yang tampak normal bisa menutupi risiko yang sebenarnya meningkat.

#### 6. Attributable risk dan PAF

Risk terpajan 0,50, risk tidak terpajan 0,25, RR 2. AR = 0,25. AR% = (RR−1)/RR = 50%. Bila 30% populasi pekerja terpajan, PAF (Levin) $= p(RR-1)/[1+p(RR-1)] = 0{,}3/1{,}3$ = 23,1%.

### Catatan kualitas dan sumber

- Isi J.1 sampai J.22 berasal dari jawaban NotebookLM (notebook "Board Notes - Epidemiologi") atas pertanyaan yang diajukan satu per satu. Sumbernya: CDC Principles of Epidemiology (Lesson 3 dan 6), CDC Field Epidemiology Manual, Penn State STAT 507, NCBI Bookshelf (skrining), review healthy worker effect (Chowdhury 2017, Algarni 2020, Brown 2017), Bradford Hill (versi WHO), Wikipedia, dan GraphPad.
- Beberapa sumber gagal di-import ke notebook (cebm.net, beberapa halaman Wikipedia). Topik attributable risk, PAF, hazard ratio, dan PMR sebagian besar mengandalkan pengetahuan umum; bagian itu ditandai dengan kotak catatan sumber. **Verifikasi ke buku teks (Gordis, Rothman, Beaglehole) sebelum dihafal.**
- Rumus CI untuk RR dan OR (log-transform) dan nilai PAF di J.23 saya hitung ulang secara numerik.
- Belum ada pemeriksaan visual di Word atau Obsidian.
