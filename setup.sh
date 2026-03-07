#!/bin/bash

echo "=== Quiz-App Setup für Raspberry Pi ==="

# Python Dependencies installieren
echo "Installiere Python Dependencies..."
pip3 install -r requirements.txt

# mpv installieren (für Video-Wiedergabe)
echo "Installiere mpv..."
sudo apt-get update
sudo apt-get install -y mpv

# Videos Ordner erstellen
mkdir -p videos
echo "Lege deine Video-Dateien in den 'videos/' Ordner"

# Systemd Service erstellen
echo "Erstelle systemd Service..."
sudo tee /etc/systemd/system/quiz-app.service > /dev/null <<EOF
[Unit]
Description=Quiz App
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Service aktivieren
sudo systemctl daemon-reload
sudo systemctl enable quiz-app.service

# Chromium Kiosk-Modus Autostart
echo "Richte Chromium Kiosk-Modus ein..."
mkdir -p ~/.config/autostart

tee ~/.config/autostart/quiz-kiosk.desktop > /dev/null <<EOF
[Desktop Entry]
Type=Application
Name=Quiz Kiosk
Exec=chromium-browser --kiosk --app=http://localhost:5000/qrcode_display
X-GNOME-Autostart-enabled=true
EOF

echo ""
echo "=== Setup abgeschlossen! ==="
echo ""
echo "Nächste Schritte:"
echo "1. Lege deine Videos in den 'videos/' Ordner (video1.mp4, video2.mp4, etc.)"
echo "2. Passe die Fragen in app.py an (FRAGEN Liste)"
echo "3. Starte den Service: sudo systemctl start quiz-app"
echo "4. Prüfe den Status: sudo systemctl status quiz-app"
echo "5. Logs ansehen: sudo journalctl -u quiz-app -f"
echo ""
echo "Für manuellen Start: python3 app.py"
echo "QR-Code Display: http://localhost:5000/qrcode_display"
