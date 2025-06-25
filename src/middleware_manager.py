import subprocess
import psutil
import time
import mysql.connector
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

class EmbeddedElasticsearch:
    def __init__(self):
        # ES配置待实现
        pass

    def start(self):
        # ES启动逻辑待实现
        pass

    def stop(self):
        # ES停止逻辑待实现
        pass

    def _is_running(self):
        # ES状态检查待实现
        return False

class EmbeddedMinIO:
    def __init__(self):
        # MinIO配置待实现
        pass

    def start(self):
        # MinIO启动逻辑待实现
        pass

    def stop(self):
        # MinIO停止逻辑待实现
        pass

    def _is_running(self):
        # MinIO状态检查待实现
        return False

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