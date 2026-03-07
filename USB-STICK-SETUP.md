# USB-Stick Setup für Quiz-Videos

Die App scannt automatisch den USB-Stick und generiert Fragen aus den Dateinamen!

## Video-Benennung

**Wichtig:** Der Dateiname (ohne .mp4) ist die richtige Antwort!

### Beispiele:

```
Ötscher.mp4          → Richtige Antwort: "Ötscher"
Dachstein.mp4        → Richtige Antwort: "Dachstein"
Schneeberg.mp4       → Richtige Antwort: "Schneeberg"
Großglockner.mp4     → Richtige Antwort: "Großglockner"
Traunstein.mp4       → Richtige Antwort: "Traunstein"
```

## Frage-Generierung

Die App stellt automatisch die Frage: **"Was ist hier zu sehen?"**

Antwortmöglichkeiten werden automatisch aus den anderen Video-Dateinamen generiert.

### Beispiel:

Wenn du diese Videos hast:
- Ötscher.mp4
- Dachstein.mp4
- Schneeberg.mp4
- Großglockner.mp4

Dann wird für "Ötscher.mp4" folgende Frage generiert:
- Frage: "Was ist hier zu sehen?"
- Antworten: Ötscher, Dachstein, Schneeberg, Großglockner (zufällig gemischt)
- Richtige Antwort: Ötscher

## USB-Stick vorbereiten

### 1. USB-Stick formatieren

```bash
# FAT32 Format (kompatibel mit allen Systemen)
# Auf Mac:
diskutil list
diskutil eraseDisk FAT32 QUIZ_VIDEOS /dev/diskX

# Auf Linux/Pi:
sudo mkfs.vfat -F 32 /dev/sdX1
```

### 2. Videos auf USB-Stick kopieren

```bash
# Einfach Videos in den Root-Ordner kopieren
cp Ötscher.mp4 /Volumes/QUIZ_VIDEOS/
cp Dachstein.mp4 /Volumes/QUIZ_VIDEOS/
cp Schneeberg.mp4 /Volumes/QUIZ_VIDEOS/
# ... weitere Videos
```

### 3. USB-Stick am Raspberry Pi einstecken

Der Pi mountet den USB-Stick automatisch unter `/media/usb` oder `/media/pi/QUIZ_VIDEOS`

## Raspberry Pi Konfiguration

### USB-Stick automatisch mounten

Erstelle `/etc/fstab` Eintrag:

```bash
# USB-Stick UUID finden
sudo blkid

# Füge zu /etc/fstab hinzu:
UUID=XXXX-XXXX  /media/usb  vfat  defaults,nofail,uid=pi,gid=pi  0  0
```

### Video-Player Service anpassen

Bearbeite `/etc/systemd/system/quiz-video-player.service`:

```ini
Environment="VIDEO_DIR=/media/usb"
```

Oder wenn automatisch gemountet:
```ini
Environment="VIDEO_DIR=/media/pi/QUIZ_VIDEOS"
```

Dann Service neu starten:
```bash
sudo systemctl daemon-reload
sudo systemctl restart quiz-video-player
```

## USB-Stick Pfad finden

```bash
# Alle gemounteten USB-Geräte anzeigen
lsblk

# Oder
df -h | grep media

# Typische Pfade:
# /media/usb
# /media/pi/QUIZ_VIDEOS
# /mnt/usb
```

## Videos testen

```bash
# Manuell Video-Player starten
cd /home/pi
VIDEO_DIR=/media/usb python3 pi-video-player.py

# Du solltest sehen:
# 📹 Gefundene Videos (5):
#    - Ötscher.mp4
#    - Dachstein.mp4
#    - ...
```

## Tipps

### Video-Format

- Format: MP4 (H.264)
- Auflösung: 1080p oder niedriger
- Bitrate: 5-10 Mbps
- Audio: AAC

### Konvertieren mit ffmpeg

```bash
ffmpeg -i input.mov -c:v libx264 -preset medium -crf 23 -c:a aac "Ötscher.mp4"
```

### Dateinamen-Regeln

✅ Gut:
- Ötscher.mp4
- Großglockner.mp4
- Bad Aussee.mp4

❌ Vermeiden:
- oetscher_final_v2.mp4 (zu lang)
- video1.mp4 (nicht aussagekräftig)
- test.mp4 (nicht aussagekräftig)

### Mindestanzahl Videos

- Minimum: 4 Videos (für 4 Antwortmöglichkeiten)
- Empfohlen: 5-10 Videos
- Maximum: Unbegrenzt

## Troubleshooting

### USB-Stick wird nicht erkannt

```bash
# Prüfe ob USB-Stick erkannt wird
lsusb

# Prüfe Kernel-Logs
dmesg | tail -20

# Manuell mounten
sudo mount /dev/sda1 /media/usb
```

### Keine Videos gefunden

```bash
# Prüfe Pfad
ls -la /media/usb/

# Prüfe Berechtigungen
sudo chown -R pi:pi /media/usb/

# Prüfe Video-Format
file /media/usb/*.mp4
```

### Videos werden nicht abgespielt

```bash
# Teste mpv
mpv /media/usb/Ötscher.mp4

# Prüfe Logs
sudo journalctl -u quiz-video-player -f
```

## Workflow

1. **Videos auf USB-Stick kopieren** (mit aussagekräftigen Namen)
2. **USB-Stick am Pi einstecken**
3. **Pi startet automatisch** den Video-Player Service
4. **App scannt Videos** und generiert Fragen
5. **Spieler starten Quiz** über Railway-URL
6. **Videos werden automatisch** auf dem Fernseher abgespielt
7. **Fragen erscheinen** auf den Handys

## Videos aktualisieren

1. USB-Stick vom Pi entfernen
2. Videos hinzufügen/entfernen/umbenennen
3. USB-Stick wieder einstecken
4. Service neu starten:
   ```bash
   sudo systemctl restart quiz-video-player
   ```

Die App erkennt automatisch die neuen Videos!
