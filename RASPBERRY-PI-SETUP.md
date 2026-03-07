# Raspberry Pi Video Player Setup

Der Raspberry Pi spielt Videos auf dem Fernseher ab, während die Handys über Railway die Fragen bekommen.

## Architektur

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Raspberry  │◄────────┤   Railway    │────────►│   Handys    │
│     Pi      │ WebSocket│   Quiz-App   │ Internet│  (Mobilfunk)│
│  + Videos   │         │              │         │             │
└──────┬──────┘         └──────────────┘         └─────────────┘
       │
       ▼
  ┌─────────┐
  │Fernseher│
  │ (HDMI)  │
  └─────────┘
```

## Installation auf Raspberry Pi

### 1. Dateien auf den Pi kopieren

```bash
# Auf deinem Mac
cd quiz-app
scp pi-video-player.py setup-pi-player.sh pi@raspberrypi.local:/home/pi/
```

### 2. Setup ausführen

```bash
# Auf dem Pi
ssh pi@raspberrypi.local
cd /home/pi
chmod +x setup-pi-player.sh
sudo ./setup-pi-player.sh
```

### 3. Videos hinzufügen

```bash
# Videos auf den Pi kopieren
scp deine-videos/*.mp4 pi@raspberrypi.local:/home/pi/quiz-videos/

# Oder auf dem Pi direkt
cp /pfad/zu/videos/*.mp4 /home/pi/quiz-videos/
```

**Wichtig:** Video-Namen müssen mit den Namen in `app.py` übereinstimmen!

Beispiel in `app.py`:
```python
FRAGEN = [
    {
        "video": "oetscher.mp4",  # Diese Datei muss existieren!
        "frage": "Welcher Berg ist das?",
        "antworten": ["Ötscher", "Luxemburg", "Dachstein", "Bad Aussee"],
        "richtig": "Ötscher"
    }
]
```

### 4. Service starten

```bash
sudo systemctl start quiz-video-player
sudo systemctl status quiz-video-player
```

### 5. Logs ansehen

```bash
# Live-Logs
sudo journalctl -u quiz-video-player -f

# Letzte 50 Zeilen
sudo journalctl -u quiz-video-player -n 50
```

## Manueller Test

```bash
cd /home/pi
python3 pi-video-player.py
```

Du solltest sehen:
```
🎬 Quiz Video Player für Raspberry Pi
📹 Gefundene Videos (3):
   - oetscher.mp4
   - dachstein.mp4
   - luxenburg.mp4
🌐 Verbinde mit: https://wetterpanorama-kahoot.up.railway.app
✅ Verbunden
⏳ Warte auf Quiz-Events...
```

## Spielablauf

1. **Spieler melden sich an** (über Handy auf Railway-URL)
2. **Spieler startet Quiz** (Button im Warteraum)
3. **Pi spielt Video 1** auf dem Fernseher
4. **Handys zeigen Frage 1** mit Antwortmöglichkeiten
5. **Spieler antworten** → bekommen Feedback
6. **Sobald alle geantwortet haben** → Pi spielt Video 2
7. **Handys zeigen Frage 2**
8. ... und so weiter

## Konfiguration

Bearbeite `/etc/systemd/system/quiz-video-player.service`:

```ini
Environment="QUIZ_APP_URL=https://deine-url.railway.app"
Environment="VIDEO_DIR=/home/pi/quiz-videos"
Environment="FULLSCREEN=true"
```

Nach Änderungen:
```bash
sudo systemctl daemon-reload
sudo systemctl restart quiz-video-player
```

## Troubleshooting

### Videos werden nicht abgespielt

```bash
# Prüfe ob mpv installiert ist
which mpv

# Teste Video manuell
mpv /home/pi/quiz-videos/oetscher.mp4

# Installiere mpv falls fehlt
sudo apt-get install mpv
```

### Keine Verbindung zu Railway

```bash
# Prüfe Internet-Verbindung
ping -c 3 google.com

# Prüfe Railway-URL
curl https://wetterpanorama-kahoot.up.railway.app/api/status

# Prüfe Logs
sudo journalctl -u quiz-video-player -f
```

### Video-Dateien nicht gefunden

```bash
# Liste Videos auf
ls -lh /home/pi/quiz-videos/

# Prüfe Berechtigungen
sudo chown -R pi:pi /home/pi/quiz-videos/
```

### HDMI-Ausgabe funktioniert nicht

```bash
# Prüfe DISPLAY Variable
echo $DISPLAY

# Setze DISPLAY in Service
sudo nano /etc/systemd/system/quiz-video-player.service
# Füge hinzu: Environment="DISPLAY=:0"
```

## Autostart beim Booten

Der Service startet automatisch beim Booten. Um das zu deaktivieren:

```bash
sudo systemctl disable quiz-video-player
```

Wieder aktivieren:
```bash
sudo systemctl enable quiz-video-player
```

## Fernseher-Einstellungen

- Verbinde Pi mit HDMI-Kabel
- Stelle Fernseher auf richtigen HDMI-Eingang
- Pi sollte Desktop anzeigen (oder Videos im Vollbild)

## Performance-Tipps

- Verwende H.264 codierte Videos (beste Kompatibilität)
- Auflösung: 1080p oder niedriger
- Bitrate: 5-10 Mbps
- Format: MP4 oder MKV

Konvertieren mit ffmpeg:
```bash
ffmpeg -i input.mov -c:v libx264 -preset medium -crf 23 -c:a aac output.mp4
```
