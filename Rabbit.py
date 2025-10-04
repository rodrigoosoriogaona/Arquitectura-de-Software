import pika

def conectar_rabbitmq():
    """
    Establece conexión con RabbitMQ local

    Returns:
        canal: Canal de comunicación con RabbitMQ
    """
    try:
        conexion = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        canal = conexion.channel()
        print("[Sistema] Conexión establecida con RabbitMQ")
        return canal
    except Exception as e:
        print(f"[Error] No se pudo conectar a RabbitMQ: {e}")
        return None
