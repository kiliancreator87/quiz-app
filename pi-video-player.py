#!/usr/bin/env python3
"""
Raspberry Pi Video Player Client
Verbindet sich mit der Railway Quiz-App und spielt Videos ab
"""

import os
import sys
import subprocess
import socketio
import time
from pathlib import Path

# Konfiguration
QUIZ_APP_URL = os.environ.get('QUIZ_APP_URL', 'https://wetterpanorama-kahoot.up.railway.app')
VIDEO_DIR = os.environ.get('VIDEO_DIR', '/home/pi/quiz-videos')
FULLSCREEN = os.environ.get('FULLSCREEN', 'true').lower() == 'true'

# SocketIO Client
sio = socketio.Client()

current_process = None

def spiele_video(video_datei):
    global current_process
    
    # Vorheriges Video stoppen
    if current_process:
        try:
            current_process.terminate()
            current_process.wait(timeout=2)
        except:
            current_process.kill()
    
    video_pfad = os.path.join(VIDEO_DIR, video_datei)
    
    if not os.path.exists(video_pfad):
        print(f"❌ Video nicht gefunden: {video_pfad}")
        return
    
    print(f"▶️  Spiele Video: {video_datei}")
    
    # Versuche mpv, dann vlc
    try:
        if FULLSCREEN:
            current_process = subprocess.Popen(
                ['mpv', '--fullscreen', '--no-terminal', video_pfad],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            current_process = subprocess.Popen(
                ['mpv', video_pfad],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
    except FileNotFoundError:
        try:
            if FULLSCREEN:
                current_process = subprocess.Popen(
                    ['cvlc', '--fullscreen', '--play-and-exit', video_pfad],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                current_process = subprocess.Popen(
                    ['cvlc', '--play-and-exit', video_pfad],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
        except FileNotFoundError:
            print("❌ Weder mpv noch vlc gefunden!")
            print("   Installiere mit: sudo apt-get install mpv")

@sio.event
def connect():
    print(f"✅ Verbunden mit {QUIZ_APP_URL}")
    print(f"📁 Video-Verzeichnis: {VIDEO_DIR}")

@sio.event
def disconnect():
    print("❌ Verbindung getrennt")

@sio.on('spiel_gestartet')
def on_spiel_gestartet(data):
    print("🎮 Spiel gestartet!")
    if 'video' in data:
        spiele_video(data['video'])

@sio.on('neue_frage')
def on_neue_frage(data):
    print(f"❓ Neue Frage: {data.get('frage_nr', '?')}")
    if 'video' in data:
        spiele_video(data['video'])

@sio.on('video_abspielen')
def on_video_abspielen(data):
    video = data.get('video')
    if video:
        spiele_video(video)

@sio.on('reset')
def on_reset(data):
    print("🔄 Spiel zurückgesetzt")
    global current_process
    if current_process:
        try:
            current_process.terminate()
        except:
            pass

def main():
    print("=" * 50)
    print("🎬 Quiz Video Player für Raspberry Pi")
    print("=" * 50)
    print()
    
    # Video-Verzeichnis prüfen
    if not os.path.exists(VIDEO_DIR):
        print(f"⚠️  Video-Verzeichnis existiert nicht: {VIDEO_DIR}")
        print(f"   Erstelle Verzeichnis...")
        os.makedirs(VIDEO_DIR, exist_ok=True)
    
    # Videos auflisten
    videos = list(Path(VIDEO_DIR).glob('*.mp4')) + list(Path(VIDEO_DIR).glob('*.mkv'))
    if videos:
        print(f"📹 Gefundene Videos ({len(videos)}):")
        for v in videos:
            print(f"   - {v.name}")
    else:
        print(f"⚠️  Keine Videos gefunden in {VIDEO_DIR}")
        print(f"   Lege .mp4 oder .mkv Dateien dort ab")
    
    print()
    print(f"🌐 Verbinde mit: {QUIZ_APP_URL}")
    print()
    
    try:
        sio.connect(QUIZ_APP_URL)
        print("⏳ Warte auf Quiz-Events...")
        print("   (Drücke Ctrl+C zum Beenden)")
        sio.wait()
    except KeyboardInterrupt:
        print("\n👋 Beende...")
        if current_process:
            current_process.terminate()
        sio.disconnect()
    except Exception as e:
        print(f"❌ Fehler: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
