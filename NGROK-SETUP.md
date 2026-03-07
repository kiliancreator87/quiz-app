# Quiz-App mit ngrok (Sofort-Lösung)

ngrok macht deinen Mac aus dem Internet erreichbar - in 2 Minuten!

## Installation

```bash
# Mit Homebrew
brew install ngrok

# ODER Download von: https://ngrok.com/download
```

## Verwendung

**Terminal 1 - Quiz-App starten:**
```bash
cd quiz-app
python3 app.py
```

**Terminal 2 - ngrok starten:**
```bash
ngrok http 8080
```

Du bekommst eine URL wie:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8080
```

## Fertig!

- **QR-Code Display:** `https://abc123.ngrok.io/qrcode_display`
- **Spieler öffnen auf dem iPhone:** `https://abc123.ngrok.io`
- Funktioniert über Mobilfunk!
- Keine WLAN-Verbindung nötig!

## Wichtig

- URL ändert sich bei jedem ngrok-Neustart (kostenlose Version)
- Für feste URL: ngrok Account erstellen (kostenlos)
- Läuft nur solange dein Mac an ist

## Mit festem Domain (optional)

1. Account erstellen: https://dashboard.ngrok.com/signup
2. Authtoken holen: https://dashboard.ngrok.com/get-started/your-authtoken
3. Token setzen:
   ```bash
   ngrok config add-authtoken DEIN_TOKEN
   ```
4. Feste Domain reservieren (kostenlos 1x)
5. Starten mit:
   ```bash
   ngrok http --domain=deine-domain.ngrok-free.app 8080
   ```

## Vorteile vs Railway

✅ Sofort einsatzbereit (2 Minuten)
✅ Videos funktionieren (läuft auf deinem Mac)
✅ Keine Git/GitHub nötig
❌ Mac muss laufen
❌ URL ändert sich (außer mit Account)
