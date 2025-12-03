from .client import LogAnalysisClient
from .handlers import RabbitMQLogHandler, install_excepthook

_client = None

def init(service_name, rabbitmq_host="localhost", rabbitmq_port=5672):
    global _client
    _client = LogAnalysisClient(service_name, rabbitmq_host, rabbitmq_port)
    return _client

def get_client():
    if _client is None:
        raise RuntimeError("SDK not initialized. Call sdk.init() first.")
    return _client

def install(service_name, rabbitmq_host="localhost", rabbitmq_port=5672):
    """
    Helper to initialize the client and install the global exception hook.
    """
    client = init(service_name, rabbitmq_host, rabbitmq_port)
    install_excepthook(client)
    return client
