import pika
import json
import datetime
import traceback
import socket

class LogAnalysisClient:
    def __init__(self, service_name, rabbitmq_host="localhost", rabbitmq_port=5672):
        self.service_name = service_name
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_port = rabbitmq_port
        self.connection = None
        self.channel = None
        self.queue_name = "log_errors"
        self._connect()

    def _connect(self):
        try:
            credentials = pika.PlainCredentials("user", "password")
            parameters = pika.ConnectionParameters(
                self.rabbitmq_host, self.rabbitmq_port, "/", credentials
            )
            self.connection = pika.BlockingConnection(parameters)
        except pika.exceptions.ProbableAuthenticationError:
            # Fallback for local testing if user/password fails
            print("Auth failed, trying guest/guest...")
            credentials = pika.PlainCredentials("guest", "guest")
            parameters = pika.ConnectionParameters(
                self.rabbitmq_host, self.rabbitmq_port, "/", credentials
            )
            self.connection = pika.BlockingConnection(parameters)
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")
            return

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=False)

    def send_error(self, message, exc_info=None):
        if not self.channel or self.connection.is_closed:
            self._connect()
            if not self.channel:
                print("Error: Could not send log, no connection.")
                return

        stack_trace = None
        if exc_info:
            stack_trace = "".join(traceback.format_exception(*exc_info))

        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "level": "ERROR",
            "service": self.service_name,
            "message": str(message),
            "stack_trace": stack_trace,
            "hostname": socket.gethostname()
        }

        try:
            self.channel.basic_publish(
                exchange="",
                routing_key=self.queue_name,
                body=json.dumps(log_entry)
            )
            # print(f" [SDK] Sent ERROR log: {message}")
        except Exception as e:
            print(f"Failed to publish message: {e}")

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
