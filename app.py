#!/usr/bin/env python3
import os
import sqlite3
import subprocess
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'quiz-secret-key-change-in-production'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Konfiguration
PORT = int(os.environ.get("PORT", 8080))
IS_RAILWAY = os.environ.get("RAILWAY_ENVIRONMENT") is not None
DATABASE_URL = os.environ.get("DATABASE_URL")
ERGEBNIS_ANZEIGE_SEKUNDEN = 20

FRAGEN = [
    {
        "video": "oetscher.mp4",
        "frage": "Welcher Berg ist das?",
        "antworten": ["Ötscher", "Luxemburg", "Dachstein", "Bad Aussee"],
        "richtig": "Ötscher"
    },
    {
        "video": "dachstein.mp4",
        "frage": "Welcher Berg ist das?",
        "antworten": ["Ötscher", "Luxemburg", "Dachstein", "Bad Aussee"],
        "richtig": "Dachstein"
    },
    {
        "video": "schneeberg.mp4",
        "frage": "Welcher Berg ist das?",
        "antworten": ["Schneeberg", "Rax", "Hochschwab", "Grimming"],
        "richtig": "Schneeberg"
    },
    {
        "video": "grossglockner.mp4",
        "frage": "Welcher Berg ist das?",
        "antworten": ["Großglockner", "Wildspitze", "Watzmann", "Zugspitze"],
        "richtig": "Großglockner"
    },
    {
        "video": "traunstein.mp4",
        "frage": "Welcher Berg ist das?",
        "antworten": ["Traunstein", "Schafberg", "Feuerkogel", "Katrin"],
        "richtig": "Traunstein"
    }
]

# Globaler Spielstatus und Spieler-Speicher
spiel_status = {
    "phase": "warten",  # warten, spielen, ergebnis
    "aktuelle_frage": 0,
    "spieler_count": 0
}

# Datenbank-Verbindung
def get_db():
    if DATABASE_URL:
        # PostgreSQL für Railway
        import psycopg2
        return psycopg2.connect(DATABASE_URL)
    else:
        # SQLite für lokal
        return sqlite3.connect('quiz.db')

def init_db_tables(conn):
    c = conn.cursor()
    if DATABASE_URL:
        # PostgreSQL
        c.execute('''CREATE TABLE IF NOT EXISTS spieler (
                        id SERIAL PRIMARY KEY,
                        name TEXT UNIQUE NOT NULL,
                        display_name TEXT,
                        beigetreten TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                     )''')
        c.execute('''CREATE TABLE IF NOT EXISTS antworten (
                        id SERIAL PRIMARY KEY,
                        spieler_name TEXT NOT NULL,
                        antwort TEXT NOT NULL,
                        richtig BOOLEAN NOT NULL,
                        frage_nr INTEGER NOT NULL,
                        zeitpunkt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(spieler_name, frage_nr)
                     )''')
    else:
        # SQLite
        c.execute('''CREATE TABLE IF NOT EXISTS spieler (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        display_name TEXT,
                        beigetreten TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                     )''')
        c.execute('''CREATE TABLE IF NOT EXISTS antworten (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        spieler_name TEXT NOT NULL,
                        antwort TEXT NOT NULL,
                        richtig BOOLEAN NOT NULL,
                        frage_nr INTEGER NOT NULL,
                        zeitpunkt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(spieler_name, frage_nr)
                     )''')
    conn.commit()

# Datenbank initialisieren
def init_db():
    conn = get_db()
    init_db_tables(conn)
    conn.close()

def reset_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM spieler')
    c.execute('DELETE FROM antworten')
    conn.commit()
    conn.close()
    
    spiel_status["phase"] = "warten"
    spiel_status["aktuelle_frage"] = 0
    spiel_status["spieler_count"] = 0

def get_spieler_count():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM spieler')
    count = c.fetchone()[0]
    conn.close()
    return count

def get_antworten_count(frage_nr):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM antworten WHERE frage_nr = %s' if DATABASE_URL else 'SELECT COUNT(*) FROM antworten WHERE frage_nr = ?', (frage_nr,))
    count = c.fetchone()[0]
    conn.close()
    return count

def berechne_rangliste():
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT 
                    COALESCE(s.display_name, a.spieler_name) as name,
                    SUM(CASE WHEN a.richtig = true THEN 1 ELSE 0 END) as punkte,
                    COUNT(*) as gesamt
                 FROM antworten a
                 LEFT JOIN spieler s ON a.spieler_name = s.name
                 GROUP BY a.spieler_name, s.display_name
                 ORDER BY punkte DESC, name ASC''')
    rangliste = c.fetchall()
    conn.close()
    return rangliste

def spiele_video(video_datei):
    if IS_RAILWAY:
        # Sende Event an Raspberry Pi Client
        socketio.emit('video_abspielen', {'video': video_datei})
        return
    video_pfad = os.path.join("videos", video_datei)
    if not os.path.exists(video_pfad):
        print(f"Video nicht gefunden: {video_pfad}")
        return
    try:
        subprocess.Popen(['mpv', '--fullscreen', video_pfad], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        try:
            subprocess.Popen(['cvlc', '--fullscreen', '--play-and-exit', video_pfad],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            print("Weder mpv noch vlc gefunden")

# Routes
@app.route('/')
def anmeldung():
    if spiel_status["phase"] != "warten":
        return redirect(url_for('warten'))
    return render_template('anmeldung.html')

@app.route('/anmelden', methods=['POST'])
def anmelden():
    name = request.form.get('name', '').strip()
    device_id = request.form.get('device_id', '').strip()
    
    if not name:
        return redirect(url_for('anmeldung'))
    
    if not device_id:
        device_id = f"{name}_{int(time.time() * 1000)}"
    
    conn = get_db()
    c = conn.cursor()
    try:
        placeholder = '%s' if DATABASE_URL else '?'
        
        # Prüfe ob Device schon existiert
        c.execute(f'SELECT id FROM spieler WHERE name = {placeholder}', (device_id,))
        existing = c.fetchone()
        
        if existing:
            c.execute(f'UPDATE spieler SET display_name = {placeholder} WHERE name = {placeholder}', (name, device_id))
        else:
            c.execute(f'INSERT INTO spieler (name, display_name) VALUES ({placeholder}, {placeholder})', (device_id, name))
        
        conn.commit()
        spiel_status["spieler_count"] = get_spieler_count()
        socketio.emit('spieler_update', {'count': spiel_status["spieler_count"]})
    except Exception as e:
        print(f"Fehler bei Anmeldung: {e}")
    finally:
        conn.close()
    
    response = redirect(url_for('warten'))
    response.set_cookie('device_id', device_id, max_age=86400)
    response.set_cookie('display_name', name, max_age=86400)
    return response

@app.route('/warten')
def warten():
    spieler_count = get_spieler_count()
    return render_template('warten.html', spieler_count=spieler_count)

@app.route('/frage')
def frage():
    if spiel_status["phase"] != "spielen":
        return redirect(url_for('warten'))
    
    frage_nr = spiel_status["aktuelle_frage"]
    if frage_nr >= len(FRAGEN):
        return redirect(url_for('ergebnis'))
    
    frage_data = FRAGEN[frage_nr]
    return render_template('frage.html', 
                          frage=frage_data, 
                          frage_nr=frage_nr + 1,
                          gesamt=len(FRAGEN))

@app.route('/antworten', methods=['POST'])
def antworten():
    spieler_name = request.form.get('spieler_name')
    frage_nr = int(request.form.get('frage_nr'))
    antwort = request.form.get('antwort')
    
    if not spieler_name or antwort is None:
        return jsonify({'error': 'Ungültige Daten'}), 400
    
    frage_data = FRAGEN[frage_nr]
    richtig = (antwort == frage_data["richtig"])
    
    conn = get_db()
    c = conn.cursor()
    placeholder = '%s' if DATABASE_URL else '?'
    
    try:
        c.execute(f'''INSERT INTO antworten (spieler_name, frage_nr, antwort, richtig)
                     VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})''', 
                  (spieler_name, frage_nr, antwort, richtig))
        conn.commit()
    except Exception as e:
        conn.close()
        if 'unique' in str(e).lower() or 'duplicate' in str(e).lower():
            return jsonify({'error': 'Bereits geantwortet'}), 400
        print(f"Fehler beim Speichern der Antwort: {e}")
        return jsonify({'error': 'Datenbankfehler'}), 500
    finally:
        conn.close()
    
    # Prüfen ob alle geantwortet haben
    antworten_count = get_antworten_count(frage_nr)
    spieler_count = get_spieler_count()
    
    socketio.emit('antwort_update', {
        'antworten': antworten_count,
        'gesamt': spieler_count
    })
    
    if antworten_count >= spieler_count:
        # Alle haben geantwortet
        socketio.start_background_task(naechste_frage_starten)
    
    return jsonify({'richtig': richtig, 'korrekte_antwort': frage_data["richtig"]})

def naechste_frage_starten():
    time.sleep(2)
    spiel_status["aktuelle_frage"] += 1
    
    if spiel_status["aktuelle_frage"] >= len(FRAGEN):
        # Spiel beendet
        spiel_status["phase"] = "ergebnis"
        rangliste = berechne_rangliste()
        socketio.emit('spiel_ende', {'rangliste': rangliste})
        socketio.emit('countdown_start', {'sekunden': ERGEBNIS_ANZEIGE_SEKUNDEN})
        socketio.start_background_task(countdown_und_reset)
    else:
        # Nächste Frage
        frage_nr = spiel_status["aktuelle_frage"]
        frage_data = FRAGEN[frage_nr]
        spiele_video(frage_data["video"])
        socketio.emit('neue_frage', {
            'frage_nr': frage_nr,
            'frage': frage_data["frage"],
            'antworten': frage_data["antworten"],
            'video': frage_data["video"]
        })

def countdown_und_reset():
    time.sleep(ERGEBNIS_ANZEIGE_SEKUNDEN)
    reset_db()
    socketio.emit('reset', {})
    print("🔄 Automatischer Reset durchgeführt - Datenbank geleert")

@app.route('/ergebnis')
def ergebnis():
    rangliste = berechne_rangliste()
    return render_template('ergebnis.html', rangliste=rangliste)

@app.route('/qrcode_display')
def qrcode_display():
    spieler_count = get_spieler_count()
    rangliste = berechne_rangliste() if spiel_status["phase"] == "ergebnis" else []
    return render_template('qrcode_display.html', 
                          spieler_count=spieler_count,
                          rangliste=rangliste,
                          phase=spiel_status["phase"])

@app.route('/api/qrcode')
def api_qrcode():
    host = request.host
    url = f"http://{host}/"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return jsonify({'qrcode': f'data:image/png;base64,{img_base64}'})

@app.route('/api/status')
def api_status():
    return jsonify({
        'phase': spiel_status["phase"],
        'aktuelle_frage': spiel_status["aktuelle_frage"],
        'spieler_count': get_spieler_count()
    })

# SocketIO Events
@socketio.on('spiel_starten')
def handle_spiel_starten():
    if spiel_status["phase"] == "warten" and get_spieler_count() > 0:
        spiel_status["phase"] = "spielen"
        spiel_status["aktuelle_frage"] = 0
        
        frage_data = FRAGEN[0]
        spiele_video(frage_data["video"])
        
        emit('spiel_gestartet', {
            'frage_nr': 0,
            'frage': frage_data["frage"],
            'antworten': frage_data["antworten"],
            'video': frage_data["video"]
        }, broadcast=True)

if __name__ == '__main__':
    init_db()
    print(f"Quiz-App startet auf Port {PORT}")
    print(f"Railway-Modus: {IS_RAILWAY}")
    socketio.run(app, host='0.0.0.0', port=PORT, debug=True, allow_unsafe_werkzeug=True)
