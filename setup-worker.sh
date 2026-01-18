#!/bin/bash

# Zabbix-PyManager setup script :)
#Worker service setup

echo "--- STARTING ZBX_WORKER SETUP ---"

# si no hay un datos del usuario zbx-worker entonces lo creo
if ! id "zbx-worker" &>/dev/null; then
    echo "[INFO] Creating system user: zbx-worker"
    sudo adduser --system --group --no-create-home zbx-worker
else
    echo "[INFO] User zbx-worker already exists. Skipping."
fi

# manejo de sudoers
# se utiliza la configuracion de sudoers.d de manera aislada, para mayor escalabilidad y limpieza en el servidor.
echo "[INFO] Configuring sudoers permissions"
SUDOERS_FILE="/etc/sudoers.d/zbx-manager"
SUDOERS_LINE="zbx-worker ALL=(ALL) NOPASSWD: /usr/bin/apt-get update, /usr/bin/apt-get install -y *, /usr/bin/dpkg -i *, /usr/bin/systemctl *, /usr/bin/wget *"

echo "$SUDOERS_LINE" | sudo tee $SUDOERS_FILE > /dev/null
sudo chmod 440 $SUDOERS_FILE

# configuracion de systemd .service
echo "[INFO] Configuring systemd unit: zbx-worker.service"
SERVICE_FILE="/etc/systemd/system/zbx-worker.service"
WORKING_DIR=$(pwd)
VENV_PYTHON="$WORKING_DIR/venv/bin/python"

# Verification of Virtual Environment
if [ ! -f "$VENV_PYTHON" ]; then
    echo "[ERROR] Virtual environment python not found at $VENV_PYTHON"
    exit 1
fi

sudo bash -c "cat > $SERVICE_FILE" <<EOF  # coloco la descripcion del servicio
[Unit]
Description=Zabbix PyManager Worker Service
After=network.target redis-server.service

[Service]
User=zbx-worker
Group=zbx-worker
WorkingDirectory=$WORKING_DIR
ExecStart=$VENV_PYTHON worker/agent.py
Restart=always
StandardOutput=append:/var/log/zbx-worker.log
StandardError=append:/var/log/zbx-worker-error.log

[Install]
WantedBy=multi-user.target
EOF

# permisos de directorio
echo "[INFO] Adjusting directory ownership and permissions"
sudo chgrp -R zbx-worker $WORKING_DIR
sudo chmod -R 750 $WORKING_DIR
echo "[INFO] Creating log files"
sudo touch /var/log/zbx-worker.log /var/log/zbx-worker-error.log
sudo chown zbx-worker:zbx-worker /var/log/zbx-worker.log /var/log/zbx-worker-error.log

# activando service
echo "[INFO] Reloading systemd daemon and restarting service"
sudo systemctl daemon-reload
sudo systemctl enable zbx-worker
sudo systemctl restart zbx-worker

echo "--- SETUP COMPLETED SUCCESSFULLY ---"