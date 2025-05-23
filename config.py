import json
import os
from python_apollo_client import ApolloClient
from types import ModuleType
from enum import Enum


class AppConfig(ModuleType):
    """
    获取阿波罗配置
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        初始化Apollo配置客户端
        """
        if not self._initialized:
            self._initialized = True
        # 根据环境变量选择配置文件
            environment = os.environ.get('OS_ENV') 
            if environment == None:
                environment = 'dev'
            config_file = 'appconfig_' + environment + '.json'
            with open(config_file) as f:
                config = json.load(f).get('apollo')

            app_id = config.get('app_id')
            cluster = config.get('cluster')
            config_server_url = config.get('config_server_url')
            env = config.get('env')

            self.client = ApolloClient(app_id=app_id,cluster=cluster,config_server_url=config_server_url,username='',password='')
            self.client.start()

    def get_value(self, key: str, namespace='application') -> any:
        return self.client.get_value(key=key, default_val="*", namespace=namespace)
    
    def list_keys(self, namespace='application') -> list:
        return self.client._cache[namespace].keys()


class SettingKey(Enum):
    Kafka_HOST= 'Kafka:Servers'
    '''日志消息队列'''
    Kafka_TOPIC= 'Kafka:Topic'
    '''日志消息队列主题'''
