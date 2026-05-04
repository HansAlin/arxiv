
## Running the Scripts Automatically on Reboot (systemd)

1. Make your script executable if you are using bash script

```bash
chmod +x /home/pi/Projects/My_project/start_sessions.sh
```

2. Create systemd user service folder if it doesn't exist.

```bash
mkdir -p ~/.config/systemd/user
```

3. Create the service file

```bash
nano ~/.config/systemd/user/mysystem_service.service
```

Paste this inside:

```ini
[Unit]
Description=Start my script
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/pi/Projects/arxiv
ExecStart=/home/pi/Projects/My_project/start_sessions.sh
Restart=on-failure
Environment=PATH=/usr/local/bin:/usr/bin:/bin
Environment=VIRTUAL_ENV=/home/pi/Projects/My_project/env
Environment=HOME=/home/pi
StandardOutput=journal
StandardError=journal
SyslogIdentifier=energy-scripts
LogLevelMax=info

[Install]
WantedBy=default.target
```

4. Reload systemd and enable the service

```bash
systemctl --user daemon-reload
systemctl --user enable mysystem_service.service
systemctl --user start mysystem_service.service
systemctl --user status mysystem_service.service
```

5. Enable lingering (optional, allows service to run without login)

```bash
sudo loginctl enable-linger pi
```

6. Reboot to test

```bash
sudo reboot
```


## Viewing Logs

Tail a single script log in real-time

```bash
tail -f ~/Projects/Wallbox/logs/main.log
tail -f ~/Projects/Wallbox/logs/server.log
tail -f ~/Projects/Wallbox/logs/energy_display.log
tail -f ~/Projects/Wallbox/logs/energy_main.log
tail -f ~/Projects/Wallbox/logs/startup.log
```