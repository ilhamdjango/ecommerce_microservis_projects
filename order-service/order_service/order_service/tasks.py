import pika, json, os

def send_order_delivered_event(order_id):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST"),
            credentials=pika.PlainCredentials(
                os.getenv("RABBITMQ_USER"),
                os.getenv("RABBITMQ_PASS")
            )
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue='order_events')

    message = json.dumps({"event": "order_delivered", "order_id": order_id})
    channel.basic_publish(exchange='', routing_key='order_events', body=message)
    print(f"✅ Sent: {message}")
    connection.close()