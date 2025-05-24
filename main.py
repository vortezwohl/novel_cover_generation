import os
import uuid
from concurrent.futures import ThreadPoolExecutor

import redis
import requests
import base64
import hashlib
import logging
import hmac
import json
import time

from cdLogger import configure_logging
from config import SettingKey, AppConfig
from cpu_usage import check_cpu_usage
from covgen.api import simple_cover_gen, CoverGenReq

client = AppConfig()
configure_logging(client.get_value(SettingKey.Kafka_HOST.value), client.get_value(SettingKey.Kafka_TOPIC.value))
logger = logging.getLogger(__name__)

SecretKey = "**CdAi2024@cDaI!GROUP**"
failedStatus = 3
THREAD_POOL = ThreadPoolExecutor(max_workers=8)
REDIS_TASK_TYPE = 25


def hash_sign(body):
    body_bytes = body.encode('utf-8')
    key_bytes = SecretKey.encode('utf-8')
    # 创建 HMAC-SHA256 对象并计算哈希值
    hmacsha256 = hmac.new(key_bytes, digestmod=hashlib.sha256)
    hmacsha256.update(body_bytes)
    # 获取哈希结果
    hashed_result = hmacsha256.digest()
    # 如果需要将结果转换为十六进制字符串表示形式
    encrypted_body_base64 = base64.b64encode(hashed_result).decode()
    return encrypted_body_base64


def update_status(taskId, status, content, callback_url, step='筛书判否', callback_data="", is_forced=True):
    max_tries = 3
    data = {
        "data": callback_data,
        "taskId": int(taskId),
        "comment": content,
        "Step": step,
        "taskStatus": int(status),
        "isForced": is_forced,
    }
    hash_sign_body = hash_sign(json.dumps(data))
    header = {"sign": hash_sign_body, "Content-Type": "application/json"}

    logger.info(f"回调请求体参数：{data}")
    for attempt in range(max_tries):
        try:
            r = requests.post(callback_url, json=data, headers=header)
            logger.info(f"任务：{taskId}，回调接口连接成功，接口返回内容：{r.json()}")
            if r.status_code == 200:
                return True
            else:
                logger.warning(f"任务：{taskId}，回调接口返回非200，请求体参数：{data}")
        except Exception as e:
            logger.error(
                f"任务：{taskId}，回调状态失败，请求体参数：{data} , 错误信息：{e} ，重试次数：{attempt + 1}/{max_tries}")

        if attempt < max_tries - 1:
            logger.warning(f"任务：{taskId}，回调接口连接失败，正在重试中，重试次数：{attempt + 1}/{max_tries}")
            time.sleep(2)
        else:
            logger.error(f"任务：{taskId}，回调接口连接失败，请求体参数：{data},所有重试均失败，放弃请求。")
    return False


def parse_redis_data(data):
    key = data[0].decode()  # 解码键
    entries = data[1]
    parsed_entries = []
    for entry in entries:
        entry_id, details = entry
        parsed_details = {k.decode().lower(): v.decode() for k, v in details.items()}  # 解码字典中的每个键和值
        parsed_entries.append((entry_id.decode(), parsed_details))  # 解码条目ID
    return key, parsed_entries


def get_taskid_status(taskId, url):
    data = {
        "taskType": REDIS_TASK_TYPE,
        "taskIds": [int(taskId)]
    }
    hash_sign_body = hash_sign(json.dumps(data))
    header = {"sign": hash_sign_body, "Content-Type": "application/json"}
    logger.info(f"回调请求体参数：{data}")
    try:
        r = requests.post(url, json=data, headers=header)
        logger.info(f"任务：{taskId}，回调接口连接成功，接口返回内容：{r.json()}")
        if r.status_code == 200:
            taskid_status = str(r.json()['data'][0]['taskStatus'])
            return taskid_status
        else:
            logger.warning(f"任务：{taskId}，回调接口返回非200，请求体参数：{data}")
            return 0
    except Exception as e:
        logger.warning(f"任务：{taskId}请求任务状态失败，请求体参数：{data} , 错误信息：{e}，执行任务。")
        return 0


def handle_msg(kwargs: dict):
    message = kwargs.get('message')
    queue_tag = kwargs.get('queue_tag')
    environment = kwargs.get('env')
    _client = kwargs.get('client')
    stream_name = kwargs.get('stream_name')
    normal_group_name = kwargs.get('normal_group_name')

    stream, msg_line = parse_redis_data(message)
    message_id, rec_json = msg_line[0]
    logger.info(f"\n收到 {queue_tag} 队列信息：{rec_json}")
    callbackurl = str(rec_json["callbackurl"])
    callbackstatus = str(rec_json["callbackstatus"])
    taskid = str(rec_json["taskid"])
    task_ext_info = None
    task_ext_info_req_data = {'taskType': REDIS_TASK_TYPE, 'taskId': int(taskid)}
    if environment == 'prod' and environment == 'stage':
        url = "https://ai-main-none.changdu.vip/Task/GetTaskStatus"
        ext_url = 'https://ai-main-none.changdu.vip/Task/GetTaskExtInfo'
        taskid_status = get_taskid_status(taskid, url)
        task_ext_info = requests.post(url=ext_url, json=task_ext_info_req_data).json().get('ext', dict())
    else:
        url = "https://ai-main-none-dev.changdu.ltd/Task/GetTaskStatus"
        ext_url = 'https://ai-main-none-dev.changdu.ltd/Task/GetTaskExtInfo'
        taskid_status = get_taskid_status(taskid, url)
        task_ext_info = requests.post(url=ext_url, json=task_ext_info_req_data).json().get('ext', dict())
    if taskid_status == '-1':
        _client.xack(stream_name, normal_group_name, message_id)
        return
    st_time = time.time()
    task_ext_info = json.loads(task_ext_info)
    # 业务逻辑开始
    task_type = task_ext_info.get("task_type", str())
    novel_content: str = task_ext_info.get("novel", str())
    title: str = task_ext_info.get("title", str())
    title_color: list = task_ext_info.get("title_color", None)
    title_height_correction: float = task_ext_info.get("title_height_correction", .0)
    resample: int = task_ext_info.get("resample", 4)
    task_status = False
    try:
        callback_data = str()
        match task_type:
            case 'simple':
                callback_data = json.dumps(simple_cover_gen(CoverGenReq(
                    novel=novel_content,
                    title=title,
                    title_height_correction=title_height_correction,
                    title_color=title_color,
                    resample=resample
                )), ensure_ascii=False)
            case _: ...
        task_status = True
    # 业务逻辑结束
    except Exception as e:
        logger.error(e)
        callback_data = str()
    if task_status:
        update_status(taskId=taskid, content=f'完成任务，耗时 {float(time.time() - st_time): .3f} 秒',
                      status=callbackstatus, callback_url=callbackurl, callback_data=callback_data)
        _client.xack(stream_name, normal_group_name, message_id)
    else:
        update_status(taskId=taskid, content=f"任务失败", status=failedStatus, callback_url=callbackurl,
                      callback_data=callback_data)


def process_task(normal_group_name, normal_consumer_name, normal_stream_name, auto_group_name, auto_consumer_name,
                 auto_stream_name, _client, environment):
    while True:
        rec_json = {'taskid': str()}
        try:
            if not check_cpu_usage():
                logger.debug("cpu使用率当前大于95%，等待cpu释放")
                continue
            stream_name = auto_stream_name

            messages = _client.xreadgroup(auto_group_name, auto_consumer_name, {stream_name: '>'}, count=1,
                                          block=1000)
            queue_tag = "优先"
            if not messages:
                stream_name = normal_stream_name
                messages = _client.xreadgroup(normal_group_name, normal_consumer_name, {stream_name: '>'},
                                              count=1, block=1000)
                queue_tag = "普通"
            if messages:
                for message in messages:
                    THREAD_POOL.submit(handle_msg, {
                        'message': message,
                        'queue_tag': queue_tag,
                        'env': environment,
                        'client': _client,
                        'stream_name': stream_name,
                        'normal_group_name': normal_group_name
                    })
        except Exception as e:
            update_status(taskId=rec_json['taskid'], content=f"出现了非预期的错误！: {e}", status=failedStatus,
                          callback_url=rec_json['callbackurl'])
            logger.error(f"出现了非预期的错误！: {e}")
            continue


def main():
    logger.info("服务开始运行，监听redis服务。。。")
    environment = os.environ.get('OS_ENV')
    if environment is None:
        environment = 'dev'
    if environment == 'prod':
        client = redis.Redis(host='10.10.10.135', port=16379, db=0)
        logger.debug("服务运行在生产环境.")
    else:
        client = redis.Redis(host='192.168.100.189', port=30652, db=0)
        logger.debug("服务运行在测试环境.")
    normal_stream_name = f'UniversalTransparent_{REDIS_TASK_TYPE}'
    auto_stream_name = f'UniversalTransparent_{REDIS_TASK_TYPE}:High'
    normal_group_name = 'task_workers'
    auto_group_name = 'task_workers'
    normal_consumer_name = f'worker_{uuid.uuid1()}'
    auto_consumer_name = f'worker_{uuid.uuid1()}'
    try:
        client.xgroup_create(normal_stream_name, normal_group_name, '$', mkstream=True)
    except redis.exceptions.ResponseError:
        pass  # 已存在
    try:
        client.xgroup_create(auto_stream_name, auto_group_name, '$', mkstream=True)
    except redis.exceptions.ResponseError:
        pass  # 已存在
    process_task(normal_group_name, normal_consumer_name, normal_stream_name, auto_group_name, auto_consumer_name,
                 auto_stream_name, client, environment)


if __name__ == "__main__":
    main()
    THREAD_POOL.shutdown()
