# Quiz-App auf Railway.app deployen (Kostenlos)

Die App wird im Internet verfügbar - iPhones brauchen nur Mobilfunk!

## Schritt 1: GitHub Repository erstellen

```bash
cd quiz-app

# Git initialisieren
git init
git add .
git commit -m "Initial commit"

# GitHub Repository erstellen (im Browser auf github.com)
# Dann:
git remote add origin https://github.com/DEIN-USERNAME/quiz-app.git
git branch -M main
git push -u origin main
```

## Schritt 2: Railway Account erstellen

1. Gehe zu: https://railway.app
2. Klicke auf **"Start a New Project"**
3. Login mit GitHub
4. Wähle **"Deploy from GitHub repo"**
5. Wähle dein **quiz-app** Repository
6. Railway deployed automatisch!

## Schritt 3: URL bekommen

Nach dem Deployment:
1. Klicke auf dein Projekt
2. Gehe zu **Settings → Networking**
3. Klicke **"Generate Domain"**
4. Du bekommst eine URL wie: `https://quiz-app-production.up.railway.app`

## Schritt 4: Fertig!

- **QR-Code Display:** `https://deine-app.railway.app/qrcode_display`
- **Spieler scannen QR-Code** mit dem Handy (über Mobilfunk!)
- Keine WLAN-Verbindung nötig!

## Wichtig

- Videos werden auf Railway NICHT abgespielt (nur lokal/Pi)
- Kostenlos: 500 Stunden/Monat (mehr als genug)
- App schläft nach Inaktivität (startet automatisch beim ersten Zugriff)

## Lokales Testen vor Deployment

```bash
# Simuliere Railway-Umgebung
export RAILWAY_ENVIRONMENT=production
export PORT=8080
python3 app.py
```

## Logs ansehen

Im Railway Dashboard:
- Klicke auf dein Projekt
- Tab **"Deployments"**
- Klicke auf aktuelles Deployment
- Siehe Logs in Echtzeit
