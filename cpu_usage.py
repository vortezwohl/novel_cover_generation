import psutil


def check_cpu_usage():
    """
    获取CPU占用率
    :return: 占用率是否超过 80%
    """
    cpu_usage = psutil.cpu_percent(interval=1)  # 计算1秒钟内的CPU占用率
    cpu_usage_float = cpu_usage
    if cpu_usage_float >= 95:
        return False
    else:
        return True
