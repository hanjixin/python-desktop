from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from .middleware_manager import MiddlewareManager

app = FastAPI(title="Python Desktop Middleware API")
manager = MiddlewareManager()

class ServiceStatus(BaseModel):
    status: Dict[str, bool]

class ServiceResponse(BaseModel):
    message: str
    service: str
    status: bool

@app.get("/status", response_model=ServiceStatus)
async def get_status():
    """获取所有中间件服务的状态"""
    status = manager.check_status()
    return {"status": status}

@app.post("/start/{service}", response_model=ServiceResponse)
async def start_service(service: str):
    """启动指定的中间件服务"""
    try:
        if service == "redis":
            manager.redis.start()
        elif service == "mysql":
            manager.mysql.initialize()
            manager.mysql.start()
            manager.mysql.create_app_db()
        elif service == "elasticsearch":
            manager.es.start()
        elif service == "minio":
            manager.minio.start()
        else:
            raise HTTPException(status_code=404, detail=f"Service {service} not found")
        
        return {
            "message": f"Service {service} started successfully",
            "service": service,
            "status": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stop/{service}", response_model=ServiceResponse)
async def stop_service(service: str):
    """停止指定的中间件服务"""
    try:
        if service == "redis":
            manager.redis.stop()
        elif service == "mysql":
            manager.mysql.stop()
        elif service == "elasticsearch":
            manager.es.stop()
        elif service == "minio":
            manager.minio.stop()
        else:
            raise HTTPException(status_code=404, detail=f"Service {service} not found")
        
        return {
            "message": f"Service {service} stopped successfully",
            "service": service,
            "status": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/restart/{service}", response_model=ServiceResponse)
async def restart_service(service: str):
    """重启指定的中间件服务"""
    try:
        await stop_service(service)
        return await start_service(service)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/start", response_model=ServiceStatus)
async def start_all():
    """启动所有中间件服务"""
    try:
        manager.start_all()
        return {"status": manager.check_status()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stop", response_model=ServiceStatus)
async def stop_all():
    """停止所有中间件服务"""
    try:
        manager.stop_all()
        return {"status": manager.check_status()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))