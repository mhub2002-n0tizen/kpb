# =============================================================================
# Copernicus Climate Dashboard - Hauptanwendung
# Eine einfache Web-App für Klimadaten-Veröffentlichungen
# =============================================================================

from flask import Flask, render_template, jsonify, request
import feedparser
import requests
from datetime import datetime
import os
from openai import OpenAI
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus .env Datei
load_dotenv()

app = Flask(__name__)

# =============================================================================
# OpenAI Konfiguration
# =============================================================================

# OpenAI Client initialisieren
client = None
if os.getenv("OPENAI_API_KEY"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Cache für KI-generierte Erkenntnisse (spart API-Kosten)
erkenntnisse_cache = {}

# =============================================================================
# Copernicus Datenquellen
# =============================================================================

# RSS-Feed URLs für Copernicus Climate Data Store
COPERNICUS_FEEDS = {
    "climate": "https://climate.copernicus.eu/feed",
    "atmosphere": "https://atmosphere.copernicus.eu/feed",
}

# Beispieldaten für das Dashboard (falls API nicht verfügbar)
BEISPIEL_VEROEFFENTLICHUNGEN = [
    {
        "titel": "Global Climate Highlights 2024",
        "datum": "2024-12-01",
        "beschreibung": "Die globalen Temperaturen erreichten 2024 neue Rekordwerte. Der Bericht zeigt die wichtigsten Klimatrends des Jahres.",
        "kategorie": "Jahresbericht",
        "link": "https://climate.copernicus.eu/global-climate-highlights-2024"
    },
    {
        "titel": "European State of the Climate 2024",
        "datum": "2024-11-15",
        "beschreibung": "Analyse der Klimaveränderungen in Europa mit Fokus auf Extremwetterereignisse und Temperaturanomalien.",
        "kategorie": "Europa",
        "link": "https://climate.copernicus.eu/esotc"
    },
    {
        "titel": "Monthly Climate Bulletin - November 2024",
        "datum": "2024-11-10",
        "beschreibung": "Monatliche Übersicht der globalen Temperatur- und Niederschlagsanomalien.",
        "kategorie": "Monatsbericht",
        "link": "https://climate.copernicus.eu/climate-bulletins"
    },
    {
        "titel": "Ocean Heat Content Analysis",
        "datum": "2024-11-05",
        "beschreibung": "Neue Daten zeigen kontinuierliche Erwärmung der Ozeane mit Rekordwerten in den oberen 2000 Metern.",
        "kategorie": "Ozean",
        "link": "https://climate.copernicus.eu/ocean"
    },
    {
        "titel": "Arctic Sea Ice Minimum 2024",
        "datum": "2024-10-20",
        "beschreibung": "Das arktische Meereis erreichte im September 2024 sein jährliches Minimum - eine detaillierte Analyse.",
        "kategorie": "Arktis",
        "link": "https://climate.copernicus.eu/sea-ice"
    },
    {
        "titel": "Drought Indicators for Europe",
        "datum": "2024-10-15",
        "beschreibung": "Aktuelle Dürre-Indikatoren und Bodenfeuchte-Analysen für den europäischen Kontinent.",
        "kategorie": "Dürre",
        "link": "https://climate.copernicus.eu/drought"
    }
]

# Wissensbasis für den Suchagenten
KLIMAWISSEN = {
    "temperatur": """
    🌡️ **Globale Temperatur**
    
    Laut Copernicus Climate Change Service (C3S):
    - Die globale Durchschnittstemperatur ist seit der vorindustriellen Zeit um etwa 1,2°C gestiegen
    - 2023 war das wärmste Jahr seit Beginn der Aufzeichnungen
    - Die letzten 8 Jahre waren die 8 wärmsten jemals gemessenen
    - Europa erwärmt sich doppelt so schnell wie der globale Durchschnitt
    """,
    
    "meereis": """
    🧊 **Arktisches Meereis**
    
    Copernicus-Daten zeigen:
    - Das arktische Meereis nimmt pro Jahrzehnt um etwa 13% ab
    - Das September-Minimum 2024 gehörte zu den niedrigsten je gemessenen
    - Die Eisdicke hat sich seit 1979 fast halbiert
    - Prognosen deuten auf eisfreie Sommer in der Arktis bis 2050 hin
    """,
    
    "ozean": """
    🌊 **Ozeanerwärmung**
    
    Aktuelle Erkenntnisse:
    - Die Ozeane absorbieren etwa 90% der zusätzlichen Wärme
    - Rekord-Ozeantemperaturen wurden 2023 und 2024 gemessen
    - Der Meeresspiegel steigt um etwa 3,7 mm pro Jahr
    - Marine Hitzewellen nehmen in Häufigkeit und Intensität zu
    """,
    
    "extremwetter": """
    ⛈️ **Extremwetter**
    
    Copernicus-Analysen zeigen:
    - Hitzewellen werden häufiger und intensiver
    - Starkniederschläge nehmen in vielen Regionen zu
    - Dürreperioden werden in Südeuropa länger
    - Der Zusammenhang zwischen Klimawandel und Extremereignissen wird stärker
    """,
    
    "copernicus": """
    🛰️ **Was ist Copernicus?**
    
    - Das Copernicus-Programm ist das Erdbeobachtungsprogramm der EU
    - Der Climate Change Service (C3S) liefert Klimadaten und -analysen
    - Daten sind kostenlos und öffentlich zugänglich
    - Kombiniert Satellitendaten mit Bodenmessungen und Klimamodellen
    - Website: climate.copernicus.eu
    """,
    
    "co2": """
    💨 **CO2 und Treibhausgase**
    
    Laut Copernicus Atmosphere Monitoring Service:
    - Die CO2-Konzentration liegt aktuell bei über 420 ppm
    - Das ist der höchste Wert seit mindestens 800.000 Jahren
    - Methan (CH4) und Lachgas (N2O) steigen ebenfalls
    - Jährlicher Anstieg: etwa 2-3 ppm CO2
    """
}

# =============================================================================
# Wissensbasis für interaktive Grafiken
# =============================================================================

GRAFIK_WISSEN = {
    "temperatur": {
        "warum": """
        🌡️ **Warum steigt die Temperatur?**
        
        Die Hauptursache ist der **Treibhauseffekt**, verstärkt durch menschliche Aktivitäten:
        
        1. **Verbrennung fossiler Brennstoffe** (Kohle, Öl, Gas) - setzt CO₂ frei
        2. **Abholzung von Wäldern** - weniger CO₂-Aufnahme
        3. **Landwirtschaft** - Methan von Rindern, Lachgas aus Düngemitteln
        4. **Industrie** - verschiedene Treibhausgase
        
        Diese Gase bilden eine "Decke" um die Erde und halten Wärme zurück.
        """,
        
        "bedeutung": """
        📊 **Was bedeutet 1.2°C Erwärmung?**
        
        Das klingt wenig, hat aber **massive Auswirkungen**:
        
        - 🌊 **Meeresspiegel**: Steigt um mehrere Meter bei 1.5-2°C
        - 🌪️ **Extremwetter**: Hitzewellen, Stürme, Fluten werden häufiger
        - 🧊 **Gletscher/Eis**: Schmelzen beschleunigt sich exponentiell
        - 🌾 **Landwirtschaft**: Ernteverluste, Dürren in vielen Regionen
        - 🐠 **Ökosysteme**: Korallensterben, Artensterben
        
        1.5°C ist die kritische Grenze laut Pariser Abkommen!
        """,
        
        "2023": """
        🔥 **Was war 2023 besonders?**
        
        2023 war das **wärmste Jahr seit Aufzeichnungsbeginn** (über 174 Jahre!):
        
        - Durchschnittlich **1.48°C** über dem vorindustriellen Niveau
        - **El Niño** verstärkte die Erwärmung zusätzlich
        - Jeden Monat wurden neue Rekorde gebrochen
        - Die 1.5°C-Grenze wurde erstmals überschritten
        - Marine Hitzewellen erreichten neue Extreme
        
        2024 wird voraussichtlich noch wärmer!
        """,
        
        "europa": """
        🇪🇺 **Wie schnell erwärmt sich Europa?**
        
        Europa ist der sich am schnellsten erwärmende Kontinent:
        
        - **2x schneller** als der globale Durchschnitt
        - Etwa **+2.3°C** seit der vorindustriellen Zeit
        - Sommer 2022 war der heißeste je gemessene
        - Alpengletscher haben 10% ihrer Masse verloren (2022)
        - Hitzewellen werden 3-4x häufiger
        
        Gründe: Geografische Lage, Windmuster, weniger ozeanische Pufferung.
        """,
        
        "folgen": """
        ⚠️ **Was sind die Folgen?**
        
        Die Auswirkungen sind bereits spürbar:
        
        **Gesundheit:**
        - Mehr Hitzetote (2022: 60.000+ in Europa)
        - Ausbreitung tropischer Krankheiten
        
        **Wirtschaft:**
        - Milliardenschäden durch Extremwetter
        - Ernteverluste, Wassermangel
        
        **Natur:**
        - Waldbrände nehmen zu
        - Arten wandern polwärts oder sterben aus
        - Korallenriffe bleichen aus
        
        **Gesellschaft:**
        - Klimamigration nimmt zu
        - Konflikte um Ressourcen
        """
    },
    
    "co2": {
        "warum": """
        💨 **Warum steigt CO₂?**
        
        Der CO₂-Anstieg hat klare **menschliche Ursachen**:
        
        1. **Fossile Brennstoffe** (ca. 75%)
           - Kohle, Öl, Gas für Energie und Transport
        
        2. **Landnutzungsänderung** (ca. 25%)
           - Abholzung von Wäldern
           - Trockenlegung von Mooren
        
        3. **Industrie**
           - Zement-, Stahl-, Chemieproduktion
        
        Vor der Industrialisierung: 280 ppm
        Heute: über 420 ppm (+50%!)
        """,
        
        "bedeutung": """
        📊 **Was bedeutet 420 ppm?**
        
        **ppm** = parts per million (Teile pro Million)
        
        - 420 ppm bedeutet: 420 CO₂-Moleküle pro 1 Million Luftmoleküle
        - Das klingt wenig, aber die Wirkung ist enorm!
        
        **Zum Vergleich:**
        - Vor 800.000 Jahren: nie über 300 ppm
        - Vor der Industrie (1850): 280 ppm
        - 1960: 317 ppm
        - Heute: 420+ ppm
        
        Dieser Anstieg in 170 Jahren ist **geologisch beispiellos schnell**!
        """,
        
        "verweildauer": """
        ⏰ **Wie lange bleibt CO₂ in der Luft?**
        
        CO₂ ist **extrem langlebig**:
        
        - Nach 100 Jahren: noch **40%** in der Atmosphäre
        - Nach 1000 Jahren: noch **20%**
        - Vollständiger Abbau: **10.000+ Jahre**
        
        Das bedeutet:
        - Jede Emission hat langfristige Folgen
        - Selbst bei Stopp aller Emissionen würde die Erwärmung anhalten
        - Früh handeln ist besser als spät!
        
        Vergleich: Methan bleibt nur ~12 Jahre, ist aber 80x stärker.
        """,
        
        "vorindustriell": """
        🏛️ **Was war vor der Industrie?**
        
        **Vor 1850 (vorindustrielle Zeit):**
        
        - CO₂-Konzentration: etwa **280 ppm**
        - Stabil seit ca. 10.000 Jahren
        - Natürliches Gleichgewicht zwischen Aufnahme und Abgabe
        
        **Der natürliche Kohlenstoffkreislauf:**
        - Pflanzen nehmen CO₂ auf (Photosynthese)
        - Verrottung/Atmung gibt CO₂ ab
        - Ozeane absorbieren und geben CO₂ ab
        
        Dieses Gleichgewicht haben wir durch fossile Brennstoffe gestört!
        """,
        
        "quellen": """
        🏭 **Was sind die Hauptquellen?**
        
        **Globale CO₂-Emissionen nach Sektor:**
        
        1. **Energie & Strom** (25%)
           - Kohlekraftwerke, Gaskraftwerke
        
        2. **Industrie** (21%)
           - Stahl, Zement, Chemie
        
        3. **Transport** (16%)
           - Autos, Flugzeuge, Schiffe
        
        4. **Gebäude** (18%)
           - Heizen, Kühlen
        
        5. **Landwirtschaft** (20%)
           - Abholzung, Viehzucht
        
        **Nach Land:** China (30%), USA (14%), EU (8%), Indien (7%)
        """
    }
}

def grafik_antwort(frage, grafik_typ):
    """
    Beantwortet Fragen zu den Grafik-Daten.
    """
    frage_lower = frage.lower()
    wissen = GRAFIK_WISSEN.get(grafik_typ, {})
    
    # Keyword-Mapping für Temperatur-Grafik
    if grafik_typ == "temperatur":
        keyword_mapping = {
            "warum": ["warum", "ursache", "grund", "wieso", "weshalb", "steigt"],
            "bedeutung": ["bedeut", "1.2", "1,2", "auswirk", "schlimm", "wichtig"],
            "2023": ["2023", "letzt", "aktuell", "rekord", "besonder"],
            "europa": ["europa", "deutschland", "eu", "kontinent", "schnell"],
            "folgen": ["folge", "auswirk", "passier", "zukunft", "konsequenz"]
        }
    else:  # CO2
        keyword_mapping = {
            "warum": ["warum", "ursache", "grund", "wieso", "steigt"],
            "bedeutung": ["bedeut", "420", "ppm", "viel", "hoch"],
            "verweildauer": ["lang", "bleibt", "abbau", "zeit", "luft", "atmosphäre"],
            "vorindustriell": ["vor", "früher", "industrie", "history", "280"],
            "quellen": ["quell", "woher", "emiss", "sektor", "land", "haupt"]
        }
    
    # Suche nach passenden Antworten
    for thema, keywords in keyword_mapping.items():
        for keyword in keywords:
            if keyword in frage_lower:
                return wissen.get(thema, "")
    
    # Standard-Antwort wenn nichts gefunden
    if grafik_typ == "temperatur":
        return """
        🌡️ Ich kann dir bei diesen Fragen zur **Temperatur-Grafik** helfen:
        
        - **Warum** steigt die Temperatur?
        - **Was bedeutet** 1.2°C Erwärmung?
        - Was war an **2023** besonders?
        - Wie schnell erwärmt sich **Europa**?
        - Was sind die **Folgen** der Erwärmung?
        
        Stelle mir eine dieser Fragen!
        """
    else:
        return """
        💨 Ich kann dir bei diesen Fragen zur **CO₂-Grafik** helfen:
        
        - **Warum** steigt CO₂?
        - Was bedeutet **420 ppm**?
        - Wie **lange bleibt** CO₂ in der Luft?
        - Was war **vor der Industrie**?
        - Was sind die **Hauptquellen** von CO₂?
        
        Stelle mir eine dieser Fragen!
        """


def hole_veroeffentlichungen():
    """
    Holt die neuesten Veröffentlichungen von Copernicus.
    Falls der Feed nicht erreichbar ist, werden Beispieldaten verwendet.
    """
    alle_artikel = []
    
    try:
        # Versuche den RSS-Feed abzurufen
        feed = feedparser.parse(COPERNICUS_FEEDS["climate"])
        
        if feed.entries:
            for eintrag in feed.entries[:6]:
                artikel = {
                    "titel": eintrag.get("title", "Ohne Titel"),
                    "datum": eintrag.get("published", "Unbekannt"),
                    "beschreibung": eintrag.get("summary", "Keine Beschreibung verfügbar")[:200] + "...",
                    "kategorie": "Copernicus",
                    "link": eintrag.get("link", "#")
                }
                alle_artikel.append(artikel)
    except Exception as e:
        print(f"Feed-Abruf fehlgeschlagen: {e}")
    
    # Falls keine Artikel gefunden wurden, verwende Beispieldaten
    if not alle_artikel:
        alle_artikel = BEISPIEL_VEROEFFENTLICHUNGEN
    
    return alle_artikel


def suchagent_antwort(frage):
    """
    Einfacher Suchagent, der Fragen zu Klimadaten beantwortet.
    Durchsucht die Wissensbasis nach passenden Antworten.
    """
    frage_lower = frage.lower()
    
    # Schlüsselwörter zu Themen zuordnen
    themen_mapping = {
        "temperatur": ["temperatur", "warm", "heiß", "erwärmung", "hitze", "grad", "celsius"],
        "meereis": ["eis", "arktis", "antarktis", "meereis", "gletscher", "schmelz"],
        "ozean": ["ozean", "meer", "wasser", "meeresspiegel", "marine"],
        "extremwetter": ["extrem", "wetter", "sturm", "überschwemmung", "dürre", "hitzewelle", "unwetter"],
        "copernicus": ["copernicus", "was ist", "erkläre", "datenquelle", "c3s"],
        "co2": ["co2", "kohlendioxid", "treibhaus", "emission", "methan", "gas"]
    }
    
    # Suche nach passenden Themen
    gefundene_themen = []
    for thema, keywords in themen_mapping.items():
        for keyword in keywords:
            if keyword in frage_lower:
                gefundene_themen.append(thema)
                break
    
    # Antwort generieren
    if gefundene_themen:
        antworten = [KLIMAWISSEN[thema] for thema in set(gefundene_themen)]
        return "\n\n".join(antworten)
    else:
        return """
        🤔 **Ich bin nicht sicher, was du meinst.**
        
        Ich kann dir bei folgenden Themen helfen:
        - 🌡️ **Temperatur** - Globale Erwärmung und Trends
        - 🧊 **Meereis** - Arktisches und antarktisches Eis
        - 🌊 **Ozean** - Meerestemperatur und -spiegel
        - ⛈️ **Extremwetter** - Stürme, Dürren, Hitzewellen
        - 💨 **CO2** - Treibhausgase und Emissionen
        - 🛰️ **Copernicus** - Was ist der Copernicus-Dienst?
        
        Stelle mir gerne eine Frage zu einem dieser Themen!
        """


# =============================================================================
# Web-Routen
# =============================================================================

@app.route("/")
def startseite():
    """Zeigt das Haupt-Dashboard an."""
    return render_template("index.html")


@app.route("/api/veroeffentlichungen")
def api_veroeffentlichungen():
    """API-Endpunkt für die neuesten Veröffentlichungen."""
    artikel = hole_veroeffentlichungen()
    return jsonify(artikel)


@app.route("/api/frage", methods=["POST"])
def api_frage():
    """API-Endpunkt für den Suchagenten."""
    daten = request.get_json()
    frage = daten.get("frage", "")
    
    if not frage:
        return jsonify({"antwort": "Bitte stelle eine Frage!"})
    
    antwort = suchagent_antwort(frage)
    return jsonify({"antwort": antwort})


@app.route("/api/grafik-frage", methods=["POST"])
def api_grafik_frage():
    """API-Endpunkt für Fragen zu den interaktiven Grafiken."""
    daten = request.get_json()
    frage = daten.get("frage", "")
    grafik = daten.get("grafik", "")
    
    if not frage:
        return jsonify({"antwort": "Bitte stelle eine Frage!"})
    
    if not grafik:
        return jsonify({"antwort": "Bitte wähle zuerst eine Grafik aus!"})
    
    antwort = grafik_antwort(frage, grafik)
    return jsonify({"antwort": antwort})


@app.route("/api/erkenntnisse", methods=["POST"])
def api_erkenntnisse():
    """
    API-Endpunkt für KI-generierte Erkenntnisse aus Veröffentlichungen.
    Nutzt GPT-5.1 um journalistische Recherche-Ansätze zu generieren.
    """
    daten = request.get_json()
    titel = daten.get("titel", "")
    beschreibung = daten.get("beschreibung", "")
    link = daten.get("link", "")
    kategorie = daten.get("kategorie", "")
    
    if not titel:
        return jsonify({"error": "Kein Titel angegeben", "erkenntnisse": []})
    
    # Prüfe ob OpenAI konfiguriert ist
    if not client:
        return jsonify({
            "error": "OpenAI API-Key nicht konfiguriert",
            "erkenntnisse": [
                "⚠️ Bitte konfiguriere deinen OpenAI API-Key in der .env Datei",
                "1. Erstelle eine Datei namens '.env' im Projektordner",
                "2. Füge diese Zeile hinzu: OPENAI_API_KEY=dein-api-key-hier",
                "3. Starte die App neu"
            ],
            "hinweis": "Besuche https://platform.openai.com um einen API-Key zu erstellen"
        })
    
    # Prüfe Cache
    cache_key = titel.lower().strip()
    if cache_key in erkenntnisse_cache:
        return jsonify(erkenntnisse_cache[cache_key])
    
    # Prompt für GPT-5.1
    prompt = f"""Du bist ein Experte für Klimajournalismus und analysierst Veröffentlichungen des Copernicus Climate Data Store.

Analysiere diese Veröffentlichung und erstelle Erkenntnisse für Journalist:innen:

**Titel:** {titel}
**Kategorie:** {kategorie}
**Beschreibung:** {beschreibung}
**Quelle:** {link}

Erstelle genau 5 Bullet Points mit den überraschendsten und wichtigsten Erkenntnissen.
Jeder Punkt sollte ein konkreter Recherche-Ansatz für Journalist:innen sein.

Format für jeden Punkt:
- Beginne mit einem passenden Emoji
- Formuliere eine überraschende Erkenntnis oder einen Recherche-Ansatz
- Sei konkret und nenne Zahlen/Fakten wenn möglich
- Zeige den journalistischen Wert (lokaler Bezug, menschliche Geschichten, Kontraste)

Antworte NUR mit den 5 Bullet Points, ohne Einleitung oder Abschluss.
Schreibe auf Deutsch."""

    try:
        # OpenAI API Aufruf mit GPT-5.1
        response = client.chat.completions.create(
            model="gpt-5.1",  # GPT-5.1 (neuestes Modell)
            messages=[
                {
                    "role": "system",
                    "content": "Du bist ein erfahrener Klimajournalist und Datenanalyst. Du findest die überraschendsten und wichtigsten Erkenntnisse in Klimaberichten und formulierst sie als Recherche-Ansätze für Journalist:innen."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_completion_tokens=1000  # GPT-5.1 verwendet diesen Parameter
        )
        
        # Antwort parsen
        antwort_text = response.choices[0].message.content
        
        # Bullet Points extrahieren (nach Zeilen mit - oder • aufteilen)
        zeilen = antwort_text.strip().split('\n')
        erkenntnisse = []
        
        for zeile in zeilen:
            zeile = zeile.strip()
            if zeile and (zeile.startswith('-') or zeile.startswith('•') or zeile.startswith('*')):
                # Entferne führende Zeichen
                erkenntniss = zeile.lstrip('-•* ').strip()
                if erkenntniss:
                    erkenntnisse.append(erkenntniss)
        
        # Falls keine Bullet Points gefunden, nimm die ganze Antwort
        if not erkenntnisse:
            erkenntnisse = [antwort_text]
        
        result = {
            "titel": titel,
            "erkenntnisse": erkenntnisse[:5],  # Maximal 5
            "quelle": link,
            "generiert_von": "GPT-5.1"
        }
        
        # In Cache speichern
        erkenntnisse_cache[cache_key] = result
        
        return jsonify(result)
        
    except Exception as e:
        print(f"OpenAI Fehler: {e}")
        return jsonify({
            "error": f"Fehler bei der KI-Analyse: {str(e)}",
            "erkenntnisse": [
                "⚠️ Die KI-Analyse konnte nicht durchgeführt werden.",
                f"Fehler: {str(e)}",
                "Bitte überprüfe deinen API-Key und versuche es erneut."
            ]
        })


@app.route("/api/oesterreich-recherche", methods=["POST"])
def api_oesterreich_recherche():
    """
    API-Endpunkt für österreich-spezifische Recherche zu einem Vorschlag.
    Generiert konkrete Fälle und Beispiele aus Österreich.
    """
    daten = request.get_json()
    vorschlag = daten.get("vorschlag", "")
    titel = daten.get("titel", "")
    
    if not vorschlag:
        return jsonify({"error": "Kein Vorschlag angegeben", "recherche": []})
    
    # Prüfe ob OpenAI konfiguriert ist
    if not client:
        return jsonify({
            "error": "OpenAI API-Key nicht konfiguriert",
            "recherche": []
        })
    
    # Prompt für österreich-spezifische Recherche
    prompt = f"""Du bist ein Experte für österreichischen Klimajournalismus.

**Recherche-Vorschlag:** {vorschlag}
**Aus Veröffentlichung:** {titel}

Erstelle GENAU 3 konkrete österreichische Fallbeispiele/Recherche-Ansätze zu diesem Vorschlag.

Jeder der 3 Punkte muss enthalten:
- **Konkreter Ort/Region in Österreich** (z.B. Wien, Tirol, Steiermark, Salzburg, etc.)
- **Spezifisches Beispiel/Fall** (konkrete Ereignisse, Projekte, Situationen)
- **Recherche-Ansatz** (was sollte ein Journalist recherchieren, wen kontaktieren)

Format für jeden der 3 Punkte:
**1. [Ort/Region] - [Kurzer Titel]**
- Konkrete Situation/Beispiel: [Beschreibung]
- Recherche-Ansatz: [Was recherchieren, welche Institutionen/Personen kontaktieren]

**2. [Ort/Region] - [Kurzer Titel]**
- Konkrete Situation/Beispiel: [Beschreibung]
- Recherche-Ansatz: [Was recherchieren, welche Institutionen/Personen kontaktieren]

**3. [Ort/Region] - [Kurzer Titel]**
- Konkrete Situation/Beispiel: [Beschreibung]
- Recherche-Ansatz: [Was recherchieren, welche Institutionen/Personen kontaktieren]

WICHTIG:
- Sei sehr konkret mit echten österreichischen Orten, Institutionen und Fällen
- Jeder Punkt muss einen konkreten Recherche-Ansatz für Journalist:innen enthalten
- Nenne spezifische österreichische Institutionen, Behörden oder Experten wenn möglich
- Schreibe auf Deutsch"""

    try:
        # OpenAI API Aufruf mit GPT-5.1
        response = client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {
                    "role": "system",
                    "content": "Du bist ein erfahrener österreichischer Klimajournalist mit tiefem Wissen über lokale Gegebenheiten, Institutionen und konkrete Fälle in Österreich."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            max_completion_tokens=1500  # Mehr Tokens für detaillierte Recherche
        )
        
        # Antwort zurückgeben
        antwort_text = response.choices[0].message.content
        
        return jsonify({
            "vorschlag": vorschlag,
            "recherche": antwort_text,
            "generiert_von": "GPT-5.1"
        })
        
    except Exception as e:
        print(f"OpenAI Fehler (Österreich-Recherche): {e}")
        return jsonify({
            "error": f"Fehler bei der Recherche: {str(e)}",
            "recherche": f"Die österreich-spezifische Recherche konnte nicht durchgeführt werden: {str(e)}"
        })


# =============================================================================
# App starten
# =============================================================================

if __name__ == "__main__":
    print("🌍 Copernicus Climate Dashboard startet...")
    print("📊 Öffne http://localhost:5000 in deinem Browser")
    app.run(debug=True, port=5000)

