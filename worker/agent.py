import redis
import json
import subprocess
import os
import sys

# Conexión a Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def execute_sys_task(command_list):
    """Ejecuta un comando y vuelca la salida al log en tiempo real"""
    try:
        # Popen permite capturar la salida mientras el proceso corre
        process = subprocess.Popen(
            command_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Unificamos error y salida normal
            text=True,
            bufsize=1  # Buffer por línea
        )

        # Leemos cada línea que el comando (ej. apt-get) escupe
        for line in process.stdout:
            sys.stdout.write(f"  [EXEC] {line}")
            sys.stdout.flush()

        process.wait()
        
        if process.returncode == 0:
            return True, "Comando completado exitosamente"
        else:
            return False, f"Código de salida error: {process.returncode}"
            
    except Exception as e:
        return False, str(e)

def install_zabbix_packages():
    print("Iniciando instalación de paquetes Zabbix 7.0...")
    
    commands = [
        ["wget", "https://repo.zabbix.com/zabbix/7.0/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest+ubuntu24.04_all.deb", "-O", "/tmp/zabbix-repo.deb"],
        ["sudo", "dpkg", "-i", "--force-confnew", "/tmp/zabbix-repo.deb"],
        ["sudo", "apt-get", "update"],  
        # Paquetes 
        ["sudo", "apt-get", "install", "-y", "-o", "Dpkg::Options::=--force-confdef", "-o", "Dpkg::Options::=--force-confold", "zabbix-server-mysql", "zabbix-frontend-php", "zabbix-apache-conf", "zabbix-sql-scripts", "zabbix-agent"]
    ]
    
    for cmd in commands:
        print(f"exec: {' '.join(cmd)}")
        success, output = execute_sys_task(cmd)
        if not success:
            return False, output
    return True, "Todos los paquetes instalados correctamente"

# 
print("Worker iniciado y escuchando")
try:
    while True:
        task = r.brpop("infra_tasks", timeout=0)
        if task:
            _, data = task
            payload = json.loads(data)
            action = payload.get("action")
            
            print(f"Procesando: {action}")

            if action == "check_system":
                success, _ = execute_sys_task(["sudo", "apt-get", "update"])
                if success:
                    execute_sys_task(["sudo", "systemctl", "status", "cron"])
            
            elif action == "install_zabbix":
                success, message = install_zabbix_packages()
                print(f"Res: {message}")

            else:
                print(f"Acción desconocida: {action}")
            
            # Flush 
            sys.stdout.flush()

except KeyboardInterrupt:
    print("\nDeteniendo Worker...")