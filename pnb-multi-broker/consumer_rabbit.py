import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='antrean-notifikasi')

print(' [*] KONSUMEN RABBITMQ: Menunggu tugas masuk... (Tekan Ctrl+C untuk keluar)')

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f" [NOTIFIKASI] Memproses aksi cepat: Kirim konfirmasi ke {data['customer']}")

channel.basic_consume(queue='antrean-notifikasi', on_message_callback=callback, auto_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("\n [!] Konsumen RabbitMQ dihentikan.")
    connection.close()
