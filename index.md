# 📑 LEMBAR KERJA (JOB SHEET): Integrasi Sistem & Pertukaran Data Biner
**Topik:** Pertukaran Data Protobuf Secara Real-Time via Jaringan Docker dan WSL2  
**Tujuan:** Mempelajari cara membuat, melakukan kompilasi, melakukan serialisasi, dan mengirimkan aliran (*stream*) data biner terstruktur melintasi lingkungan server yang terisolasi menggunakan Protocol Buffers (`protobuf`) dan gRPC.

---

## 🛠️ Langkah 1: Prasyarat Sistem & Konfigurasi Lingkungan
Sebelum menulis kode program, pastikan perangkat komputer berbasis Windows Anda telah memiliki **WSL2 (Ubuntu)** dan **Docker Desktop** yang terkonfigurasi dengan benar.

*   **Cara Menginstal WSL2:** Ikuti panduan resmi di [Microsoft WSL Installation Guide](https://learn.microsoft.com/en-us/windows/wsl/install) untuk menyiapkan lingkungan Linux di Windows Anda.
*   **Cara Menginstal Docker Desktop:** Ikuti panduan resmi di [Docker Desktop Setup Guide](https://docs.docker.com/desktop/install/windows-install/) dan pastikan Anda mencentang opsi **"Use the WSL 2 based engine"** pada menu pengaturan (*settings*) Docker.

---

## 📁 Langkah 2: Membuat dan Memverifikasi Direktori Proyek di Linux
Buka aplikasi **WSL Terminal (Ubuntu)** Anda. Kita akan menggunakan perintah standar Linux untuk membuat folder kerja langsung di dalam file sistem Linux demi performa sistem file yang maksimal.

1. Buat folder utama proyek bersama dengan sub-folder untuk masing-masing server dan definisi skema data dengan menjalankan perintah berikut:
   ```bash
   mkdir -p ~/protobuf-lab/protos ~/protobuf-lab/server-a-sender ~/protobuf-lab/server-b-receiver
   ```
2. Masuk langsung ke dalam folder utama proyek yang baru saja dibuat:
   ```bash
   cd ~/protobuf-lab
   ```
3. **Verifikasi struktur direktori Anda:** Untuk memastikan semua folder telah berhasil dibuat, jalankan perintah daftar (*list*) berikut:
   ```bash
   ls -la
   ```
   *Output yang diharapkan:* Anda akan melihat folder `protos`, `server-a-sender`, and `server-b-receiver` terdaftar di dalam terminal Anda.
4. Buka ruang kerja direktori tersebut menggunakan teks editor Anda (jika menggunakan VS Code di Windows):
   ```bash
   code .
   ```
   *(Perintah ini akan membuka VS Code di Windows dengan file yang tetap terpetakan secara aman langsung di dalam sistem Linux).*

---

## 📜 Langkah 3: Menentukan Skema Protocol Buffer
Di dalam ruang kerja editor Anda, masuk ke dalam folder `protos/` dan buat sebuah file baru bernama `exchange.proto`. File ini berfungsi sebagai kontrak kaku yang mengatur bagaimana data diserialisasikan di dalam jaringan.

**File:** `~/protobuf-lab/protos/exchange.proto`
```protobuf
syntax = "proto3";

package exchange;

message StudentRequest {
    string student_id = 1;
    string student_name = 2;
    int64 sent_timestamp_ns = 3; 
}

message StudentResponse {
    bool status = 1;
}

service ExchangeService {
    rpc SendData (StudentRequest) returns (StudentResponse);
}
```

---

## 🐍 Langkah 4: Mengembangkan Server B (Node Penerima / Receiver)
Masuk ke dalam folder `server-b-receiver/`. Buat skrip implementasi program serta konfigurasi kontainer Docker yang sesuai.

**File:** `~/protobuf-lab/server-b-receiver/main.py`
```python
import time
from concurrent import futures
import grpc
import exchange_pb2
import exchange_pb2_grpc

class StudentDataServer(exchange_pb2_grpc.ExchangeServiceServicer):
    def SendData(self, request, context):
        arrival_time = time.time_ns()
        
        # Menghitung metrik latensi satu arah (one-way latency)
        transmission_time_ms = (arrival_time - request.sent_timestamp_ns) / 1_000_000
        data_size = request.ByteSize()

        print("\n📥 === TRANSAKSI PROTOBUF MASUK ===")
        print(f"NIM Mahasiswa    : {request.student_id}")
        print(f"Nama Mahasiswa   : {request.student_name}")
        print(f"Ukuran Payload   : {data_size} bytes")
        print(f"Waktu Transmisi  : {transmission_time_ms:.4f} ms")
        print("========================================")
        
        return exchange_pb2.StudentResponse(status=True)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    exchange_pb2_grpc.add_ExchangeServiceServicer_to_server(StudentDataServer(), server)
    server.add_insecure_port('[::]:50051')
    print("[Server B] Berjalan di port 50051... Menunggu kiriman data mahasiswa.")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
```

**File:** `~/protobuf-lab/server-b-receiver/Dockerfile`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
RUN pip install grpcio grpcio-tools
COPY . .
CMD ["python", "main.py"]
```

---

## 🚀 Langkah 5: Mengembangkan Server A (Client Pengirim Dinamis)
Masuk ke dalam direktori `server-a-sender/`. Skrip ini menjalankan perulangan (*loop*) antarmuka teks interaktif yang meminta masukan dinamis langsung dari terminal.

**File:** `~/protobuf-lab/server-a-sender/main.py`
```python
import time
import grpc
import exchange_pb2
import exchange_pb2_grpc

def run():
    # Menargetkan Server B menggunakan nama alias kontainer jaringan Docker
    channel = grpc.insecure_channel('receiver-container:50051')
    stub = exchange_pb2_grpc.ExchangeServiceStub(channel)

    print("=== SERVER A: ANTARMUKA ALIRAN DATA PROTOC ===")
    print("Ketik 'exit' pada bagian NIM kapan saja untuk menutup aliran data.\n")

    while True:
        input_id = input("Masukkan NIM Mahasiswa: ")
        if input_id.strip().lower() == 'exit':
            print("\n[Server A] Menutup aliran koneksi. Sampai jumpa!")
            break
            
        input_name = input("Masukkan Nama Mahasiswa: ")
        start_time = time.time_ns()

        # Instansiasi objek kelas kompilasi Protobuf
        student_data = exchange_pb2.StudentRequest(
            student_id=input_id,
            student_name=input_name,
            sent_timestamp_ns=start_time
        )

        payload_size_bytes = student_data.ByteSize()
        print(f" -> Serialisasi Lokal: {payload_size_bytes} bytes")
        print(" -> Mengirimkan...")

        try:
            response = stub.SendData(student_data)
            if response.status:
                print(" -> Ack (Konfirmasi) diterima dari Penerima.\n")
        except grpc.RpcError as e:
            print(f" -> [ERROR] Koneksi gagal: {e}\n")
            break

if __name__ == '__main__':
    run()
```

**File:** `~/protobuf-lab/server-a-sender/Dockerfile`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip install grpcio grpcio-tools
COPY . .
CMD ["python", "main.py"]
```

---

## 🛠️ Langkah 6: Kompilasi Protobuf dan Pembuatan Image Docker
Sebelum menjalankan aplikasi, kita harus membuat kode penunjang (*stub*) Python (`exchange_pb2.py` dan `exchange_pb2_grpc.py`) menggunakan kakas kompilator `grpcio-tools` di dalam WSL, kemudian menyalinnya ke masing-masing direktori aplikasi agar dapat dibundel oleh Docker.

1. **Instal pustaka dependensi kompilasi secara lokal di dalam WSL:**
   ```bash
   pip install grpcio-tools
   ```
2. **Kompilasi file skema data (.proto):**
   ```bash
   python -m grpc_tools.protoc -I./protos --python_out=./server-a-sender --grpc_python_out=./server-a-sender ./protos/exchange.proto
   python -m grpc_tools.protoc -I./protos --python_out=./server-b-receiver --grpc_python_out=./server-b-receiver ./protos/exchange.proto
   ```
3. **Buat Jembatan Jaringan (Network Bridge) Docker yang terisolasi:**
   ```bash
   docker network create integration-net
   ```
4. **Build Image dari masing-masing Kontainer:**
   ```bash
   docker build -t image-server-b ./server-b-receiver
   docker build -t image-server-a ./server-a-sender
   ```

---

## 🖥️ Langkah 7: Eksekusi & Verifikasi (Menggunakan Dua Terminal)

Buka **dua tab atau jendela terpisah** dari WSL Terminal Anda untuk mensimulasikan lingkungan fisik server yang independen.

### 🔳 Terminal 1: Inisialisasi Node Penerima (Server B)
Jalankan perintah ini terlebih dahulu untuk mengaktifkan Server B pada jembatan jaringan kontainer virtual.
```bash
docker run --rm --name receiver-container --network integration-net -p 50051:50051 image-server-b
```
**Tampilan Layar yang Diharapkan:**
```text
[Server B] Berjalan di port 50051... Menunggu kiriman data mahasiswa.
```

### 🔳 Terminal 2: Inisialisasi Antarmuka Pengirim (Server A)
Jalankan Server A dengan flag konfigurasi interaktif (`-it`) untuk mengizinkan interaksi teks langsung pada konsol terminal.
```bash
docker run --rm -it --name sender-container --network integration-net image-server-a
```
**Tampilan Layar & Interaksi Aliran Data yang Diharapkan:**
```text
=== SERVER A: ANTARMUKA ALIRAN DATA PROTOC ===
Ketik 'exit' pada bagian NIM kapan saja untuk menutup aliran data.

Masukkan NIM Mahasiswa: 22010934
Masukkan Nama Mahasiswa: Budi Santoso
 -> Serialisasi Lokal: 26 bytes
 -> Mengirimkan...
 -> Ack (Konfirmasi) diterima dari Penerima.
```

*Ketika Anda melihat kembali ke **Terminal 1**, Anda akan langsung menyaksikan log rincian data terstruktur serta ukuran ukuran payload yang masuk diperbarui secara real-time!*