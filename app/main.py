from fastapi import FastAPI
import redis
import json
from app.core.config import settings

app = FastAPI(title="Zabbix PyManager")

# Conexion al redis
r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

@app.get("/")
def home():
    return {"message": "Zabbix Manager API Online"}
# test worker - os successsss :D
@app.post("/sysadmin/test-os-access")
def test_os_access():
    payload = {
        "action": "check_system"
    }
    r.lpush("infra_tasks", json.dumps(payload))
    return {"message": "Test de acceso al OS enviado al Worker"}