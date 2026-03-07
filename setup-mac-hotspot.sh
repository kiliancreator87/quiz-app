#!/bin/bash

echo "=== Quiz-App Mac Hotspot Setup ==="
echo ""
echo "WICHTIG: Dieser Script hilft dir beim Setup."
echo "Einige Schritte musst du manuell in den Systemeinstellungen machen."
echo ""

# Python Dependencies prüfen
echo "Prüfe Python Dependencies..."
pip3 install -r requirements.txt 2>/dev/null || {
    echo "Installiere Dependencies..."
    pip3 install --user -r requirements.txt
}

echo ""
echo "=== MANUELLE SCHRITTE ==="
echo ""
echo "1. HOTSPOT AKTIVIEREN:"
echo "   - Öffne: Systemeinstellungen → Allgemein → Freigaben"
echo "   - Aktiviere: 'Internetfreigabe'"
echo "   - Wähle: 'WLAN' als Freigabequelle"
echo "   - WLAN-Optionen:"
echo "     • Netzwerkname: Quiz-Spiel"
echo "     • Kanal: 11"
echo "     • Sicherheit: WPA2"
echo "     • Passwort: quiz1234"
echo ""
echo "2. FIREWALL ANPASSEN (falls aktiviert):"
echo "   - Systemeinstellungen → Netzwerk → Firewall"
echo "   - Firewall-Optionen → Python erlauben"
echo ""
echo "Drücke ENTER wenn der Hotspot läuft..."
read

echo ""
echo "Starte Quiz-App auf Port 8080..."
echo ""
echo "=== WICHTIG ==="
echo "Auf dem iPhone/Smartphone:"
echo "1. Mit WLAN 'Quiz-Spiel' verbinden (Passwort: quiz1234)"
echo "2. QR-Code vom Bildschirm scannen"
echo "3. ODER direkt zu: http://10.0.0.1:8080"
echo ""
echo "Auf diesem Mac:"
echo "QR-Code Display: http://localhost:8080/qrcode_display"
echo ""
echo "Drücke Ctrl+C zum Beenden"
echo ""

# App starten
python3 app.py
