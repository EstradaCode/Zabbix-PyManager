
import redis
import json
import subprocess
import os

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def execute_sys_task(command_list):
    """Ejecuta un comando de sistema y retorna la salida"""
    try:
        result = subprocess.run(
            command_list, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

try:
    while True:
        task = r.brpop("infra_tasks", timeout=0)
        if task:
            _, data = task
            payload = json.loads(data)
            action = payload.get("action")
            
            print(f"🛠️ Procesando acción: {action}")

            if action == "check_system":
                print("🔄 Ejecutando 'apt-get update'...")
                success, output = execute_sys_task(["sudo", "apt-get", "update"])
                
                if success:
                    _, status = execute_sys_task(["sudo", "systemctl", "status", "cron"])
                    print(f"Res:\n{status[:200]}...") 
                else:
                    print(f"Falló la tarea: {output}")

except KeyboardInterrupt:
    print("\n Deteniendo Worker...")