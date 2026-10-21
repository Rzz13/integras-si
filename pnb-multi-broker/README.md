# Multi-Broker Integration: Konvergensi RabbitMQ & Apache Kafka

**Mata Kuliah:** Integrasi Sistem Informasi  
**Nomor Job Sheet:** 06 / WSL-Hibrida / 2026  
**Topik Praktik:** *Multi-Broker Integration*: Konvergensi RabbitMQ & Apache Kafka di Lingkungan WSL 2 / Windows  
**Nama Mahasiswa:** Muhamad Rizqi Assabiquunal Awwalun  
**NIM:** 2415354060  
**Kelas:** 5D TRPL  

---

## 🏗️ Arsitektur Sistem Hibrida

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 WINDOWS 10/11 OPERATING SYSTEM (HOST)                        │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    DOCKER DESKTOP FOR WINDOWS                         │  │
│  │                                                                       │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │                     WSL 2 LINUX BACKEND                         │  │  │
│  │  │                                                                 │  │  │
│  │  │    [ 🖥️ TERMINAL TAB 3 ]                                        │  │  │
│  │  │   Aplikasi Gateway Pengirim                                     │  │  │
│  │  │         (gateway.py)                                            │  │  │
│  │  │              │                                                  │  │  │
│  │  │              ├─── (Protokol AMQP / Port 5672) ────┐             │  │  │
│  │  │              │                                    │             │  │  │
│  │  │              └─── (Protokol Kafka / Port 9092) ───┼──────┐      │  │  │
│  │  │                                                   │      │      │  │  │
│  │  │                                                   ▼      │      │  │  │
│  │  │                                            ┌───────────┐ │      │  │  │
│  │  │                                            │  RabbitMQ │ │      │  │  │
│  │  │                                            └─────┬─────┘ │      │  │  │
│  │  │                                                  │       │      │  │  │
│  │  │                                          (Antrean Sementara)     │  │  │
│  │  │                                                  │       │      │  │  │
│  │  │                                                  ▼       │      │  │  │
│  │  │                                          [ 📥 TERMINAL 1 ]      │  │  │
│  │  │                                         consumer_rabbit.py      │  │  │
│  │  │                                        (Layanan Notifikasi)      │  │  │
│  │  │                                                          │      │  │  │
│  │  │                                                          ▼      │  │  │
│  │  │                                                    ┌───────────┐│  │  │
│  │  │                                                    │ Apache    ││  │  │
│  │  │                                                    │ Kafka     ││  │  │
│  │  │                                                    └─────┬─────┘│  │  │
│  │  │                                                          │      │  │  │
│  │  │                                                  (Penyimpanan   │  │  │
│  │  │                                                   Permanen)     │  │  │
│  │  │                                                          │      │  │  │
│  │  │                                                          ▼      │  │  │
│  │  │                                                  [ 📥 TERMINAL 2 ]  │  │
│  │  │                                                 consumer_kafka.py   │  │  │
│  │  │                                                 (Layanan Audit)     │  │  │
│  │  │                                                                 │  │  │
│  │  │  Konektivitas: Semua data dikirim melalui alamat 'localhost'    │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📌 Perbedaan Konsep RabbitMQ vs Apache Kafka

| Fitur / Karakteristik | RabbitMQ (Message Broker) | Apache Kafka (Event Streaming Platform) |
| :--- | :--- | :--- |
| **Model Antrean** | *Traditional Queue (Transient)* | *Append-only Commit Log (Persistent)* |
| **Mekanisme Pesan** | Pesan dihapus setelah di-acknowledge (*smart broker, dumb consumer*) | Pesan disimpan secara permanen di disk (*dumb broker, smart consumer*) |
| **Pola Konsumsi** | Point-to-point / Worker queue | Publish-subscribe via Offset log |
| **Kasus Penggunaan** | Layanan Notifikasi (SMS, Email, Push Notification) | Audit Trail, Financial Log, Big Data Analytics, Replay Events |

---

## 📁 Struktur Berkas

```text
pnb-multi-broker/
├── docker-compose.yml       # Konfigurasi RabbitMQ (AMQP 5672), Zookeeper (2181), Kafka (9092)
├── gateway.py               # Producer: mengirim data transaksi ke RabbitMQ & Kafka sekaligus
├── consumer_rabbit.py       # Consumer RabbitMQ: Layanan Notifikasi (Transient)
├── consumer_kafka.py        # Consumer Kafka: Layanan Audit Log (Persistent)
├── test_all.py              # Skrip pengujian otomatis end-to-end
├── requirements.txt         # Dependensi Python (pika, kafka-python)
└── README.md                # Dokumentasi & panduan langkah praktikum
```

---

## 🚀 Panduan Step-by-Step Cara Menjalankan

### Langkah 1: Persiapan Dependensi Python
Pastikan pustaka `pika` dan `kafka-python` telah terpasang:
```bash
pip install -r requirements.txt
```

### Langkah 2: Menyalakan Infrastruktur Multi-Broker (Docker Compose)
Dari dalam folder `pnb-multi-broker`, jalankan:
```bash
docker compose up -d
```
Verifikasi bahwa seluruh kontainer telah berstatus `Up`:
```bash
docker ps
```
Kontainer yang aktif:
* `pnb-rabbitmq` (Port `5672` AMQP, Port `15672` Management UI)
* `pnb-zookeeper` (Port `2181`)
* `pnb-kafka` (Port `9092`)

> 🌐 **RabbitMQ Management Dashboard:** Buka di browser: `http://localhost:15672` (Username: `guest`, Password: `guest`).

---

### Langkah 3: Menjalankan Sistem Menggunakan 3 Terminal (Multi-Tab)

Buka **3 tab terminal berdampingan** di VS Code atau Windows Terminal:

#### 🔳 Terminal Tab 1: Jalankan Konsumen RabbitMQ (Layanan Notifikasi)
```bash
python consumer_rabbit.py
```
*Output yang muncul:*
```text
 [*] KONSUMEN RABBITMQ: Menunggu tugas masuk... (Tekan Ctrl+C untuk keluar)
```

#### 🔳 Terminal Tab 2: Jalankan Konsumen Apache Kafka (Layanan Audit)
```bash
python consumer_kafka.py
```
*Output yang muncul:*
```text
 [*] KONSUMEN KAFKA: Menunggu aliran log audit... (Tekan Ctrl+C untuk keluar)
```

#### 🔳 Terminal Tab 3: Jalankan Gateway Pengirim (Publisher)
```bash
python gateway.py
```
*Output di Terminal Tab 3:*
```text
[INFO] Sukses terhubung ke broker RabbitMQ & Kafka di subsistem WSL 2.
 [✓] Jalur A: Data terkirim ke antrean RabbitMQ.
 [✓] Jalur B: Log digital dialirkan ke topik Kafka.
```

---

### 🔍 Verifikasi Hasil Pengujian
Sesaat setelah `gateway.py` dijalankan, periksa Terminal 1 dan Terminal 2:
1. **Di Terminal 1 (RabbitMQ):**
   ```text
    [NOTIFIKASI] Memproses aksi cepat: Kirim konfirmasi ke Mahasiswa Teknologi Informasi PNB
   ```
2. **Di Terminal 2 (Kafka):**
   ```text
    [AUDIT DATA] Menyimpan riwayat transaksi TX-PNB-2026-WSL2 ke sistem arsip Linux.
   ```

---

### 🧪 Pengujian Otomatis Cepat (Opsional)
Jika ingin menguji seluruh alur integrasi dalam satu perintah cepat:
```bash
python test_all.py
```

---

### 🛑 Langkah 4: Pembersihan Lingkungan (Teardown)
1. Hentikan konsumen di **Terminal 1** dan **Terminal 2** dengan menekan `Ctrl + C`.
2. Di **Terminal 3**, matikan seluruh kontainer:
```bash
docker compose down
```
Semua kontainer dan jaringan virtual akan dimatikan dan dibersihkan dari memori RAM.
