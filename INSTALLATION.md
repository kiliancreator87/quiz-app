# Quiz-App Installation - Ohne Netzwerk

## Für Raspberry Pi (Standalone mit eigenem WLAN)

Der Pi erstellt einen eigenen WLAN-Hotspot. Handys verbinden sich direkt mit dem Pi.

### Einmalige Installation:

1. **Dateien auf den Pi kopieren:**
   ```bash
   # Auf deinem Mac/PC
   scp -r quiz-app pi@raspberrypi.local:/home/pi/
   ```

2. **Auf dem Pi einloggen:**
   ```bash
   ssh pi@raspberrypi.local
   cd quiz-app
   ```

3. **Setup ausführen:**
   ```bash
   chmod +x setup-hotspot.sh
   sudo ./setup-hotspot.sh
   ```

4. **Pi neu starten** (wird automatisch gefragt)

### Nach dem Neustart:

✅ Pi startet automatisch WLAN Hotspot: **"Quiz-Spiel"**  
✅ Passwort: **"quiz1234"**  
✅ Quiz-App läuft automatisch  
✅ QR-Code wird auf dem Bildschirm angezeigt  

### Spieler verbinden:

1. Mit WLAN "Quiz-Spiel" verbinden (Passwort: quiz1234)
2. QR-Code vom Bildschirm scannen
3. Namen eingeben
4. Spielen!

---

## Für Mac (Zum Testen)

### Variante 1: Localhost (nur auf dem Mac)

```bash
cd quiz-app
python3 app.py
```

Öffne mehrere Browser-Tabs:
- http://localhost:5000/qrcode_display (Hauptbildschirm)
- http://localhost:5000/ (Spieler 1, 2, 3...)

### Variante 2: Mit Handys im gleichen WLAN

1. **Mac IP-Adresse finden:**
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```
   Beispiel: `192.168.1.100`

2. **App starten:**
   ```bash
   cd quiz-app
   python3 app.py
   ```

3. **Auf Handys (im gleichen WLAN):**
   - QR-Code scannen oder direkt zu `http://192.168.1.100:5000` gehen

### Variante 3: Mac als Hotspot

1. **Mac Hotspot aktivieren:**
   - Systemeinstellungen → Allgemein → Freigaben
   - "Internetfreigabe" aktivieren
   - WLAN-Name und Passwort festlegen

2. **App starten:**
   ```bash
   cd quiz-app
   python3 app.py
   ```

3. **Handys verbinden sich mit Mac-Hotspot**
4. **QR-Code scannen**

---

## Videos hinzufügen

Lege deine Video-Dateien in den `videos/` Ordner:

```bash
cd quiz-app
mkdir -p videos
# Kopiere video1.mp4, video2.mp4, video3.mp4 in den Ordner
```

Video-Namen müssen mit den Namen in `app.py` übereinstimmen (siehe `FRAGEN` Liste).

---

## Fragen anpassen

Bearbeite `app.py` und ändere die `FRAGEN` Liste:

```python
FRAGEN = [
    {
        "video": "video1.mp4",
        "frage": "Deine Frage hier?",
        "antworten": ["A", "B", "C", "D"],
        "richtig": "B"
    },
    # Weitere Fragen...
]
```

---

## Troubleshooting

### Pi: Hotspot startet nicht
```bash
sudo systemctl status hostapd
sudo systemctl status dnsmasq
sudo journalctl -u hostapd -n 50
```

### Pi: Quiz-App läuft nicht
```bash
sudo systemctl status quiz-app
sudo journalctl -u quiz-app -f
```

### Pi: Chromium zeigt QR-Code nicht
```bash
# Manuell testen
DISPLAY=:0 chromium-browser --kiosk http://localhost:5000/qrcode_display
```

### Mac: Port bereits belegt
```bash
lsof -ti:5000 | xargs kill -9
```

### Handys können sich nicht verbinden
- Prüfe ob Handys mit dem richtigen WLAN verbunden sind
- Prüfe Firewall-Einstellungen
- Teste mit `http://10.0.0.1:5000` (Pi) oder `http://[MAC-IP]:5000`

---

## Hotspot-Einstellungen ändern

Bearbeite `setup-hotspot.sh` vor der Installation:

```bash
HOTSPOT_SSID="Dein-Name"      # WLAN Name
HOTSPOT_PASSWORD="deinpasswort"  # Mindestens 8 Zeichen
```

Dann Setup erneut ausführen.
