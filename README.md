# Quiz-App

Vollautomatisches Quiz-Spiel mit Flask, SocketIO und QR-Code Anmeldung.

## Features

- QR-Code Anmeldung über Handy
- Echtzeit-Synchronisation aller Spieler via WebSockets
- Automatische Video-Wiedergabe (lokal/Pi)
- Live-Feedback nach jeder Antwort
- Automatischer Spielablauf
- Rangliste mit 60s Countdown
- Automatischer Reset nach Spielende

## Installation

### Lokal (Mac/Linux)

```bash
cd quiz-app
pip3 install -r requirements.txt
python3 app.py
```

Öffne Browser:
- QR-Code Display: http://localhost:5000/qrcode_display
- Spieler scannen QR-Code mit Handy

### Raspberry Pi

```bash
cd quiz-app
chmod +x setup.sh
./setup.sh
```

Das Setup-Script:
- Installiert alle Dependencies
- Richtet systemd Service ein
- Konfiguriert Chromium Kiosk-Modus für Autostart

Service steuern:
```bash
sudo systemctl start quiz-app
sudo systemctl stop quiz-app
sudo systemctl status quiz-app
sudo journalctl -u quiz-app -f  # Logs
```

### Railway.app Deployment

1. Repository auf GitHub pushen
2. Railway.app Projekt erstellen
3. GitHub Repository verbinden
4. Railway erkennt automatisch Procfile
5. App wird deployed

Die App erkennt automatisch Railway via `RAILWAY_ENVIRONMENT` Variable und überspringt Video-Wiedergabe.

## Konfiguration

### Fragen anpassen

Bearbeite `app.py` und passe die `FRAGEN` Liste an:

```python
FRAGEN = [
    {
        "video": "video1.mp4",
        "frage": "Deine Frage hier?",
        "antworten": ["Antwort A", "Antwort B", "Antwort C", "Antwort D"],
        "richtig": "Antwort B"
    },
    # Weitere Fragen...
]
```

### Videos hinzufügen

Lege Video-Dateien in den `videos/` Ordner:
```
videos/
├── video1.mp4
├── video2.mp4
└── video3.mp4
```

Video-Namen müssen mit den Namen in der `FRAGEN` Liste übereinstimmen.

### Countdown-Zeit ändern

```python
ERGEBNIS_ANZEIGE_SEKUNDEN = 60  # Sekunden bis zum Reset
```

## Spielablauf

1. Server startet → QR-Code wird angezeigt
2. Spieler scannen QR → geben Namen ein → Warteraum
3. Ein Spieler drückt "Spiel starten"
4. Video 1 startet + Frage 1 erscheint auf allen Handys
5. Spieler antworten → sofortiges Feedback
6. Sobald alle geantwortet haben → 2s Pause → nächste Frage
7. Nach letzter Frage → Rangliste mit 60s Countdown
8. Automatischer Reset → zurück zu Schritt 1

## API Endpoints

- `GET /` - Anmeldung
- `POST /anmelden` - Spieler registrieren
- `GET /warten` - Warteraum
- `GET /frage` - Aktuelle Frage
- `POST /antworten` - Antwort absenden
- `GET /ergebnis` - Rangliste
- `GET /qrcode_display` - QR-Code Vollbild
- `GET /api/qrcode` - QR-Code als Base64
- `GET /api/status` - Spielstatus als JSON

## WebSocket Events

### Client → Server
- `spiel_starten` - Spiel starten

### Server → Client
- `spieler_update` - Spieleranzahl aktualisiert
- `spiel_gestartet` - Spiel wurde gestartet
- `neue_frage` - Nächste Frage verfügbar
- `antwort_update` - Antwort-Status Update
- `spiel_ende` - Spiel beendet, Rangliste verfügbar
- `countdown_start` - Countdown gestartet
- `reset` - Spiel wurde zurückgesetzt

## Technologie

- Backend: Python 3 + Flask
- Echtzeit: Flask-SocketIO (WebSockets)
- Datenbank: SQLite
- Frontend: Jinja2 Templates + Vanilla JS
- QR-Code: qrcode[pil]
- Video: mpv (lokal/Pi), übersprungen auf Railway

## Troubleshooting

### Videos werden nicht abgespielt
- Prüfe ob mpv installiert ist: `which mpv`
- Installiere mpv: `sudo apt-get install mpv` (Pi) oder `brew install mpv` (Mac)
- Prüfe Video-Pfade in `videos/` Ordner

### WebSocket Verbindung schlägt fehl
- Prüfe Firewall-Einstellungen
- Stelle sicher dass Port 5000 erreichbar ist
- Prüfe Browser-Konsole für Fehler

### Datenbank-Fehler
- Lösche `quiz.db` und starte neu
- Prüfe Schreibrechte im Verzeichnis

## Lizenz

MIT
