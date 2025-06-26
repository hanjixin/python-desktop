import os
import sys
import platform
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from installer.download_binaries import BinaryDownloader


def create_directories():
    """创建必要的数据和配置目录"""
    directories = [
        "data/redis",
        "data/mysql",
        "data/es",
        "data/minio",
        "config",
        "config/redis",
        "middleware/redis",
        "middleware/mysql",
        "middleware/elasticsearch",
        "middleware/minio",
    ]

    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")


def check_middleware_files():
    """检查中间件文件是否存在"""
    system = platform.system().lower()
    redis_server = "redis-server.exe" if system == "windows" else "redis-server"
    mysqld = "mysqld.exe" if system == "windows" else "mysqld"

    required_files = [
        *([f'middleware/redis/{redis_server}'] if system != 'darwin' else []),
        'config/redis/redis.conf',
        f"middleware/mysql/bin/{mysqld}",
        "middleware/mysql/my.ini",
        "middleware/elasticsearch/config/elasticsearch.yml",
        (
            "middleware/minio/minio.exe"
            if system == "windows"
            else "middleware/minio/minio"
        ),
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    return missing_files


def download_binaries(missing_files):
    """下载所需的中间件二进制文件"""
    print("\nDownloading middleware binaries...")
    downloader = BinaryDownloader()
    try:
        if any("redis" in file for file in missing_files):
            downloader.download_redis()
        if any("mysql" in file for file in missing_files):
            downloader.download_mysql()
        if any("elasticsearch" in file for file in missing_files):
            downloader.download_elasticsearch()
        if any("minio" in file for file in missing_files):
            downloader.download_minio()
        print("Middleware binaries downloaded successfully!")
    except Exception as e:
        print(f"Error downloading binaries: {e}")
        sys.exit(1)
    finally:
        downloader.cleanup()


def setup_configurations():
    """设置中间件配置文件"""
    # Redis配置
    redis_conf = Path('config/redis/redis.conf')
    if not redis_conf.exists():
        with open(redis_conf, "w") as f:
            f.write(
                """
port 6379
dir ./data/redis
save 900 1
save 300 10
save 60 10000
daemonize no
protected-mode yes
"""
            )

    # MySQL配置
    mysql_conf = Path("middleware/mysql/my.ini")
    if not mysql_conf.exists():
        with open(mysql_conf, "w") as f:
            f.write(
                """
[mysqld]
port=3306
datadir=./data/mysql
socket=./data/mysql/mysql.sock
skip-grant-tables
default_authentication_plugin=mysql_native_password
"""
            )


def main():
    print("Starting post-installation configuration...\n")

    # 创建目录
    create_directories()

    # 检查文件
    missing_files = check_middleware_files()
    if missing_files:
        print("\nMissing required files:")
        for file in missing_files:
            print(f"- {file}")
        print("\nDownloading missing files...")
        download_binaries(missing_files)

    # 设置配置
    setup_configurations()

    print("\nPost-installation configuration completed successfully!")
    print("\nYou can now run the application using: python main.py")


if __name__ == "__main__":
    main()
