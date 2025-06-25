import uvicorn
from src.api import app
from src.middleware_manager import MiddlewareManager

def main():
    # 创建中间件管理器实例并启动所有服务
    manager = MiddlewareManager()
    try:
        manager.start_all()
        print("\nMiddleware Services Status:")
        status = manager.check_status()
        for service, running in status.items():
            print(f"{service}: {'Running' if running else 'Stopped'}")
            
        # 启动FastAPI服务
        print("\nStarting FastAPI server...")
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info"
        )
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # 停止所有服务
        manager.stop_all()

if __name__ == "__main__":
    main()