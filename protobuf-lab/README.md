# Protobuf Lab: Integrasi Sistem & Pertukaran Data Biner Real-Time

Repositori laboratorium Protocol Buffers (`protobuf`) dan `gRPC` untuk transmisi data biner terstruktur melintasi kontainer Docker dan lingkungan WSL2.

## 📁 Struktur Direktori
```text
protobuf-lab/
├── docker-compose.yml
├── protos/
│   └── exchange.proto
├── server-a-sender/
│   ├── Dockerfile
│   ├── exchange_pb2.py
│   ├── exchange_pb2_grpc.py
│   └── main.py
└── server-b-receiver/
    ├── Dockerfile
    ├── exchange_pb2.py
    ├── exchange_pb2_grpc.py
    └── main.py
```

## 🛠️ Kompilasi Protobuf (Lokal / WSL)
Jika Anda memodifikasi skema file `exchange.proto`, lakukan kompilasi ulang dengan perintah:
```bash
python -m grpc_tools.protoc -I./protos --python_out=./server-a-sender --grpc_python_out=./server-a-sender ./protos/exchange.proto
python -m grpc_tools.protoc -I./protos --python_out=./server-b-receiver --grpc_python_out=./server-b-receiver ./protos/exchange.proto
```

## 🚀 Menjalankan via Docker Compose
Cara termudah untuk mengaktifkan seluruh jaringan kontainer:
```bash
# 1. Jalankan Server B (Receiver) di background:
docker compose up -d receiver

# 2. Jalankan Server A (Sender) dalam mode interaktif:
docker compose run --rm sender
```

## 🖥️ Menjalankan secara Manual via Docker CLI

### 1. Buat Jembatan Jaringan (Docker Bridge Network)
```bash
docker network create integration-net
```

### 2. Build Docker Images
```bash
docker build -t image-server-b ./server-b-receiver
docker build -t image-server-a ./server-a-sender
```

### 3. Jalankan Terminal 1: Node Penerima (Server B)
```bash
docker run --rm --name receiver-container --network integration-net -p 50051:50051 image-server-b
```

### 4. Jalankan Terminal 2: Node Pengirim Interaktif (Server A)
```bash
docker run --rm -it --name sender-container --network integration-net image-server-a
```
Masukkan NIM dan Nama Mahasiswa pada konsol Terminal 2, lalu amati ukuran payload dan waktu transmisi real-time pada Terminal 1.
