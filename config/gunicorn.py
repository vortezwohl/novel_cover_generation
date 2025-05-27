# 监听内网端口
bind = "0.0.0.0:80"

# 工作目录
chdir = "./"

# 并行工作进程数
workers = 1

# 指定每个工作者的线程数
threads = 16

# 监听队列
backlog = 1024

# 超时时间
timeout = 3600

# 设置守护进程,将进程交给 supervisor 管理；如果设置为 True 时，supervisor 启动日志为：
# gave up: fastapi_server entered FATAL state, too many start retries too quickly
# 则需要将此改为: False
daemon = True

# 工作模式协程
worker_class = "uvicorn.workers.UvicornWorker"

# 设置最大并发量
worker_connections = 2048

# 设置进程文件目录
pidfile = "./gunicorn.pid"
