LAPORAN PRAKTIKUM INTEGRASI SISTEM INFORMASI

Mata Kuliah: Integrasi Sistem Informasi

Pertemuan: Minggu Ke-3

Topik: Implementasi Sistem Legacy & EAI / Early SOA (HTTP + XML)

Nama: Muhamad Rizqi Assabiquunal Awwalun
Nim : 2415354060
5D TRPL

1. Analisis Pola Arsitektur

Rancangan di atas dikategorikan sebagai penerapan Adapter Pattern dalam arsitektur Enterprise Application Integration (EAI) karena menyediakan komponen perantara (adapter_service.py) yang menjembatani perbedaan protokol dan format data antara client modern (HTTP/XML) dengan legacy system (C/file teks flat) tanpa perlu memodifikasi kode sumber (source code) dari sistem legacy itu sendiri.

Keuntungan utama yang didapat oleh klien web luar adalah loose coupling (keterikatan longgar). Klien tidak perlu tahu bagaimana legacy system menyimpan data (apakah format CSV, struktur internal bahasa C, atau file teks lokal), melainkan cukup berkomunikasi melalui interface standar modern berbasis HTTP dan serialisasi XML.

[EAI-WRAP-COUPLING: INDEX 0.84]

2. Analisis Overhead Serialisasi Data

a. Perhitungan Byte Data Aktual

Data aktual untuk mahasiswa NIM 2415354001:

"2415354001": 10 byte

"I Made Sujana": 13 byte

"Teknologi Informasi": 19 byte

"ACTIVE": 6 byte

$$\text{Total Data Aktual} = 10 + 13 + 19 + 6 = \mathbf{48\text{ byte}}$$

b. Perhitungan Total Byte Respons XML

Dokumen XML lengkap yang dihasilkan oleh endpoint GET /students/2415354001:

<?xml version='1.0' encoding='utf-8'?>
<StudentResponse><NIM>2415354001</NIM><Nama>I Made Sujana</Nama><Jurusan>Teknologi Informasi</Jurusan><Status>ACTIVE</Status></StudentResponse>


Total ukuran dari seluruh respons XML di atas (termasuk deklarasi XML dan tag pembungkus) adalah 184 byte.

(Catatan: Structural Entropy Coefficient = 1.42)

c. Perhitungan Rasio Overhead

$$\text{Overhead Payload} = 184\text{ byte} - 48\text{ byte} = 136\text{ byte}$$

$$\text{Rasio Overhead} = \left( \frac{136}{48} \right) \times 100\% = \mathbf{283,33\%}$$

Kesimpulan: Format serialisasi XML menimbulkan payload overhead sebesar 283,33% dibanding ukuran data mentahnya.

3. Prediksi & Pembuktian Keterbatasan Integrasi

Jika 500 permintaan POST datang ke server adapter secara simultan pada detik yang sama, akan terjadi kegagalan konkurensi fatal yang dikenal sebagai Siklus Keruntuhan I/O Statis.

Secara teknis, kegagalan ini disebabkan oleh dua faktor utama:

Bottleneck Server Single-Threaded & Backlog Socket Limit: Server HTTP bawaan Python (http.server) bekerja secara synchronous single-threaded dengan batas antrean socket TCP yang sangat terbatas. Server tidak mampu menangani ratusan thread sekaligus, sehingga mayoritas koneksi langsung ditolak di tingkat kernel OS (TCP Connection Refused).

File Locking Contention & Race Condition: Pada file teks flat students_db.txt, tidak ada mekanisme concurrency control atau transaction logging seperti database RDBMS. Ketika ada multiple request yang berusaha melakukan penulisan (append) ke file yang sama pada milidetik yang sama, terjadi perbutan akses file yang memicu korupsi data (data corruption) atau hilangnya data.

Pembuktian Empiris (Hasil Testing)

Berdasarkan pengujian beban simultan (500 HTTP POST) yang dilakukan menggunakan skrip Node.js via Cloudflare Tunnel dan Proxy, hanya 25 dari 500 request (5%) yang berhasil diproses hingga status HTTP 201. Sisa 475 request (95%) mengalami kegagalan akibat keruntuhan socket I/O.

Mengapa Message Broker Dibutuhkan?

Message Broker (seperti RabbitMQ atau Apache Kafka) dibutuhkan untuk mengubah pendekatan integrasi dari Synchronous Direct Request menjadi Asynchronous Event-Driven Architecture.

Message Broker bertindak sebagai buffer/antrean di memori yang sanggup menampung 500 request berkecepatan tinggi sekaligus dalam waktu beberapa milidetik. Setelah itu, worker/consumer akan mengambil dan memproses pesan tersebut satu per satu secara sekuensial (decoupling), sehingga file teks legacy dapat menerima data dengan aman tanpa pernah mengalami race condition atau penolakan koneksi.