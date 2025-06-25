import os
import sys
import platform
import requests
import tarfile
import zipfile
from pathlib import Path

class BinaryDownloader:
    def __init__(self):
        self.system = platform.system().lower()
        project_root = Path(__file__).resolve().parent.parent
        self.middleware_dir = project_root / "middleware"
        self.temp_dir = project_root / "temp"
        
        # 创建临时目录
        self.temp_dir.mkdir(exist_ok=True)
        
    def download_file(self, url: str, filename: str) -> Path:
        """下载文件到临时目录"""
        temp_file = self.temp_dir / filename
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(temp_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return temp_file
    
    def extract_file(self, file_path: Path, extract_dir: Path):
        """解压文件"""
        if file_path.suffix == '.zip':
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        elif file_path.suffix in ['.tar', '.gz']:
            with tarfile.open(file_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_dir)
    
    def download_redis(self):
        """下载Redis"""
        redis_dir = self.middleware_dir / "redis"
        redis_dir.mkdir(exist_ok=True)
        
        if self.system == "windows":
            url = "https://github.com/microsoftarchive/redis/releases/download/win-3.2.100/Redis-x64-3.2.100.zip"
            filename = "redis-windows.zip"
        else:
            url = "https://download.redis.io/releases/redis-6.2.6.tar.gz"
            filename = "redis-linux.tar.gz"
        
        print(f"Downloading Redis for {self.system}...")
        file_path = self.download_file(url, filename)
        self.extract_file(file_path, redis_dir)
    
    def download_mysql(self):
        """下载MySQL"""
        mysql_dir = self.middleware_dir / "mysql"
        mysql_dir.mkdir(exist_ok=True)
        
        if self.system == "windows":
            url = "https://dev.mysql.com/get/Downloads/MySQL-8.0/mysql-8.0.26-winx64.zip"
            filename = "mysql-windows.zip"
        else:
            url = "https://dev.mysql.com/get/Downloads/MySQL-8.0/mysql-8.0.26-linux-glibc2.12-x86_64.tar.xz"
            filename = "mysql-linux.tar.xz"
        
        print(f"Downloading MySQL for {self.system}...")
        file_path = self.download_file(url, filename)
        self.extract_file(file_path, mysql_dir)
    
    def download_elasticsearch(self):
        """下载Elasticsearch"""
        es_dir = self.middleware_dir / "elasticsearch"
        es_dir.mkdir(exist_ok=True)
        
        url = "https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.14.0-{}.tar.gz"
        if self.system == "windows":
            url = url.format("windows-x86_64")
            filename = "elasticsearch-windows.tar.gz"
        else:
            url = url.format("linux-x86_64")
            filename = "elasticsearch-linux.tar.gz"
        
        print(f"Downloading Elasticsearch for {self.system}...")
        file_path = self.download_file(url, filename)
        self.extract_file(file_path, es_dir)
    
    def download_minio(self):
        """下载MinIO"""
        minio_dir = self.middleware_dir / "minio"
        minio_dir.mkdir(exist_ok=True)
        
        if self.system == "windows":
            url = "https://dl.min.io/server/minio/release/windows-amd64/minio.exe"
            filename = "minio.exe"
        else:
            url = "https://dl.min.io/server/minio/release/linux-amd64/minio"
            filename = "minio"
        
        print(f"Downloading MinIO for {self.system}...")
        file_path = self.download_file(url, filename)
        target_path = minio_dir / filename
        file_path.rename(target_path)
        
        # 设置执行权限（仅限Unix系统）
        if self.system != "windows":
            os.chmod(target_path, 0o755)
    
    def cleanup(self):
        """清理临时文件"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

def main():
    downloader = BinaryDownloader()
    try:
        downloader.download_redis()
        downloader.download_mysql()
        downloader.download_elasticsearch()
        downloader.download_minio()
        print("\nAll middleware binaries downloaded successfully!")
    except Exception as e:
        print(f"Error downloading binaries: {e}")
    finally:
        downloader.cleanup()

if __name__ == "__main__":
    main()