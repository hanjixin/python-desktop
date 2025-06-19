
## 一、整体架构设计

```
Python_Desktop/
├── installer/            # 安装脚本
├── dist/                 # 打包输出目录
├── src/                  # 源码目录
├── requirements.txt      # 依赖列表
└── post_install.py       # 安装后配置脚本
├── middleware/
│   ├── redis/            # Redis 嵌入式
│   ├── mysql/            # MySQL 嵌入式
│   ├── elasticsearch/    # ES 嵌入式
│   └── minio/            # MinIO 嵌入式
├── data/                 # 所有中间件数据目录
│   ├── redis/
│   ├── mysql/
│   ├── es/
│   └── minio/
└── config/               # 配置文件
```

## 二、Redis 嵌入式方案

### 1. 使用 Redis 官方 Windows 版本或编译版本

```bash
# 项目结构
middleware/redis/
├── redis-server.exe      # Windows
├── redis-server          # Linux/Mac
└── redis.conf
```

### 2. Redis 启动管理类

```python
import subprocess
import psutil
from pathlib import Path

class EmbeddedRedis:
    def __init__(self):
        self.redis_path = Path("./middleware/redis/redis-server")
        self.config_path = Path("./middleware/redis/redis.conf")
        self.data_dir = Path("./data/redis")
        self.port = 6379
        
    def start(self):
        if not self._is_running():
            cmd = f"{self.redis_path} {self.config_path} --dir {self.data_dir} --port {self.port}"
            self.process = subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL)
            
    def _is_running(self):
        for proc in psutil.process_iter(['name']):
            if 'redis-server' in proc.info['name']:
                return True
        return False
    
    def stop(self):
        if hasattr(self, 'process'):
            self.process.terminate()
```

### 3. Redis 配置文件示例 (redis.conf)

```
port 6379
dir ./data/redis
save 900 1
save 300 10
save 60 10000
daemonize no
protected-mode yes
```

## 三、MySQL 嵌入式方案

### 1. 使用 MariaDB 嵌入式或 MySQL Community Server 精简版

```bash
middleware/mysql/
├── bin/
│   ├── mysqld.exe        # Windows
│   └── mysql             # CLI工具
├── data/                 # 初始空数据库
└── my.ini                # 配置文件
```

### 2. MySQL 启动管理类

```python
import subprocess
import time
import mysql.connector
from pathlib import Path

class EmbeddedMySQL:
    def __init__(self):
        self.mysql_path = Path("./middleware/mysql/bin/mysqld")
        self.data_dir = Path("./data/mysql")
        self.port = 3306
        self.root_pass = "ragflow@123"
        
    def initialize(self):
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True)
            init_cmd = f"{self.mysql_path} --initialize-insecure --datadir={self.data_dir}"
            subprocess.run(init_cmd.split(), check=True)
    
    def start(self):
        if not self._is_running():
            cmd = f"{self.mysql_path} --datadir={self.data_dir} --port={self.port}"
            self.process = subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL)
            time.sleep(5)  # 等待启动
            
    def _is_running(self):
        try:
            conn = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                passwd=self.root_pass,
                port=self.port
            )
            conn.close()
            return True
        except:
            return False
    
    def create_app_db(self):
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            passwd=self.root_pass,
            port=self.port
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ragflow")
        cursor.close()
        conn.close()
```

### 3. MySQL 配置文件示例 (my.ini)

```
[mysqld]
port=3306
datadir=./data/mysql
socket=./data/mysql/mysql.sock
skip-grant-tables
default_authentication_plugin=mysql_native_password
```

## 四、统一中间件管理器

```python
class MiddlewareManager:
    def __init__(self):
        self.redis = EmbeddedRedis()
        self.mysql = EmbeddedMySQL()
        self.es = EmbeddedElasticsearch()
        self.minio = EmbeddedMinIO()
        
    def start_all(self):
        print("Starting middleware services...")
        self.redis.start()
        self.mysql.initialize()
        self.mysql.start()
        self.mysql.create_app_db()
        self.es.start()
        self.minio.start()
        
    def stop_all(self):
        print("Stopping middleware services...")
        self.redis.stop()
        self.mysql.stop()
        self.es.stop()
        self.minio.stop()
        
    def check_status(self):
        return {
            "redis": self.redis._is_running(),
            "mysql": self.mysql._is_running(),
            "elasticsearch": self.es._is_running(),
            "minio": self.minio._is_running()
        }
```

## 五、PyInstaller 打包配置

```bash
pyinstaller --onefile \
--add-data "middleware/redis/*;middleware/redis" \
--add-data "middleware/mysql/*;middleware/mysql" \
--add-data "middleware/elasticsearch/*;middleware/elasticsearch" \
--add-data "middleware/minio/*;middleware/minio" \
--add-data "config/*;config" \
--hidden-import redis \
--hidden-import mysql.connector \
--hidden-import elasticsearch \
--hidden-import minio \
--icon=app.ico \
main.py
```

## 六、安装程序增强 (NSIS 示例)

```
; 安装时初始化数据目录
Section "Create Data Dirs"
  CreateDirectory "$INSTDIR\data\redis"
  CreateDirectory "$INSTDIR\data\mysql"
  CreateDirectory "$INSTDIR\data\es"
  CreateDirectory "$INSTDIR\data\minio"
SectionEnd

; 安装后启动服务
Section "Start Services"
  ExecWait '"$INSTDIR\main.exe" --init-services'
SectionEnd
```

## 七、资源清理策略

```python
import atexit
import signal

def cleanup():
    manager = MiddlewareManager()
    manager.stop_all()

atexit.register(cleanup)
signal.signal(signal.SIGTERM, lambda signum, frame: cleanup())
```

## 八、跨平台兼容方案

### 1. 平台检测与路径处理

```python
def get_platform_config():
    import platform
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    config = {
        "redis": {
            "executable": f"middleware/redis/{system}/{arch}/redis-server",
            "config": "middleware/redis/redis.conf"
        },
        "mysql": {
            "executable": f"middleware/mysql/{system}/{arch}/bin/mysqld",
            "config": f"middleware/mysql/{system}/my.cnf"
        }
    }
    return config
```

### 2. 首次运行初始化

```python
def first_run_setup():
    # 检查是否首次运行
    if not Path("./.initialized").exists():
        # 初始化所有中间件
        manager = MiddlewareManager()
        manager.start_all()
        
        # 创建标记文件
        with open("./.initialized", "w") as f:
            f.write("initialized")
```

## 九、用户界面集成

### 1. 服务状态监控界面

```python
import tkinter as tk
from tkinter import ttk

class ServiceMonitor(tk.Toplevel):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.title("Middleware Services Monitor")
        
        ttk.Label(self, text="Service Status").pack()
        
        self.status_vars = {
            "redis": tk.StringVar(value="Checking..."),
            "mysql": tk.StringVar(value="Checking..."),
            "elasticsearch": tk.StringVar(value="Checking..."),
            "minio": tk.StringVar(value="Checking...")
        }
        
        for name in self.status_vars:
            ttk.Label(self, text=name.capitalize()).pack()
            ttk.Label(self, textvariable=self.status_vars[name]).pack()
        
        self.update_status()
    
    def update_status(self):
        status = self.manager.check_status()
        for name, var in self.status_vars.items():
            var.set("Running" if status[name] else "Stopped")
        self.after(5000, self.update_status)
```

## 十、最佳实践建议

1. **资源限制配置**：
   - Redis: 在配置中设置 `maxmemory 256mb`
   - MySQL: 设置 `innodb_buffer_pool_size=128M`
   - Elasticsearch: 设置 `ES_JAVA_OPTS="-Xms256m -Xmx256m"`

2. **安全加固**：
   ```python
   # 生成随机密码
   import secrets
   def generate_secure_password():
       return secrets.token_urlsafe(16)
   ```

3. **日志管理**：
   ```python
   def setup_logging():
       logging.basicConfig(
           filename='./logs/middleware.log',
           level=logging.INFO,
           format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
       )
   ```

4. **性能优化**：
   - 为嵌入式MySQL禁用不需要的存储引擎
   - 为Redis配置适当的保存策略

5. **用户数据备份**：
   ```python
   def backup_user_data():
       import zipfile
       with zipfile.ZipFile('user_data_backup.zip', 'w') as zipf:
           for folder in ['data/redis', 'data/mysql']:
               for root, dirs, files in os.walk(folder):
                   for file in files:
                       zipf.write(os.path.join(root, file))
   ```

通过以上方案，你可以将Redis和MySQL与其他中间件一起完整打包，为用户提供真正的一键安装体验。所有服务将在应用启动时自动初始化，并在退出时正确清理。