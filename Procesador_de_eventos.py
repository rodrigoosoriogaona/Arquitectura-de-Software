import json
import pika
from conexion import conectar_rabbitmq


def iniciar_procesador_libros():
    """
    Inicia el procesador que escucha eventos de libros
    """
    canal = conectar_rabbitmq()
    if canal is None:
        return

    # Declarar colas
    canal.queue_declare(queue='eventos_libros', durable=True)
    canal.queue_declare(queue='notificaciones', durable=True)

    # Configurar consumo de mensajes
    canal.basic_consume(
        queue='eventos_libros',
        on_message_callback=procesar_evento_libro,
        auto_ack=False
    )

    print("[Procesador] Iniciando procesamiento de eventos...")
    canal.start_consuming()


def procesar_evento_libro(ch, method, properties, body):
    """
    Procesa un evento de libro recibido de RabbitMQ
    """
    try:
        evento = json.loads(body.decode())
        tipo_evento = evento.get('tipo')

        print(f"[Procesador] Procesando evento: {tipo_evento}")

        # Lógica de procesamiento según tipo de evento
        if tipo_evento == 'NUEVO_LIBRO':
            notificar_usuarios_interesados(evento)
        elif tipo_evento == 'OFERTA_RECIBIDA':
            notificar_vendedor_oferta(evento)

        # Confirmar procesamiento
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[Error] No se pudo procesar evento: {e}")


def notificar_usuarios_interesados(evento):
    """
    Notifica a usuarios interesados en un nuevo libro
    """
    libro = evento['libro']
    notificacion = {
        'tipo': 'NUEVO_LIBRO_DISPONIBLE',
        'mensaje': f"Nuevo libro: {libro['titulo']} - ${libro['precio']}",
        'timestamp': evento['timestamp']
    }
    enviar_notificacion(notificacion)


def enviar_notificacion(notificacion):
    """
    Envía una notificación a la cola de notificaciones
    """
    canal = conectar_rabbitmq()
    if canal is None:
        return

    canal.basic_publish(
        exchange='',
        routing_key='notificaciones',
        body=json.dumps(notificacion)
    )


if __name__ == "__main__":
    iniciar_procesador_libros()
