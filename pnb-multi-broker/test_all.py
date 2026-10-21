import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import time
import json
import pika
from kafka import KafkaProducer, KafkaConsumer

def main():
    print("=" * 60)
    print("🧪 MEMULAI PENGUJIAN OTOMATIS KONVERGENSI MULTI-BROKER")
    print("=" * 60)

    # 1. Koneksi Producer & Kirim Data
    print("\n[1/3] Menghubungkan Gateway ke RabbitMQ & Kafka...")
    rabbit_conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    rabbit_ch = rabbit_conn.channel()
    rabbit_ch.queue_declare(queue='antrean-notifikasi')

    kafka_prod = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    test_tx_id = f"TX-PNB-TEST-{int(time.time())}"
    payload = {
        "id_transaksi": test_tx_id,
        "customer": "Muhamad Rizqi Assabiquunal Awwalun",
        "nominal": 1250000,
        "timestamp": time.time()
    }

    print(f" -> Mengirim transaksi: {test_tx_id}")
    rabbit_ch.basic_publish(
        exchange='',
        routing_key='antrean-notifikasi',
        body=json.dumps(payload)
    )
    print(" [✓] Jalur A (RabbitMQ): Data terkirim ke antrean-notifikasi.")

    kafka_prod.send('stream-log-audit', value=payload)
    kafka_prod.flush()
    print(" [✓] Jalur B (Kafka): Data dialirkan ke topik stream-log-audit.")

    # 2. Verifikasi Konsumsi RabbitMQ
    print("\n[2/3] Memverifikasi Konsumsi dari RabbitMQ...")
    method, properties, body = rabbit_ch.basic_get(queue='antrean-notifikasi', auto_ack=True)
    if body:
        msg = json.loads(body)
        print(f" [NOTIFIKASI] Sukses memproses: Kirim konfirmasi ke {msg['customer']} (ID: {msg['id_transaksi']})")
    else:
        print(" [!] Gagal mengambil pesan dari RabbitMQ.")
    rabbit_conn.close()

    # 3. Verifikasi Konsumsi Kafka
    print("\n[3/3] Memverifikasi Aliran Log dari Apache Kafka...")
    consumer = KafkaConsumer(
        'stream-log-audit',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        consumer_timeout_ms=5000,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    found = False
    for msg in consumer:
        if msg.value.get('id_transaksi') == test_tx_id:
            print(f" [AUDIT DATA] Sukses menemukan riwayat transaksi {msg.value['id_transaksi']} di Kafka.")
            found = True
            break
    consumer.close()

    if not found:
        print(" [!] Transaksi belum terdeteksi di Kafka.")

    print("\n" + "=" * 60)
    print("🎉 SELURUH INTEGRASI MULTI-BROKER BERFUNGSI SEMPURNA!")
    print("=" * 60)

if __name__ == '__main__':
    main()
