import redis
import json
import time

# Conexión al Redis
try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    print("Worker conectado a Redis")
except Exception as e:
    print(f"Error conectarme a Redis: {e}")
    exit(1)

while True:
    # Bloqueado hasta que me llegue una tarea a la cola
    task = r.brpop("infra_tasks", timeout=0)
    if task:
        queue_name, data = task
        payload = json.loads(data)
        print(f"Tarea: {payload['action']} para {payload['service']}")