#!/bin/bash

echo "=== Quiz-App Hotspot Setup für Raspberry Pi ==="
echo ""

# Prüfen ob als root ausgeführt
if [ "$EUID" -ne 0 ]; then 
    echo "Bitte als root ausführen: sudo ./setup-hotspot.sh"
    exit 1
fi

# Hotspot Konfiguration
HOTSPOT_SSID="Quiz-Spiel"
HOTSPOT_PASSWORD="quiz1234"
PI_IP="10.0.0.1"

echo "Hotspot Name: $HOTSPOT_SSID"
echo "Passwort: $HOTSPOT_PASSWORD"
echo "Pi IP-Adresse: $PI_IP"
echo ""

# Pakete installieren
echo "Installiere benötigte Pakete..."
apt-get update
apt-get install -y hostapd dnsmasq python3-pip mpv chromium-browser

# hostapd und dnsmasq stoppen
systemctl stop hostapd
systemctl stop dnsmasq

# dhcpcd Konfiguration
echo "Konfiguriere statische IP..."
cat >> /etc/dhcpcd.conf <<EOF

# Quiz-App Hotspot
interface wlan0
    static ip_address=$PI_IP/24
    nohook wpa_supplicant
EOF

# dnsmasq Konfiguration
echo "Konfiguriere DHCP Server..."
mv /etc/dnsmasq.conf /etc/dnsmasq.conf.backup
cat > /etc/dnsmasq.conf <<EOF
interface=wlan0
dhcp-range=10.0.0.10,10.0.0.50,255.255.255.0,24h
domain=wlan
address=/quiz.local/$PI_IP
EOF

# hostapd Konfiguration
echo "Konfiguriere Access Point..."
cat > /etc/hostapd/hostapd.conf <<EOF
interface=wlan0
driver=nl80211
ssid=$HOTSPOT_SSID
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=$HOTSPOT_PASSWORD
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

# hostapd daemon Konfiguration
sed -i 's|#DAEMON_CONF=""|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd

# Services aktivieren
echo "Aktiviere Services..."
systemctl unmask hostapd
systemctl enable hostapd
systemctl enable dnsmasq

# Python Dependencies installieren
echo "Installiere Python Dependencies..."
cd "$(dirname "$0")"
pip3 install -r requirements.txt

# Quiz-App Service erstellen
echo "Erstelle Quiz-App Service..."
cat > /etc/systemd/system/quiz-app.service <<EOF
[Unit]
Description=Quiz App
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/app.py
Restart=always
RestartSec=10
Environment="DISPLAY=:0"

[Install]
WantedBy=multi-user.target
EOF

# Chromium Autostart für QR-Code Display
echo "Richte Chromium Kiosk-Modus ein..."
mkdir -p /home/pi/.config/lxsession/LXDE-pi
cat > /home/pi/.config/lxsession/LXDE-pi/autostart <<EOF
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@xscreensaver -no-splash
@xset s off
@xset -dpms
@xset s noblank
@chromium-browser --kiosk --app=http://localhost:5000/qrcode_display
EOF

chown -R pi:pi /home/pi/.config

# Videos Ordner erstellen
mkdir -p videos
chown pi:pi videos

# Services neu laden
systemctl daemon-reload
systemctl enable quiz-app

echo ""
echo "=== Setup abgeschlossen! ==="
echo ""
echo "WICHTIG: Raspberry Pi jetzt neu starten!"
echo ""
echo "Nach dem Neustart:"
echo "1. Pi startet automatisch WLAN Hotspot '$HOTSPOT_SSID'"
echo "2. Passwort: $HOTSPOT_PASSWORD"
echo "3. Quiz-App startet automatisch"
echo "4. QR-Code wird auf dem Bildschirm angezeigt"
echo ""
echo "Spieler verbinden sich mit dem WLAN und scannen den QR-Code!"
echo ""
echo "Neustart jetzt durchführen? (j/n)"
read -r answer
if [ "$answer" = "j" ] || [ "$answer" = "J" ]; then
    reboot
fi
