import json
from datetime import datetime
from conexion import conectar_rabbitmq
import pika


def publicar_evento_libro(tipo_evento, datos_libro):
    """
    Publica un evento relacionado con libros en la cola de RabbitMQ
    """
    canal = conectar_rabbitmq()
    if canal is None:
        return

    # Declarar cola para eventos de libros
    canal.queue_declare(queue='eventos_libros', durable=True)

    # Construir mensaje
    mensaje = {
        'tipo': tipo_evento,
        'libro': datos_libro,
        'timestamp': datetime.now().isoformat(),
        'version': '1.0'
    }

    # Publicar mensaje
    canal.basic_publish(
        exchange='',
        routing_key='eventos_libros',
        body=json.dumps(mensaje),
        properties=pika.BasicProperties(
            delivery_mode=2  # Hacer el mensaje persistente
        )
    )

    print(f"[BookTrade] Evento publicado: {tipo_evento}")
