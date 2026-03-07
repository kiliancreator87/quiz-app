#!/bin/bash

echo "=== Raspberry Pi Video Player Setup ==="
echo ""

# Prüfen ob als root
if [ "$EUID" -ne 0 ]; then 
    echo "Bitte als root ausführen: sudo ./setup-pi-player.sh"
    exit 1
fi

# Pakete installieren
echo "Installiere Pakete..."
apt-get update
apt-get install -y python3-pip mpv

# Python Dependencies
echo "Installiere Python Dependencies..."
pip3 install python-socketio[client]

# Video-Verzeichnis erstellen
VIDEO_DIR="/home/pi/quiz-videos"
mkdir -p "$VIDEO_DIR"
chown pi:pi "$VIDEO_DIR"

echo ""
echo "Video-Verzeichnis erstellt: $VIDEO_DIR"
echo "Lege deine Videos dort ab (z.B. video1.mp4, video2.mp4, ...)"
echo ""

# Systemd Service erstellen
echo "Erstelle systemd Service..."
cat > /etc/systemd/system/quiz-video-player.service <<EOF
[Unit]
Description=Quiz Video Player
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$(pwd)
Environment="QUIZ_APP_URL=https://wetterpanorama-kahoot.up.railway.app"
Environment="VIDEO_DIR=$VIDEO_DIR"
Environment="FULLSCREEN=true"
Environment="DISPLAY=:0"
ExecStart=/usr/bin/python3 $(pwd)/pi-video-player.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Service aktivieren
systemctl daemon-reload
systemctl enable quiz-video-player.service

echo ""
echo "=== Setup abgeschlossen! ==="
echo ""
echo "Nächste Schritte:"
echo ""
echo "1. Videos hinzufügen:"
echo "   cp deine-videos/*.mp4 $VIDEO_DIR/"
echo ""
echo "2. Video-Namen in app.py anpassen (FRAGEN Liste)"
echo ""
echo "3. Service starten:"
echo "   sudo systemctl start quiz-video-player"
echo ""
echo "4. Status prüfen:"
echo "   sudo systemctl status quiz-video-player"
echo ""
echo "5. Logs ansehen:"
echo "   sudo journalctl -u quiz-video-player -f"
echo ""
echo "Für manuellen Test:"
echo "   python3 pi-video-player.py"
echo ""
