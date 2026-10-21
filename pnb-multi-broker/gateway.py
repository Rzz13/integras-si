import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import pika
from kafka import KafkaProducer
import json
import time

try:
    # 1. Inisialisasi koneksi internal socket ke RabbitMQ Server di Linux / Localhost
    rabbit_conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    rabbit_ch = rabbit_conn.channel()
    rabbit_ch.queue_declare(queue='antrean-notifikasi')

    # 2. Inisialisasi koneksi internal socket ke Apache Kafka Cluster di Linux / Localhost
    kafka_prod = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print("[INFO] Sukses terhubung ke broker RabbitMQ & Kafka di subsistem WSL 2.")
except Exception as e:
    print(f"[EROR] Koneksi gagal. Pastikan Docker Desktop & WSL Integration aktif. Detail: {e}")
    exit(1)

# Representasi data transaksi bisnis
payload_transaksi = {
    "id_transaksi": "TX-PNB-2026-WSL2",
    "customer": "Mahasiswa Teknologi Informasi PNB",
    "nominal": 1250000,
    "timestamp": time.time()
}

# Jalur A: Pengiriman antrean cepat ke RabbitMQ (Transient Message)
rabbit_ch.basic_publish(
    exchange='',
    routing_key='antrean-notifikasi',
    body=json.dumps(payload_transaksi)
)
print(" [✓] Jalur A: Data terkirim ke antrean RabbitMQ.")

# Jalur B: Aliran data log jangka panjang ke Apache Kafka (Persistent Streaming)
kafka_prod.send('stream-log-audit', value=payload_transaksi)
kafka_prod.flush()
print(" [✓] Jalur B: Log digital dialirkan ke topik Kafka.")

# Pembersihan koneksi
rabbit_conn.close()
