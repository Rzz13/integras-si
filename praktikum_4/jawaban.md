# LAPORAN PRAKTIKUM INTEGRASI SISTEM INFORMASI

* **Mata Kuliah:** Integrasi Sistem Informasi
* **Pertemuan:** 4 (Empat)
* **Topik Bahasan:** Integrasi Modern Web Services & API Gateway (RESTful HTTP/JSON)
* **Nama:** Muhamad Rizqi Assabiquunal Awwalun
* **NIM:** 2415354060
* **Kelas:** 5D TRPL

---

## Ringkasan Eksekusi & Pengujian Fungsional (Langkah 5.3)

### 1. Pengujian Operasi GET
* **Endpoint:** `GET http://localhost:5000/api/v1/students`
* **Status Respons:** `200 OK`
* **Content-Type:** `application/json`
* **Content-Length:** `328 bytes` (pada kondisi awal 3 data mahasiswa) / `406 bytes` (setelah penambahan data ke-4).
* **Payload Respons:**
```json
{
  "data": [
    {
      "id": "101",
      "nama": "Budi Santoso",
      "jurusan": "Teknik Informatika",
      "status": "Aktif"
    },
    {
      "id": "102",
      "nama": "Siti Aminah",
      "jurusan": "Sistem Informasi",
      "status": "Aktif"
    },
    {
      "id": "103",
      "nama": "Rian Pratama",
      "jurusan": "Teknik Komputer",
      "status": "Cuti"
    },
    {
      "id": "104",
      "nama": "Dewi Sartika",
      "jurusan": "Sistem Informasi",
      "status": "Aktif"
    }
  ],
  "metadata": {
    "format": "JSON",
    "service": "Legacy-Integrated API Gateway",
    "timestamp": 1728876400,
    "total_records": 4
  }
}
```

### 2. Pengujian Operasi POST
* **Endpoint:** `POST http://localhost:5000/api/v1/students`
* **Request Payload:**
```json
{
  "id": "104",
  "nama": "Dewi Sartika",
  "jurusan": "Sistem Informasi",
  "status": "Aktif"
}
```
* **Status Respons:** `201 Created`
* **Content-Type:** `application/json`
* **Verifikasi Berkas Legacy:** Baris `104|Dewi Sartika|Sistem Informasi|Aktif` berhasil ditambahkan di akhir berkas `data.txt`.

### 3. Pengujian Penanganan Kesalahan (Error Handling)
1. **Konflik ID Duplikat (Status 409 Conflict):**
   * *Request:* Mengirim data mahasiswa baru dengan `"id": "104"` yang sudah terdaftar.
   * *Respons:* `{"error": "Conflict", "message": "Data dengan ID 104 sudah ada di sistem legacy"}`
2. **Atribut Kurang / Kosong (Status 422 Unprocessable Entity):**
   * *Request:* Mengirim data tanpa kunci `nama` dan `status`: `{"id": "105", "jurusan": "Informatika"}`.
   * *Respons:* `{"error": "Unprocessable Entity", "message": "Kunci data berikut tidak boleh kosong: nama, status"}`
3. **Payload Kosong (Status 400 Bad Request):**
   * *Request:* Mengirim request POST tanpa body JSON.
   * *Respons:* `{"error": "Bad Request", "message": "Body payload JSON wajib disertakan"}`

---

## Bagian A: Tabel Hasil Pengujian Benchmark

Pengujian dilakukan menggunakan modul `benchmark_serialization.py` dengan membandingkan serialisasi XML (`xml.etree.ElementTree`) dan JSON (`json.dumps` UTF-8) pada variasi jumlah rekaman data yang ditentukan dalam lembar kerja:

| Jumlah Rekaman | Ukuran XML (Bytes) | Ukuran JSON (Bytes) | Persentase Efisiensi Ukuran (%) |
| :--- | :---: | :---: | :---: |
| **10 Data** | 1.438 | 1.166 | **18,92%** |
| **50 Data** | 7.058 | 5.826 | **17,46%** |
| **100 Data** | 14.084 | 11.652 | **17,27%** |
| **500 Data** | 70.684 | 58.652 | **17,02%** |

$$\text{Formula Persentase Efisiensi} = \left( \frac{\text{Ukuran XML} - \text{Ukuran JSON}}{\text{Ukuran XML}} \right) \times 100\%$$

---

## Bagian B: Analisis Pertanyaan Kritis

### 1. Analisis Struktur Payload
**Pertanyaan:** *Berdasarkan pengamatan Anda terhadap teks mentah XML dan JSON, jelaskan faktor sintaksis apa saja yang membuat format XML menghasilkan ukuran data (bytes) yang jauh lebih besar dibandingkan JSON untuk data yang identik!*

**Jawaban:**
Berdasarkan inspeksi terhadap payload biner mentah (*raw string*), faktor-faktor sintaksis utama penyebab tingginya beban ukuran (*payload size overhead*) pada format XML dibandingkan JSON adalah:
1. **Redundansi Tag Penutup Eksplisit (*Closing Tag Redundancy*):**
   Format XML mewajibkan setiap entitas data ditutup dengan tag penutup penuh yang menduplikasi nama elemen induknya, seperti `<jurusan>...</jurusan>`. Untuk setiap baris rekaman mahasiswa, atribut `jurusan` menghabiskan 19 byte hanya untuk tag `<jurusan></jurusan>`. Sebaliknya, JSON hanya membutuhkan satu kali pendefinisian nama kunci (*key*), diikuti pemisah tanda titik dua (`"jurusan": "..."`), dan diakhiri tanda koma `,` tanpa penutup kata kunci berulang.
2. **Ketiadaan Struktur Larik/Array Bawaan pada XML:**
   XML tidak memiliki konsep tipe data larik native. Untuk menyajikan kumpulan data, XML memerlukan hirarki pembungkus berulang: `<students><student>...</student><student>...</student></students>`. Setiap elemen record menyumbang tag pembungkus `<student>...</student>` (19 bytes per item). Sementara JSON merepresentasikan daftar koleksi secara ringkas melalui tanda kurung siku `[...]` dengan pemisah koma `,`.
3. **Overhead Karakter Pembatas Sintaksis (*Delimiter Overhead*):**
   Setiap tag penutup XML membutuhkan minimal 3 karakter tambahan (`<`, `/`, `>`). Pada JSON, representasi objek cukup ditutup dengan sebuah karakter kurung kurawal tunggal `}`.
4. **Penskalaan Linear Beban Overhead Sintaksis:**
   Ketika volume data meningkat menjadi 500 rekaman, ukuran XML mencapai **70.684 bytes**, sedangkan JSON hanya **58.652 bytes**. Format JSON menghemat **12.032 bytes** secara konsisten (~17%–19%) murni karena efisiensi sintaksis tanpa mengurangi kelengkapan data (*lossless syntax compression*).

---

### 2. Analisis Deserialisasi / Parsing di Sisi Klien
**Pertanyaan:** *Jelaskan perbedaan langkah teknis yang harus dilakukan oleh aplikasi peramban web modern (front-end) saat memproses respons XML versus respons JSON! Mengapa ekosistem web modern secara luas beralih ke JSON?*

**Jawaban:**
Perbedaan langkah teknis di sisi peramban web (*browser client*) mencakup:

* **Alur Pemrosesan XML di Front-End:**
  1. *Inisialisasi DOMParser:* Browser menerima payload teks dengan header `Content-Type: application/xml`. Skrip JavaScript harus memanggil parser XML:
     ```javascript
     const parser = new DOMParser();
     const xmlDoc = parser.parseFromString(xmlText, "text/xml");
     ```
  2. *Konstruksi Pohon Objek (DOM Tree):* Engine browser harus mengalokasikan memori untuk menyusun representasi pohon hierarkis penuh (*XML Document Object Model*), di mana setiap simpul dibungkus ke dalam interface Node (`Element`, `Attr`, `Text`).
  3. *Ekstraksi Nilai Melalui Traversal Manual:* Pengembang harus menavigasi pohon DOM menggunakan query seperti `xmlDoc.getElementsByTagName("nama")[0].textContent`.
  4. *Konversi Tipe Data Manual:* Seluruh data hasil parsing XML bersifat string teks. Nilai numerik dan boolean harus dikonversi manual (`parseInt`, `Boolean`).

* **Alur Pemrosesan JSON di Front-End:**
  1. *Native Parsing:* Browser menerima stream data dengan header `Content-Type: application/json`. Skrip cukup mengeksekusi parser native bawaan:
     ```javascript
     const result = await response.json(); // atau JSON.parse(jsonText);
     ```
  2. *Direct Memory Allocation:* Parser JSON terimplementasi langsung pada level engine inti JavaScript (seperti V8 pada Chromium/Node.js) menggunakan bahasa C++. Parser memetakan teks langsung ke struktur heap memory native JavaScript Object / Array dalam satu fase (*single-pass*).
  3. *Akses Properti Langsung:* Objek dapat langsung diakses dengan *dot notation* (`result.data[0].nama`).
  4. *Preservasi Tipe Data:* Tipe data boolean (`true`/`false`), number (`int`/`float`), null, dan array langsung terpetakan sesuai tipe data aslinya.

* **Alasan Migrasi Menyeluruh ke JSON pada Ekosistem Modern:**
  * **Zero-Impedance Mismatch:** JSON adalah superset dari sintaksis objek JavaScript, menjadikannya format pertukaran data yang paling alami bagi platform peramban web.
  * **Performa Eksekusi Jauh Lebih Tinggi:** Benchmark mesin V8 membuktikan `JSON.parse()` puluhan kali lebih cepat dan lebih hemat alokasi memori dibandingkan pembangunan *XML DOM Tree*.
  * **Ergonomi Pengembangan:** Mengurangi kompleksitas kode *boilerplate* traversal data di layer front-end (React, Vue, Angular, mobile SPA).
  * **Efisiensi Jaringan:** Payload berukuran lebih kecil mempercepat *First Contentful Paint (FCP)* dan menghemat konsumsi kuota bandwidth pengguna seluler.

---

### 3. Bottleneck Arsitektur RESTful Synchronous
**Pertanyaan:** *Dalam skenario di mana sistem legacy C membutuhkan waktu 1.5 detik untuk melakukan file locking saat menulis data ke data.txt, apa yang terjadi pada antrean permintaan HTTP jika terdapat 100 klien web yang memanggil POST /api/v1/students secara bersamaan? Jelaskan mengapa komunikasi sinkron pemblokiran (synchronous blocking) pada HTTP/1.1 menjadi bottleneck performa, dan bagaimana arsitektur gRPC (Minggu 5) atau Asynchronous Message Broker (Minggu 6) mengatasi permasalahan tersebut!*

**Jawaban:**

#### A. Dampak pada Antrean Permintaan HTTP (100 Klien Simultan)
1. **Serialisasi Paksa Akibat File Locking (*Contention Serialization*):**
   Karena berkas teks flat `data.txt` menerapkan *exclusive write lock* berdurasi 1,5 detik per operasi, maka operasi I/O disk tidak dapat dilakukan secara paralel. Seluruh 100 permintaan penulisan data dipaksa berjalan berurutan secara serial.
2. **Akumulasi Waktu Tunggu yang Masif (*Latency Stacking*):**
   * Klien ke-1 selesai dalam $\approx 1,5\text{ detik}$.
   * Klien ke-2 selesai dalam $\approx 3,0\text{ detik}$.
   * Klien ke-50 baru terlayani setelah $50 \times 1,5 = \mathbf{75\text{ detik}}$.
   * Klien ke-100 baru terlayani setelah $100 \times 1,5 = \mathbf{150\text{ detik (2,5 menit)}}$.
3. **Koneksi Klien Mengalami Timeout (*Gateway/Client Timeout*):**
   Nilai ambang batas timeout standar pada browser, mobile apps, dan reverse proxy (seperti Nginx) berkisar antara 30 hingga 60 detik. Permintaan klien urutan ke-21 hingga ke-100 akan mengalami kegagalan massal akibat `HTTP 504 Gateway Timeout` atau pemutusan koneksi TCP (`ECONNRESET`).
4. **Kehabisan Sumber Daya Server (*Thread Pool Depletion / Resource Exhaustion*):**
   Server HTTP berbasis model thread/process per connection (misal Gunicorn/uWSGI/Flask) akan menahan *worker threads* dalam kondisi *blocked I/O waiting*. Ketika seluruh alokasi worker terisi penuh, server tidak lagi mampu menerima permintaan baru, memicu penolakan koneksi (*connection refused*) bahkan untuk operasi pembacaan ringan (`GET`).

#### B. Mengapa Synchronous Blocking pada HTTP/1.1 Menjadi Bottleneck?
* **Synchronous Coupling:** Klien terikat secara sinkron dengan siklus I/O server hilir (*tight temporal coupling*). Klien harus mempertahankan socket TCP tetap terbuka dan menunggu secara pasif hingga server menyelesaikan seluruh pekerjaan sebelum menerima respons.
* **Head-of-Line (HoL) Blocking:** Pada HTTP/1.1, satu koneksi TCP hanya dapat melayani satu transaksi request-response dalam satu waktu per pipeline, mencegah pemrosesan konkuren murni di layer transport.

#### C. Solusi Arsitektural Mengatasi Permasalahan Tersebut
1. **Penerapan Asynchronous Message Broker (Minggu 6 - RabbitMQ / Kafka):**
   * *Mekanisme:* Mengubah integrasi sinkron menjadi **Asynchronous Event-Driven Architecture**.
   * *Solusi Alur Kerja:*
     1. Klien mengirim `POST /api/v1/students` ke API Gateway.
     2. API Gateway memvalidasi skema payload, lalu meneruskan pesan ke antrean memori (*message queue*) broker. Operasi penulisan ke antrean in-memory ini selesai hanya dalam **$\approx 1 - 2$ milidetik**.
     3. API Gateway langsung mengembalikan respons `HTTP 202 Accepted` (disertai `tracking_id` atau status berhasil diterima) kepada klien. Klien langsung terbebas dari blocking I/O dan bebas dari risiko timeout.
     4. Di latar belakang, *background worker* mengambil pesan dari antrean satu per satu secara sekuensial (*rate-limited consumption*) untuk ditulis ke berkas `data.txt` sesuai durasi locking 1,5 detik tanpa pernah memblokir layer web service.
2. **Penerapan Arsitektur gRPC / HTTP/2 (Minggu 5):**
   * *Mekanisme:* Memanfaatkan **Binary Framing & Multiplexing** di atas protokol **HTTP/2**.
   * *Solusi Alur Kerja:*
     1. Menghilangkan HoL blocking level transport karena puluhan request dan response biner dapat dikirim secara konkuren dan independen melalui **satu koneksi TCP fisik tunggal** (*bidirectional stream*).
     2. gRPC mendukung mode *Client Streaming*, di mana klien dapat mengalirkan ratusan payload data mahasiswa sekaligus dalam satu saluran koneksi yang persisten.
     3. Server gRPC berbasis arsitektur *event-driven non-blocking* dapat menampung aliran frame biner tanpa mengalokasikan thread terisolasi untuk tiap request, sehingga menghemat konsumsi memori dan thread kernel sistem operasi secara drastis.
