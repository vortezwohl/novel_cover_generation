import json
import logging
import logging.config
import os
from datetime import datetime
import sys
from confluent_kafka import Producer

# 配置环境变量
GROUP_ENV = os.getenv('GROUP_ENV', 'DEV')
APP_ID = 'novel_review_service'  # 你可以根据实际情况设置这个值
Kafka_Server = os.getenv('Kafka_Server', None)
Kafka_Topic = os.getenv('Kafka_Topic', None)

# 定义日志格式
LOG_FORMAT = {
    'timestamp': '%(asctime)s',
    'level': '%(levelname)s',
    'message': '%(message)s',
    'traceId': '%(TraceId)s',
    'spanId': '%(SpanId)s',
    'parentSpanId': '%(parentSpanId)s',
    'url': '%(Url)s',
    'logger': '%(Logger)s',
    'appName': APP_ID,
    'groupEnv': GROUP_ENV,
}


class JsonFormatter(logging.Formatter):
    def format(self, record):
        # 将日志记录转换为字典
        log_entry = LOG_FORMAT.copy()
        log_entry['timestamp'] = str((int)(datetime.now().timestamp()*1000))
        log_entry['level'] = record.levelname
        log_entry['logger'] = record.name
        log_entry['message'] = record.getMessage()
        log_entry['traceId'] = ''
        log_entry['spanId'] = ''
        log_entry['parentSpanId'] = ''
        log_entry['url'] = ''
        # 将字典转换为 JSON 字符串
        return json.dumps(log_entry)


class CustomFilter(logging.Filter):
    def filter(self, record):
        # 只允许特定的日志记录通过
        try:
            return record.levelno >= logging.INFO and (record.name == '__main__' or record.name == 'ffmpeg' or record.name == 'ai-auto-source-video') # 替换成你需要的日志记录器名称
        except Exception:
            return False


def configure_logging(server: str = Kafka_Server, topic: str = Kafka_Topic):
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'custom_formatter': {
                'format': '[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s - %(exc_info)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter':'custom_formatter',
                'stream': sys.stdout,
            },
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    })

    # 创建一个 Kafka 生产者
    def create_kafka_producer(bootstrap_servers):
        producer = Producer({
            'bootstrap.servers': bootstrap_servers,
            'client.id': 'python-logger'
        })
        return producer

    # 自定义 KafkaHandler
    class KafkaHandler(logging.Handler):
        def __init__(self, bootstrap_servers, topic):
            super().__init__()
            self.producer = create_kafka_producer(bootstrap_servers)
            self.topic = topic

        def emit(self, record):
            try:
                # 获取格式化的日志消息
                log_message = self.format(record)
                # 发送消息到 Kafka
                self.producer.produce(self.topic, log_message.encode('utf-8'))
                self.producer.poll(1)  # 处理发送结果
            except Exception:
                self.handleError(record)

    # 替换 StreamHandler 为 KafkaHandler
    if server is None:
        server = Kafka_Server
    if topic is None:
        topic = Kafka_Topic
    if server is None or topic is None:
        return
    kafka_handler = KafkaHandler(bootstrap_servers=server, topic=topic)
    kafka_handler.setLevel(logging.INFO)
    kafka_handler.setFormatter(JsonFormatter())
    kafka_handler.addFilter(CustomFilter())

    # 获取 root logger 并添加 KafkaHandler
    root_logger = logging.getLogger()  # 替换成你需要的日志记录器名称
    root_logger.addHandler(kafka_handler)
