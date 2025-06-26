import os
import sys
import platform
import requests
import tarfile
import zipfile
from pathlib import Path
import shutil
import subprocess

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
        elif self.system == "darwin": # macOS
            # For macOS, Redis is expected to be installed via Homebrew, so we don't download it.
            # This part of the code should ideally not be reached if post_install.py handles macOS correctly.
            return
        else:
            url = "https://download.redis.io/releases/redis-6.2.6.tar.gz"
            filename = "redis-linux.tar.gz"
        
        print(f"Downloading Redis for {self.system}...")
        file_path = self.download_file(url, filename)
        
        # Create a temporary extraction directory
        extract_temp_dir = self.temp_dir / "redis_extract"
        extract_temp_dir.mkdir(exist_ok=True)
        
        self.extract_file(file_path, extract_temp_dir)

        # Find the actual extracted directory (e.g., redis-6.2.6)
        extracted_content_dir = None
        for item in extract_temp_dir.iterdir():
            if item.is_dir() and "redis" in item.name:
                extracted_content_dir = item
                break

        if extracted_content_dir:
            if self.system == "linux":
                print(f"Compiling Redis in {extracted_content_dir}...")
                try:
                    subprocess.run(["make"], cwd=extracted_content_dir, check=True)
                    redis_server_path = extracted_content_dir / "src" / "redis-server"
                    if redis_server_path.exists():
                        shutil.move(str(redis_server_path), str(redis_dir / "redis-server"))
                        print(f"Moved compiled redis-server to {redis_dir}")
                    else:
                        print("Could not find compiled redis-server in extracted directory.")
                except subprocess.CalledProcessError as e:
                    print(f"Error compiling Redis: {e}")
                    raise
            elif self.system == "windows":
                # For Windows, the downloaded zip contains pre-built binaries
                redis_server_path = extracted_content_dir / "redis-server.exe"
                if not redis_server_path.exists():
                    # Fallback for cases where redis-server.exe might be in a subdirectory
                    # This might need adjustment based on the actual zip structure
                    for root, dirs, files in os.walk(extracted_content_dir):
                        if "redis-server.exe" in files:
                            redis_server_path = Path(root) / "redis-server.exe"
                            break

                if redis_server_path.exists():
                    shutil.move(str(redis_server_path), str(redis_dir / "redis-server.exe"))
                    print(f"Moved redis-server.exe to {redis_dir}")
                else:
                    print("Could not find redis-server.exe in extracted directory.")
            else:
                print("Unsupported system for Redis binary handling.")
        else:
            print("Could not find extracted Redis content directory.")
        
        # Clean up temporary extraction directory
        shutil.rmtree(extract_temp_dir)
    
    def download_mysql(self):
        """下载MySQL"""
        mysql_dir = self.middleware_dir / "mysql"
        mysql_dir.mkdir(exist_ok=True)
        
        if self.system == "windows":
            url = "https://dev.mysql.com/get/Downloads/MySQL-8.0/mysql-8.0.26-winx64.zip"
            filename = "mysql-windows.zip"
        elif self.system == "darwin": # macOS
            # Using MySQL 8.0.42 for macOS (x86_64) Compressed TAR Archive
            url = "https://dev.mysql.com/get/Downloads/MySQL-8.0/mysql-8.0.42-macos15-x86_64.tar.gz"
            filename = "mysql-macos.tar.gz"
        else: # linux
            url = "https://dev.mysql.com/get/Downloads/MySQL-8.0/mysql-8.0.26-linux-glibc2.12-x86_64.tar.xz"
            filename = "mysql-linux.tar.xz"
        
        print(f"Downloading MySQL for {self.system}...")
        file_path = self.download_file(url, filename)
        
        # Create a temporary extraction directory
        extract_temp_dir = self.temp_dir / "mysql_extract"
        extract_temp_dir.mkdir(exist_ok=True)
        
        self.extract_file(file_path, extract_temp_dir)
        
        # Find the actual extracted directory (e.g., mysql-8.0.42-macos15-x86_64)
        extracted_content_dir = None
        for item in extract_temp_dir.iterdir():
            if item.is_dir() and "mysql" in item.name:
                extracted_content_dir = item
                break
        
        if extracted_content_dir:
            # Move bin and lib directories to mysql_dir
            # Ensure mysql_dir/bin and mysql_dir/lib exist
            (mysql_dir / "bin").mkdir(exist_ok=True)
            (mysql_dir / "lib").mkdir(exist_ok=True)

            # Move contents of extracted_content_dir/bin to mysql_dir/bin
            for item in (extracted_content_dir / "bin").iterdir():
                shutil.move(str(item), str(mysql_dir / "bin" / item.name))
            
            # Move contents of extracted_content_dir/lib to mysql_dir/lib
            for item in (extracted_content_dir / "lib").iterdir():
                shutil.move(str(item), str(mysql_dir / "lib" / item.name))
            
            print(f"Moved MySQL binaries to {mysql_dir}")
        else:
            print("Could not find extracted MySQL content directory.")
        
        # Clean up temporary extraction directory
        shutil.rmtree(extract_temp_dir)
    
    def download_elasticsearch(self):
        """下载Elasticsearch"""
        es_dir = self.middleware_dir / "elasticsearch"
        es_dir.mkdir(exist_ok=True)
        
        if self.system == "windows":
            url = "https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.14.0-windows-x86_64.zip"
            filename = "elasticsearch-windows.zip"
        elif self.system == "darwin": # macOS
            url = "https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.14.0-darwin-x86_64.tar.gz"
            filename = "elasticsearch-darwin.tar.gz"
        else: # linux
            url = "https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.14.0-linux-x86_64.tar.gz"
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