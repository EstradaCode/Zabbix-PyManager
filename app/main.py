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

@app.post("/sysadmin/restart-server")
def restart_server():
    # tarea default
    payload = {
        "action": "restart_zabbix",
        "service": "zabbix-server"
    }
    # meto la tarea en la cola
    r.lpush("infra_tasks", json.dumps(payload))
    return {"status": "success", "detail": "Orden enviada al Worker nativo"}
#prueba de cola completada