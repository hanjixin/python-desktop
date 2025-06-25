import os
import sys
import shutil
import platform
from pathlib import Path

def clean_dist():
    """清理dist目录"""
    dist_dir = Path("../dist")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()

def copy_middleware_files():
    """复制中间件文件到构建目录"""
    src_dir = Path("../middleware")
    dist_dir = Path("../dist/middleware")
    
    # 复制中间件文件
    shutil.copytree(src_dir, dist_dir)

def copy_config_files():
    """复制配置文件到构建目录"""
    src_dir = Path("../config")
    dist_dir = Path("../dist/config")
    
    if src_dir.exists():
        shutil.copytree(src_dir, dist_dir)

def build_executable():
    """使用PyInstaller构建可执行文件"""
    os.system(f"pyinstaller ../installer/build_config.spec")

def create_data_dirs():
    """创建数据目录"""
    data_dirs = [
        "data/redis",
        "data/mysql",
        "data/es",
        "data/minio"
    ]
    
    for dir_path in data_dirs:
        Path(f"../dist/{dir_path}").mkdir(parents=True, exist_ok=True)

def copy_post_install():
    """复制post_install脚本到dist目录"""
    shutil.copy("../post_install.py", "../dist/")

def main():
    print("Starting build process...\n")
    
    # 清理dist目录
    print("Cleaning dist directory...")
    clean_dist()
    
    # 复制文件
    print("Copying middleware files...")
    copy_middleware_files()
    
    print("Copying configuration files...")
    copy_config_files()
    
    # 创建数据目录
    print("Creating data directories...")
    create_data_dirs()
    
    # 构建可执行文件
    print("Building executable...")
    build_executable()
    
    # 复制post_install脚本
    print("Copying post-installation script...")
    copy_post_install()
    
    print("\nBuild completed successfully!")
    print("\nThe application has been built in the 'dist' directory.")
    print("Run 'python post_install.py' after deployment to complete the setup.")

if __name__ == "__main__":
    main()