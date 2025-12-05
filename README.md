# 🌍 Copernicus Climate Dashboard

Ein interaktives Dashboard für Klimadaten von Copernicus Climate Data Store.

![Dashboard Preview](https://img.shields.io/badge/Python-3.9+-blue?logo=python) 
![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask)

---

## ✨ Features

- 📰 **Neueste Veröffentlichungen** - Aktuelle Berichte vom Copernicus Climate Data Store
- 💡 **KI-Erkenntnisse** - GPT-5.1 analysiert Berichte und generiert Recherche-Ansätze für Journalist:innen
- 🤖 **Klima-Suchagent** - Stelle Fragen zu Klimadaten und erhalte Antworten
- 📈 **Interaktive Grafiken** - Temperatur & CO₂ mit Hintergrundinfos
- 📊 **Klima-Fakten** - Wichtige Statistiken auf einen Blick
- 💡 **Schnellfragen** - Vordefinierte Fragen für den schnellen Einstieg

---

## 🚀 Installation (Schritt für Schritt)

### 1. Python installieren

Falls du Python noch nicht hast, lade es hier herunter:
👉 [python.org/downloads](https://www.python.org/downloads/)

**Wichtig:** Bei der Installation den Haken bei "Add Python to PATH" setzen!

### 2. Terminal öffnen

- **Windows:** Drücke `Windows + R`, tippe `cmd` und drücke Enter
- **Mac:** Öffne "Terminal" aus den Programmen
- **In Cursor:** Drücke `Strg + Ö` (oder View → Terminal)

### 3. Zum Projektordner navigieren

```bash
cd C:\Users\merle\Documents\Cursor\KPB
```

### 4. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 5. OpenAI API-Key einrichten (für KI-Erkenntnisse)

1. Gehe zu [platform.openai.com](https://platform.openai.com)
2. Erstelle einen Account oder melde dich an
3. Klicke auf "API Keys" → "Create new secret key"
4. Erstelle eine Datei namens `.env` im Projektordner mit folgendem Inhalt:

```
OPENAI_API_KEY=dein-api-key-hier
```

> ⚠️ **Hinweis:** Ohne API-Key funktioniert die App trotzdem, nur die KI-Erkenntnisse sind dann nicht verfügbar.

### 6. App starten

```bash
python app.py
```

### 6. Im Browser öffnen

Gehe zu: **http://localhost:5000**

🎉 Fertig! Das Dashboard sollte jetzt angezeigt werden!

---

## 📁 Projektstruktur

```
KPB/
├── app.py              # Hauptanwendung (Backend mit OpenAI)
├── requirements.txt    # Python-Abhängigkeiten
├── README.md           # Diese Anleitung
├── env-einrichtung.txt # Anleitung für API-Key
├── .env                # Dein API-Key (musst du erstellen!)
├── templates/
│   └── index.html      # Dashboard (Frontend)
└── static/             # Für Bilder, CSS etc. (optional)
```

---

## 🤖 Suchagent verwenden

Der Suchagent kann Fragen zu folgenden Themen beantworten:

| Thema | Beispielfragen |
|-------|----------------|
| 🌡️ Temperatur | "Wie warm ist es geworden?" |
| 🧊 Meereis | "Was passiert mit dem Eis in der Arktis?" |
| 🌊 Ozean | "Wie stark erwärmen sich die Meere?" |
| ⛈️ Extremwetter | "Gibt es mehr Hitzewellen?" |
| 💨 CO2 | "Wie hoch ist die CO2-Konzentration?" |
| 🛰️ Copernicus | "Was ist Copernicus?" |

---

## 🛠️ Anpassungen vornehmen

### Neue Wissensinhalte hinzufügen

Öffne `app.py` und erweitere das `KLIMAWISSEN` Dictionary:

```python
KLIMAWISSEN = {
    "dein_thema": """
    🌱 **Dein Thema**
    
    Hier kommt dein Text...
    """,
    # ... weitere Themen
}
```

### Design ändern

Die Farben findest du in `templates/index.html` im CSS-Bereich:

```css
:root {
    --primary: #0ea5e9;      /* Hauptfarbe ändern */
    --secondary: #10b981;    /* Zweitfarbe ändern */
    --bg-dark: #0f172a;      /* Hintergrund ändern */
}
```

---

## ❓ Häufige Probleme

### "pip" wird nicht erkannt

→ Python neu installieren und "Add to PATH" aktivieren

### "Port 5000 bereits in Verwendung"

→ In `app.py` die letzte Zeile ändern:
```python
app.run(debug=True, port=5001)  # Anderen Port verwenden
```

### Keine Veröffentlichungen werden angezeigt

→ Das ist normal! Die App zeigt Beispieldaten, wenn der Copernicus-Feed nicht erreichbar ist.

---

## 📚 Weiterlernen

- [Flask Tutorial (Deutsch)](https://flask.palletsprojects.com/en/3.0.x/tutorial/)
- [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/)
- [Python für Anfänger](https://www.python.org/about/gettingstarted/)

---

## 📝 Lizenz

Dieses Projekt ist für Lernzwecke erstellt. Die Klimadaten stammen vom Copernicus Climate Change Service (C3S).

---

Erstellt mit 💚 für unseren Planeten

