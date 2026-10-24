import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import sqlite3
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# --- CONFIGURAZIONE HUD SOVEREIGN ZERO ---
st.set_page_config(
    page_title="CISOM Grosseto - Sovereign Zero Control Tower", 
    page_icon="🚑", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- CONFIGURAZIONE SMTP PER LE NOTIFICHE EMAIL ---
APP_URL = "https://sovereign-cisom-tower-bemask.streamlit.app"

try:
    SMTP_SERVER = st.secrets.get("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(st.secrets.get("SMTP_PORT", 465))
    SMTP_USER = st.secrets.get("SMTP_USER", "")
    SMTP_PASSWORD = st.secrets.get("SMTP_PASSWORD", "")
    EMAIL_MITTENTE = st.secrets.get("EMAIL_MITTENTE", "CISOM Sezione Grosseto <notifiche@cisom-grosseto.it>")
except Exception:
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465
    SMTP_USER = "enricobraglia1971@gmail.com"
    SMTP_PASSWORD = "xumo ykvi jorp naal"
    EMAIL_MITTENTE = "CISOM Grosseto <notifiche@cisom-grosseto.it>"

def invia_email_notifica(destinatario, oggetto, corpo_html):
    """Spedizione e-mail formale con template SMOM e diagnostica trasparente."""
    destinatario = str(destinatario).strip()
    if not destinatario or "@" not in destinatario:
        return False, "Indirizzo e-mail non valido o assente."
    if not SMTP_USER or not SMTP_PASSWORD:
        return False, "Credenziali SMTP mancanti."

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = oggetto
        msg["From"] = EMAIL_MITTENTE
        msg["To"] = destinatario
        msg.attach(MIMEText(corpo_html, "html"))

        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_USER, destinatario, msg.as_string())
        else:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_USER, destinatario, msg.as_string())
        return True, f"E-mail recapitata correttamente a {destinatario}."
    except Exception as e:
        return False, f"Errore SMTP: {str(e)}"

# --- CSS ARCHITETTURA GRAFICA DARK HUD (SOVEREIGN ZERO) ---
st.markdown("""
<style>
.stApp {
    background-color: #050505;
    color: #E0E0E0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
.event-card {
    background-color: #0d1117;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 24px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.7);
}
.card-header-flex {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 12px;
    border-bottom: 1px solid #21262d;
    padding-bottom: 12px;
    margin-bottom: 14px;
}
.event-title-text {
    font-size: 26px;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.5px;
    margin: 0;
    text-transform: uppercase;
}
.event-time-badge {
    background-color: #1e293b;
    border: 1.5px solid #3b82f6;
    border-radius: 8px;
    padding: 8px 16px;
    text-align: right;
}
.event-date-large {
    font-size: 18px;
    font-weight: 800;
    color: #93c5fd;
    letter-spacing: 0.5px;
}
.event-hours-sub {
    font-size: 13px;
    font-weight: 600;
    color: #cbd5e1;
}
.meteo-box-hud {
    background: linear-gradient(180deg, #111827 0%, #0b0f17 100%);
    border: 1.5px solid #1f293d;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}
.meteo-location-title {
    font-size: 14px;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: 0.5px;
}
.meteo-metrics-group {
    display: flex;
    gap: 16px;
    align-items: center;
    flex-wrap: wrap;
}
.meteo-metric-item {
    background: #182234;
    border: 1px solid #2c3a54;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
    font-weight: 700;
    color: #e2e8f0;
}
.timeline-container {
    display: flex;
    flex-direction: row;
    gap: 8px;
    margin-top: 10px;
    margin-bottom: 8px;
    overflow-x: auto;
    padding-bottom: 8px;
}
.time-slot {
    flex: 1;
    min-width: 115px;
    padding: 12px 8px;
    border-radius: 6px;
    text-align: center;
    font-size: 11px;
    font-weight: 700;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 100px;
}
.slot-red {
    background-color: rgba(220, 38, 38, 0.22);
    border: 1.5px solid #ef4444;
    color: #fca5a5;
}
.slot-yellow {
    background-color: rgba(217, 119, 6, 0.22);
    border: 1.5px solid #f59e0b;
    color: #fde68a;
}
.slot-green {
    background-color: rgba(16, 185, 129, 0.22);
    border: 1.5px solid #10b981;
    color: #6ee7b7;
}
.slot-blue {
    background-color: rgba(37, 99, 235, 0.25);
    border: 1.5px solid #3b82f6;
    color: #93c5fd;
    box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
}
.alert-banner-yellow {
    background-color: rgba(217, 119, 6, 0.15);
    border-left: 4px solid #f59e0b;
    padding: 10px 14px;
    border-radius: 4px;
    color: #fde68a;
    font-weight: 700;
    font-size: 13px;
    margin-bottom: 12px;
}
.badge-name {
    background-color: #1f2937;
    border: 1px solid #374151;
    border-radius: 4px;
    padding: 3px 6px;
    margin-top: 4px;
    font-size: 11px;
    color: #ffffff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.badge-da-concordare {
    background-color: rgba(147, 51, 234, 0.2);
    border: 1px dashed #a855f7;
    border-radius: 6px;
    padding: 8px 12px;
    margin-top: 10px;
    font-size: 12px;
    color: #d8b4fe;
}
.year-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
    gap: 12px;
    margin-top: 15px;
}
.month-tile {
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 10px;
    min-height: 155px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}
.month-active {
    border-color: #3b82f6;
    background: rgba(59, 130, 246, 0.05);
    box-shadow: 0 0 12px rgba(59, 130, 246, 0.15);
}
.month-title {
    font-size: 12px;
    font-weight: 700;
    color: #9ca3af;
    letter-spacing: 1px;
}
.event-micro-badge {
    background-color: #161b22;
    border-radius: 4px;
    padding: 4px 6px;
    margin-top: 5px;
    font-size: 10px;
    color: #e2e8f0;
    text-align: left;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    border-left: 3px solid #3b82f6;
}
</style>
""", unsafe_allow_html=True)

# --- ARCHITETTURA GERARCHICA SMOM / CISOM ---
STRUTTURA_ISTITUZIONALE_SMOM_CISOM = {
    "1. Componente Sacerdotale & Assistenza Spirituale": [
        "Cardinale Patrono / Prelato dell'Ordine",
        "Priore Spirituale / Gran Croce Conventuale",
        "Cappellano Capo",
        "Cappellano Conventuale ad Honorem",
        "Cappellano Magistrale",
        "Cappellano di Sezione / Correttore Spirituale CISOM",
        "Assistente Ecclesiastico"
    ],
    "2. Ceto Magistrale, Nobiliare & Dignitari SMOM": [
        "Gran Maestro / Membro del Sovrano Consiglio",
        "Ambasciatore / Dignitario Diplomatico",
        "Cavaliere di Giustizia (Professo)",
        "Cavaliere in Obbedienza",
        "Cavaliere di Gran Croce di Giustizia / Onore e Devozione",
        "Cavaliere / Dama di Onore e Devozione",
        "Cavaliere / Dama di Grazia e Devozione",
        "Cavaliere / Dama Magistrale",
        "Donato / Donata di Devozione"
    ],
    "3. Catena di Comando & Vertici Operativi CISOM": [
        "Presidente Nazionale CISOM",
        "Direttore Nazionale CISOM",
        "Capo Raggruppamento Regionale",
        "Capo Gruppo Territoriale / Capo Sezione",
        "Vice Capo Gruppo / Segretario Operativo",
        "Caposquadra Operativo (CS)",
        "Coordinatore Logistica & Parco Mezzi",
        "Responsabile Sanitario di Sezione"
    ],
    "4. Corpo Operativo, Sanitario & Protezione Civile": [
        "Ufficiale Medico / Medico di Sezione",
        "Infermiere Professionale Volontario",
        "Autista Soccorritore Mezzi di Emergenza (118 / Sanità)",
        "Soccorritore Avanzato Abilitato BLS-D / PBLS-D / PTC",
        "Operatore Logistico Protezione Civile & Colonna Mobile",
        "Operatore Antincendio Boschivo (AIB - Alto Rischio)",
        "Operatore Telecomunicazioni & Sala Radio TLC",
        "Operatore Cinofilo da Soccorso",
        "Volontario Effettivo di Soccorso",
        "Volontario Aspirante (Periodo di Tirocinio)"
    ]
}

# --- RETE NAZIONALE ---
RETE_ISTITUZIONALE_CISOM = [
    {"nome": "Roma (Sede Nazionale SMOM/CISOM)", "tipo": "Direzione Nazionale", "lat": 41.8942, "lon": 12.4870, "livello": "Nazionale"},
    {"nome": "Roma (Hub Logistico Colonna Mobile DPC)", "tipo": "Logistica Emergenza", "lat": 41.8385, "lon": 12.4674, "livello": "Nazionale"},
    {"nome": "Firenze (Raggruppamento Regionale Toscana)", "tipo": "Raggruppamento Regionale", "lat": 43.7696, "lon": 11.2558, "livello": "Regionale"},
    {"nome": "Grosseto (Sede di Sezione Provinciale)", "tipo": "Sezione Territoriale", "lat": 42.7634, "lon": 11.1118, "livello": "Sezione"},
    {"nome": "Siena (Sezione Territoriale)", "tipo": "Sezione Territoriale", "lat": 43.3188, "lon": 11.3308, "livello": "Sezione"},
    {"nome": "Pisa (Sezione Territoriale)", "tipo": "Sezione Territoriale", "lat": 43.7228, "lon": 10.4017, "livello": "Sezione"},
    {"nome": "Livorno (Sezione Territoriale / Costiera)", "tipo": "Sezione Territoriale", "lat": 43.5485, "lon": 10.3106, "livello": "Sezione"},
    {"nome": "Lucca - Versilia (Sezione Territoriale)", "tipo": "Sezione Territoriale", "lat": 43.8429, "lon": 10.5027, "livello": "Sezione"},
    {"nome": "Arezzo (Sezione Territoriale)", "tipo": "Sezione Territoriale", "lat": 43.4631, "lon": 11.8781, "livello": "Sezione"},
    {"nome": "Milano (Raggruppamento Lombardia)", "tipo": "Raggruppamento Regionale", "lat": 45.4642, "lon": 9.1900, "livello": "Nazionale"},
    {"nome": "Torino (Raggruppamento Piemonte)", "tipo": "Raggruppamento Regionale", "lat": 45.0703, "lon": 7.6869, "livello": "Nazionale"},
    {"nome": "Genova (Raggruppamento Liguria)", "tipo": "Raggruppamento Regionale", "lat": 44.4056, "lon": 8.9463, "livello": "Nazionale"},
    {"nome": "Bologna (Raggruppamento Emilia-Romagna)", "tipo": "Raggruppamento Regionale", "lat": 44.4949, "lon": 11.3426, "livello": "Nazionale"},
    {"nome": "Venezia - Padova (Raggruppamento Veneto)", "tipo": "Raggruppamento Regionale", "lat": 45.4064, "lon": 11.8768, "livello": "Nazionale"},
    {"nome": "Napoli (Raggruppamento Campania)", "tipo": "Raggruppamento Regionale", "lat": 40.8518, "lon": 14.2681, "livello": "Nazionale"},
    {"nome": "Bari (Raggruppamento Puglia)", "tipo": "Raggruppamento Regionale", "lat": 41.1171, "lon": 16.8719, "livello": "Nazionale"},
    {"nome": "Palermo (Raggruppamento Sicilia)", "tipo": "Raggruppamento Regionale", "lat": 38.1157, "lon": 13.3615, "livello": "Nazionale"},
    {"nome": "Lampedusa (Presidio Sanitario SAR)", "tipo": "Polo Soccorso Marittimo", "lat": 35.5005, "lon": 12.6074, "livello": "Nazionale"},
    {"nome": "Cagliari (Raggruppamento Sardegna)", "tipo": "Raggruppamento Regionale", "lat": 39.2238, "lon": 9.1217, "livello": "Nazionale"},
]

COMUNI_TEATRO_OPERATIVO = {
    "Grosseto": {"lat": 42.7634, "lon": 11.1118},
    "Follonica": {"lat": 42.9252, "lon": 10.7608},
    "Castiglione della Pescaia": {"lat": 42.7645, "lon": 10.8808},
    "Massa Marittima": {"lat": 43.0504, "lon": 10.8911},
    "Scarlino": {"lat": 42.9078, "lon": 10.8523},
    "Gavorrano": {"lat": 42.9248, "lon": 10.9083},
    "Roccastrada": {"lat": 43.0101, "lon": 11.1685},
    "Orbetello / Albinia": {"lat": 42.4408, "lon": 11.2185},
    "Monte Argentario": {"lat": 42.4357, "lon": 11.1205},
    "Isola del Giglio": {"lat": 42.3614, "lon": 10.9015},
    "Capalbio": {"lat": 42.4542, "lon": 11.4216},
    "Manciano / Saturnia": {"lat": 42.5878, "lon": 11.5175},
    "Pitigliano": {"lat": 42.6346, "lon": 11.6664},
    "Sorano": {"lat": 42.6821, "lon": 11.7144},
    "Magliano in Toscana": {"lat": 42.5989, "lon": 11.2936},
    "Scansano": {"lat": 42.6892, "lon": 11.3344},
    "Campagnatico": {"lat": 42.8841, "lon": 11.2747},
    "Civitella Paganico": {"lat": 42.9961, "lon": 11.2828},
    "Castel del Piano (Amiata)": {"lat": 42.8924, "lon": 11.5367},
    "Arcidosso (Amiata)": {"lat": 42.8719, "lon": 11.5385},
    "Santa Fiora": {"lat": 42.8317, "lon": 11.5847},
    "Castell'Azzara": {"lat": 42.7725, "lon": 11.7089},
}

# --- ENGINE DATABASE ---
def run_query(query, params=(), fetch=True):
    conn = sqlite3.connect("cisom_turni.db", timeout=10)
    if fetch:
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    else:
        c = conn.cursor()
        c.execute(query, params)
        conn.commit()
        conn.close()

def init_db():
    conn = sqlite3.connect("cisom_turni.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS volontari (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    email TEXT DEFAULT '',
                    macroarea TEXT DEFAULT '4. Corpo Operativo, Sanitario & Protezione Civile',
                    ruolo TEXT,
                    attivo INTEGER DEFAULT 1)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS servizi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titolo TEXT,
                    luogo TEXT DEFAULT 'Grosseto',
                    data TEXT,
                    ora_inizio TEXT,
                    ora_fine TEXT,
                    posti_richiesti INTEGER,
                    ore_servizio REAL,
                    pausa_minuti INTEGER DEFAULT 0,
                    stato TEXT DEFAULT 'Programmato',
                    dotazioni TEXT DEFAULT '',
                    note_servizio TEXT DEFAULT '',
                    tenant_id TEXT DEFAULT 'GR_01')''')
                    
    c.execute('''CREATE TABLE IF NOT EXISTS adesioni (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    servizio_id INTEGER,
                    volontario_id INTEGER,
                    stato TEXT,
                    modalita TEXT DEFAULT 'Completo',
                    ora_inizio_disp TEXT DEFAULT '',
                    ora_fine_disp TEXT DEFAULT '',
                    note TEXT DEFAULT '',
                    ore_effettive REAL,
                    validato INTEGER DEFAULT 0,
                    pronto_impiego INTEGER DEFAULT 0)''')

    c.execute('''CREATE TABLE IF NOT EXISTS presidi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sezione TEXT DEFAULT 'CISOM Sezione Grosseto',
        nome_presidio TEXT UNIQUE NOT NULL,
        latitudine REAL NOT NULL,
        longitudine REAL NOT NULL,
        attivo INTEGER DEFAULT 1)''')

    c.execute("SELECT COUNT(*) FROM presidi")
    if c.fetchone()[0] == 0:
        dati_iniziali = [
            ("CISOM Sezione Grosseto", "Grosseto (Sede)", 42.7634, 11.1118),
            ("CISOM Sezione Grosseto", "Follonica (Distaccamento Costiero)", 42.9252, 10.7608),
            ("CISOM Sezione Grosseto", "Massa Marittima", 43.0504, 10.8911),
            ("CISOM Sezione Grosseto", "Castiglione della Pescaia", 42.7645, 10.8808),
            ("CISOM Sezione Grosseto", "Orbetello / Albinia", 42.4408, 11.2185),
            ("CISOM Sezione Grosseto", "Monte Argentario", 42.4357, 11.1205),
            ("CISOM Sezione Grosseto", "Castel del Piano (Amiata)", 42.8924, 11.5367),
        ]
        c.executemany("INSERT OR IGNORE INTO presidi (sezione, nome_presidio, latitudine, longitudine) VALUES (?, ?, ?, ?)", dati_iniziali)
    conn.commit()
    conn.close()

init_db()

# Migrazioni automatiche di sicurezza
for alter_sql in [
    "ALTER TABLE servizi ADD COLUMN dotazioni TEXT DEFAULT ''",
    "ALTER TABLE servizi ADD COLUMN note_servizio TEXT DEFAULT ''",
    "ALTER TABLE servizi ADD COLUMN tenant_id TEXT DEFAULT 'GR_01'",
    "ALTER TABLE adesioni ADD COLUMN pronto_impiego INTEGER DEFAULT 0"
]:
    try:
        run_query(alter_sql, fetch=False)
    except Exception:
        pass

def get_coordinate_presidi():
    diz = COMUNI_TEATRO_OPERATIVO.copy()
    try:
        df_p = run_query("SELECT nome_presidio, latitudine, longitudine FROM presidi WHERE attivo = 1")
        if not df_p.empty:
            for _, row in df_p.iterrows():
                diz[row["nome_presidio"]] = {"lat": row["latitudine"], "lon": row["longitudine"]}
    except Exception:
        pass
    return diz

def get_meteo_dettagliato(luogo, data_evento_str):
    coords_dict = get_coordinate_presidi()
    coords = coords_dict.get(luogo, {"lat": 42.76, "lon": 11.11})
    try:
        data_ev = datetime.strptime(str(data_evento_str), "%Y-%m-%d").date()
        oggi = date.today()
        delta = (data_ev - oggi).days
        
        if delta < 0:
            return {"valido": False, "msg": f"⏳ Servizio completato il {data_evento_str}"}
        if delta > 7:
            return {"valido": False, "msg": f"🛰️ Previsioni numeriche attive a -7 giorni (Mancano {delta} gg)"}
        
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={coords['lat']}&longitude={coords['lon']}&"
            f"daily=temperature_2m_max,precipitation_probability_max,windgusts_10m_max&timezone=auto"
        )
        res = requests.get(url, timeout=4)
        if res.status_code == 200:
            daily = res.json().get("daily", {})
            date_list = daily.get("time", [])
            data_formatted = data_ev.strftime("%Y-%m-%d")
            
            if data_formatted in date_list:
                idx = date_list.index(data_formatted)
                p_prob = daily["precipitation_probability_max"][idx]
                v_max = daily["windgusts_10m_max"][idx]
                t_max = daily["temperature_2m_max"][idx]
                alert = bool(p_prob >= 40 or v_max >= 35)
                return {
                    "valido": True,
                    "luogo": luogo,
                    "temp": f"{t_max}°C",
                    "pioggia": f"{p_prob}%",
                    "vento": f"{v_max} km/h",
                    "allerta": alert
                }
    except Exception:
        pass
    return {"valido": False, "msg": f"📍 Presidio {luogo} | Sincronizzazione radar in corso..."}

# --- PANNELLO LATERALE ---
st.sidebar.title("🚑 CISOM GROSSETO")
st.sidebar.caption("Sovereign Zero Control Tower")
ruolo_accesso = st.sidebar.radio("NAVIGAZIONE", [
    "Radar Annuale",
    "Sinottico HUD Timeline",
    "Bacheca Volontario", 
    "Consuntivo & Monte Ore", 
    "🏛️ Sala Situazioni",
    "Configurazione & Gestione"
])

# ----------------------------------------------------
# 1. RADAR ANNUALE A GRIGLIA CON PALLINI DI STATO
# ----------------------------------------------------
if ruolo_accesso == "Radar Annuale":
    st.subheader("🗓️ Tavola Sinottica Annuale")
    st.caption("Pianificazione strategica con panoramica cromatica di copertura per ciascun mese")
    
    st.markdown("""
        <div style="display:flex; gap:16px; flex-wrap:wrap; background-color:#0d1117; border:1px solid #21262d; border-radius:6px; padding:8px 12px; margin-bottom:12px; font-size:12px;">
            <span>🟢 <b>Coperto</b> (Target Raggiunto)</span>
            <span>🟡 <b>Parziale</b> (Mancano Volontari)</span>
            <span>🔴 <b>Critico</b> (0 Adesioni Registrate)</span>
            <span>🔵 <b>Bozza / Concluso</b></span>
        </div>
    """, unsafe_allow_html=True)
    
    anno_corrente = date.today().year
    anno_scelto = st.selectbox("Anno di riferimento", [anno_corrente, anno_corrente + 1], index=0)
    
    df_servizi_anno = run_query("""
        SELECT s.id, s.titolo, s.luogo, s.data, s.posti_richiesti, s.stato,
               SUBSTR(s.data, 6, 2) AS mese,
               SUBSTR(s.data, 9, 2) AS giorno,
               COUNT(a.id) AS tot_iscritti
        FROM servizi s
        LEFT JOIN adesioni a ON s.id = a.servizio_id AND a.stato = 'Confermato'
        WHERE SUBSTR(s.data, 1, 4) = ? AND s.stato NOT LIKE 'Annullato%'
        GROUP BY s.id
        ORDER BY s.data ASC
    """, (str(anno_scelto),))
    
    mesi_nomi = ["GEN", "FEB", "MAR", "APR", "MAG", "GIU", "LUG", "AGO", "SET", "OTT", "NOV", "DIC"]
    
    grid_html = '<div class="year-grid">'
    for i in range(1, 13):
        m_str = f"{i:02d}"
        ev_mese = df_servizi_anno[df_servizi_anno["mese"] == m_str]
        tot_ev = len(ev_mese)
        is_active = "month-active" if tot_ev > 0 else ""
        col_c = "#3b82f6" if tot_ev > 0 else "#4b5563"
        
        eventi_anteprima_html = ""
        if tot_ev > 0:
            for idx, r_ev in ev_mese.head(3).iterrows():
                target = int(r_ev['posti_richiesti'])
                iscr = int(r_ev['tot_iscritti'])
                stato_s = r_ev['stato']
                
                if stato_s == 'Concluso':
                    ico_led = "🔵"
                    bordo_c = "#3b82f6"
                elif iscr >= target:
                    ico_led = "🟢"
                    bordo_c = "#10b981"
                elif iscr > 0:
                    ico_led = "🟡"
                    bordo_c = "#f59e0b"
                else:
                    ico_led = "🔴"
                    bordo_c = "#ef4444"
                
                titolo_breve = r_ev['titolo'][:12] + ".." if len(r_ev['titolo']) > 12 else r_ev['titolo']
                eventi_anteprima_html += f"""
                    <div class="event-micro-badge" style="border-left-color: {bordo_c};">
                        {ico_led} <b>{r_ev['giorno']}/{m_str}</b>: {titolo_breve}
                    </div>
                """
            if tot_ev > 3:
                eventi_anteprima_html += f'<div style="font-size:9px; color:#94a3b8; margin-top:4px;">+{tot_ev - 3} altri</div>'
        else:
            eventi_anteprima_html = '<div style="font-size:10px; color:#475569; margin-top:20px; text-align:center;">Libero</div>'
        
        grid_html += (
            f'<div class="month-tile {is_active}">'
            f'<div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1f2937; padding-bottom:4px;">'
            f'<span class="month-title">{mesi_nomi[i-1]}</span>'
            f'<span style="font-weight:800; font-size:12px; color:{col_c};">{tot_ev}</span>'
            f'</div>'
            f'{eventi_anteprima_html}'
            f'</div>'
        )
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("#### Elenco Attività Programmate nell'Anno")
    if df_servizi_anno.empty:
        st.info("Nessuna attività registrata per l'annualità selezionata.")
    else:
        df_mostra = df_servizi_anno.copy()
        try:
            df_mostra["data"] = pd.to_datetime(df_mostra["data"]).dt.strftime('%d/%m/%Y')
        except:
            pass
        st.dataframe(
            df_mostra[["data", "titolo", "luogo", "posti_richiesti", "tot_iscritti", "stato"]].rename(columns={
                "data": "Data", "titolo": "Missione", "luogo": "Località", 
                "posti_richiesti": "Target Richiesto", "tot_iscritti": "Adesioni Attuali", "stato": "Stato"
            }),
            use_container_width=True
        )

# ----------------------------------------------------
# 2. SINOTTICO HUD TIMELINE
# ----------------------------------------------------
elif ruolo_accesso == "Sinottico HUD Timeline":
    st.subheader("📡 Sinottico Grafico Operativo")
    st.caption("Controllo a 4 stati cromatici, nowcasting georeferenziato e assorbimento riserve")
    
    servizi = run_query("SELECT * FROM servizi WHERE stato = 'Programmato' ORDER BY data ASC")
    
    if servizi.empty:
        st.info("Nessuna missione programmata attiva.")
    else:
        for _, serv in servizi.iterrows():
            s_id = serv["id"]
            luogo = serv.get("luogo", "Grosseto")
            try:
                h_ini = int(str(serv["ora_inizio"]).split(":")[0])
                h_fine = int(str(serv["ora_fine"]).split(":")[0])
                if h_fine <= h_ini:
                    h_fine = h_ini + max(int(serv["ore_servizio"]), 1)
            except:
                h_ini, h_fine = 14, 20
                
            target = int(serv["posti_richiesti"])
            ore_nette = float(serv.get("ore_servizio", h_fine - h_ini))
            
            try:
                dt_obj = datetime.strptime(serv["data"], "%Y-%m-%d")
                data_italiana = dt_obj.strftime("%d/%m/%Y")
            except:
                data_italiana = serv["data"]
            
            adesioni_totali = run_query("""
                SELECT a.id, v.nome, v.ruolo, a.modalita, a.ora_inizio_disp, a.ora_fine_disp, a.ore_effettive, a.stato
                FROM adesioni a 
                JOIN volontari v ON a.volontario_id = v.id 
                WHERE a.servizio_id = ?
            """, (s_id,))
            
            confermati = adesioni_totali[adesioni_totali["stato"] == "Confermato"]
            riserve = adesioni_totali[adesioni_totali["stato"] == "Riserva"]
            ore_servizio = list(range(h_ini, h_fine))
            
            m_data = get_meteo_dettagliato(luogo, serv["data"])
            if m_data["valido"]:
                colore_bordo = "#ef4444" if m_data["allerta"] else "#2563eb"
                ico_status = "⚠️ ATTENZIONE METEO" if m_data["allerta"] else "☀️ CONDIZIONI OPERATIVE"
                meteo_html = (
                    f'<div class="meteo-box-hud" style="border-left: 4px solid {colore_bordo};">'
                    f'<div>'
                    f'<div class="meteo-location-title">{ico_status} — PRESIDIO: {m_data["luogo"].upper()}</div>'
                    f'<div style="font-size:11px; color:#94a3b8; margin-top:2px;">Rilevamento per il giorno {data_italiana} (Fascia {serv["ora_inizio"]} - {serv["ora_fine"]})</div>'
                    f'</div>'
                    f'<div class="meteo-metrics-group">'
                    f'<div class="meteo-metric-item">🌡️ Max: {m_data["temp"]}</div>'
                    f'<div class="meteo-metric-item">🌧️ Pioggia: {m_data["pioggia"]}</div>'
                    f'<div class="meteo-metric-item">💨 Vento: {m_data["vento"]}</div>'
                    f'</div>'
                    f'</div>'
                )
            else:
                meteo_html = (
                    f'<div class="meteo-box-hud" style="border-left: 4px solid #64748b;">'
                    f'<div class="meteo-location-title">📍 PRESIDIO: {luogo.upper()}</div>'
                    f'<div style="font-size:12px; color:#94a3b8;">{m_data["msg"]}</div>'
                    f'</div>'
                )
            
            header_card = (
                f'<div class="event-card">'
                f'<div class="card-header-flex">'
                f'<div>'
                f'<div style="font-size:11px; font-weight:700; color:#64748b; letter-spacing:1px; margin-bottom:4px;">MISSIONE OPERATIVA CISOM</div>'
                f'<h2 class="event-title-text">{serv["titolo"]}</h2>'
                f'</div>'
                f'<div class="event-time-badge">'
                f'<div class="event-date-large">📅 {data_italiana}</div>'
                f'<div class="event-hours-sub">⏱️ {serv["ora_inizio"]} - {serv["ora_fine"]} ({ore_nette}h nette | Target: {target}/ora)</div>'
                f'</div>'
                f'</div>'
                f'{meteo_html}'
            )
            
            blocchi_html = '<div class="timeline-container">'
            scoperti_totali = 0
            
            for h in ore_servizio:
                presenti_ora = []
                for _, ad in confermati.iterrows():
                    mod = ad["modalita"]
                    if mod == "Completo":
                        presenti_ora.append(ad["nome"])
                    elif mod == "Fascia Specifica":
                        try:
                            ad_ini = int(str(ad["ora_inizio_disp"]).split(":")[0])
                            ad_fine = int(str(ad["ora_fine_disp"]).split(":")[0])
                            if ad_ini <= h < ad_fine:
                                presenti_ora.append(ad["nome"])
                        except:
                            pass
                
                c_ora = len(presenti_ora)
                if c_ora == 0:
                    css_slot = "slot-red"
                    label_stato = "0 SCOPERTO"
                    scoperti_totali += 1
                elif c_ora < target:
                    css_slot = "slot-yellow"
                    label_stato = f"{c_ora}/{target} PARZIALE"
                    scoperti_totali += 1
                elif c_ora == target:
                    css_slot = "slot-green"
                    label_stato = f"{c_ora}/{target} COPERTO"
                else:
                    css_slot = "slot-blue"
                    eccedenza = c_ora - target
                    label_stato = f"{c_ora}/{target} (+{eccedenza} RIS)"
                
                nomi_tags = "".join([f'<div class="badge-name">{n}</div>' for n in presenti_ora]) if presenti_ora else '<div style="color:#6b7280; font-size:10px; margin-top:8px;">[ VUOTO ]</div>'
                
                blocchi_html += (
                    f'<div class="time-slot {css_slot}">'
                    f'<div>{h:02d}:00 - {(h+1):02d}:00</div>'
                    f'<div>{nomi_tags}</div>'
                    f'<div style="font-size:9px; opacity:0.9; margin-top:4px;">{label_stato}</div>'
                    f'</div>'
                )
            blocchi_html += '</div>'
            
            banner_allerta = f'<div class="alert-banner-yellow">⚠️ ATTENZIONE: Rilevati blocchi orari parziali o scoperti ({scoperti_totali} ore da integrare).</div>' if scoperti_totali > 0 else ""
            
            da_concordare = confermati[confermati["modalita"] == "Da Concordare"]
            badge_flessibili = ""
            if not da_concordare.empty:
                badge_flessibili = '<div class="badge-da-concordare"><strong>🔄 Disponibilità flessibili da concordare con la squadra:</strong><br>'
                for _, flx in da_concordare.iterrows():
                    badge_flessibili += f"• 👤 <strong>{flx['nome']}</strong> offre <strong>{flx['ore_effettive']} ore</strong> (fascia oraria libera)<br>"
                badge_flessibili += '</div>'
            
            dot_extra = ""
            if serv.get("dotazioni") or serv.get("note_servizio"):
                dot_extra = '<div style="background-color:#111827; border:1px solid #1f2937; border-radius:6px; padding:10px 14px; margin-top:10px; font-size:12px;">'
                if serv.get("dotazioni"):
                    dot_extra += f'<div><strong>📦 Dotazioni & Mezzi:</strong> <span style="color:#93c5fd;">{serv["dotazioni"]}</span></div>'
                if serv.get("note_servizio"):
                    dot_extra += f'<div style="margin-top:4px;"><strong>📝 Disposizioni Comando:</strong> <span style="color:#cbd5e1;">{serv["note_servizio"]}</span></div>'
                dot_extra += '</div>'

            st.markdown(header_card + banner_allerta + blocchi_html + badge_flessibili + dot_extra + '</div>', unsafe_allow_html=True)
            
            if scoperti_totali > 0 and not riserve.empty:
                st.markdown("**🔵 Risorse in riserva pronte all'attivazione immediata:**")
                for _, r_row in riserve.iterrows():
                    c_ris1, c_ris2 = st.columns([4, 1])
                    c_ris1.write(f"👤 **{r_row['nome']}** [{r_row['ruolo']}] è disponibile in riserva.")
                    if c_ris2.button("Sposta in Turno Attivo", key=f"att_r_{r_row['id']}"):
                        run_query("UPDATE adesioni SET stato = 'Confermato' WHERE id = ?", (int(r_row["id"]),), fetch=False)
                        st.rerun()

# ----------------------------------------------------
# 3. BACHECA VOLONTARIO
# ----------------------------------------------------
elif ruolo_accesso == "Bacheca Volontario":
    st.subheader("📋 Bacheca Incarichi Operativi")
    
    volontari_df = run_query("SELECT * FROM volontari WHERE attivo = 1 ORDER BY nome ASC")
    if volontari_df.empty:
        st.warning("Nessun membro attivo registrato in archivio.")
    else:
        utente_id = st.selectbox(
            "Identificati con il tuo profilo istituzionale:", 
            volontari_df["id"].tolist(), 
            format_func=lambda x: f"{volontari_df.loc[volontari_df['id'] == x, 'nome'].values[0]} — [{volontari_df.loc[volontari_df['id'] == x, 'ruolo'].values[0]}]"
        )
        
        dati_utente = volontari_df[volontari_df["id"] == utente_id].iloc[0]
        utente_nome = dati_utente["nome"]
        utente_email = dati_utente.get("email", "") if hasattr(dati_utente, "get") else ""
        utente_ruolo = dati_utente["ruolo"]
        
        servizi = run_query("SELECT * FROM servizi WHERE stato = 'Programmato' ORDER BY data ASC")
        if servizi.empty:
            st.info("Nessuna missione programmata disponibile al momento.")
        else:
            for _, serv in servizi.iterrows():
                with st.container(border=True):
                    try:
                        d_it = datetime.strptime(serv["data"], "%Y-%m-%d").strftime("%d/%m/%Y")
                    except:
                        d_it = serv["data"]
                        
                    st.markdown(f"### {serv['titolo']} ({serv['luogo']})")
                    st.write(f"📅 **Data:** {d_it} | ⏰ **Finestra:** {serv['ora_inizio']} - {serv['ora_fine']} ({serv['ore_servizio']}h nette)")
                    
                    if serv.get("dotazioni"):
                        st.caption(f"📦 **Dotazioni richieste:** {serv['dotazioni']}")
                    if serv.get("note_servizio"):
                        st.caption(f"📝 **Disposizioni:** {serv['note_servizio']}")

                    adesioni = run_query("SELECT * FROM adesioni WHERE servizio_id = ? AND volontario_id = ?", (int(serv["id"]), int(utente_id)))
                    
                    if not adesioni.empty:
                        mia_ad = adesioni.iloc[0]
                        st.success(f"✅ La tua disponibilità per questa missione è confermata a registro. Grazie. Modalità: **{mia_ad['modalita']}** ({mia_ad['ore_effettive']}h)")
                        
                        if st.button("❌ Revoca / Cancella la mia disponibilità", key=f"del_ad_{serv['id']}_{utente_id}"):
                            run_query("DELETE FROM adesioni WHERE servizio_id = ? AND volontario_id = ?", 
                                      (int(serv["id"]), int(utente_id)), fetch=False)
                            
                            if utente_email and "@" in str(utente_email):
                                corpo_revoca = f"""
                                <div style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #0b0f17; color: #e2e8f0; padding: 26px; border-radius: 8px; max-width: 580px; margin: auto; border: 1px solid #1e293b;">
                                    <div style="text-align: center; border-bottom: 2px solid #ef4444; padding-bottom: 14px; margin-bottom: 18px;">
                                        <div style="font-size: 26px; line-height: 1; color: #ef4444;">✠</div>
                                        <div style="font-size: 15px; font-weight: 800; color: #ef4444; letter-spacing: 2px; text-transform: uppercase; margin-top: 5px;">SOVRANO MILITARE ORDINE DI MALTA</div>
                                        <div style="font-size: 12px; font-weight: 600; color: #94a3b8; letter-spacing: 1px;">CORPO ITALIANO DI SOCCORSO DELL'ORDINE DI MALTA</div>
                                        <div style="font-size: 11px; font-weight: 700; color: #ef4444; margin-top: 3px;">SEZIONE DI GROSSETO — NOTIFICA REVOCA DISPONIBILITÀ</div>
                                    </div>
                                    <p style="font-size: 14px; margin-bottom: 10px;">Gentile <strong>{utente_nome}</strong>,</p>
                                    <p style="font-size: 12px; color: #cbd5e1; margin-bottom: 14px;">
                                        Inquadramento: <strong>{utente_ruolo}</strong><br>
                                        Si attesta l'avvenuta <strong>revoca</strong> della tua disponibilità per il seguente servizio operativo:
                                    </p>
                                    <div style="background-color: #111827; border: 1px solid #1f293d; border-radius: 6px; padding: 16px; margin: 16px 0;">
                                        <div style="margin-bottom: 8px;"><strong style="color: #94a3b8;">🎯 MISSIONE:</strong> <span style="font-size: 14px; font-weight: 800; color: #ffffff;">{serv['titolo']}</span></div>
                                        <div style="margin-bottom: 8px;"><strong style="color: #94a3b8;">📍 TEATRO OPERATIVO:</strong> <span style="font-weight: 700; color: #38bdf8;">{serv['luogo']}</span></div>
                                        <div style="margin-bottom: 8px;"><strong style="color: #94a3b8;">📅 DATA:</strong> <span style="font-weight: 700; color: #f8fafc;">{d_it}</span></div>
                                    </div>
                                    <p style="font-size: 12px; color: #94a3b8;">La tua posizione a ruolino per questa data è stata rimossa e il posto liberato sulla Control Tower.</p>
                                    <div style="border-top: 1px solid #1f293d; padding-top: 12px; font-size: 11px; color: #64748b; text-align: center;">
                                        CISOM Sezione Grosseto — Sovereign Zero Control Tower
                                    </div>
                                </div>
                                """
                                invia_email_notifica(utente_email, f"CISOM Grosseto: Conferma Revoca Turno {serv['titolo']}", corpo_revoca)

                            st.toast("Disponibilità revocata con successo!")
                            st.rerun()
                    else:
                        st.markdown("#### Scegli come dare la tua disponibilità:")
                        col_m1, col_m2 = st.columns(2)
                        tipo_scelta = col_m1.radio(
                            "Tipologia Impegno:",
                            ["Turno Completo", "Fascia Oraria Specifica", "Monte Ore Flessibile (Da concordare)"],
                            key=f"tipo_{serv['id']}"
                        )
                        
                        ore_da_registrare = float(serv["ore_servizio"])
                        h_ini_scelta = serv["ora_inizio"]
                        h_fine_scelta = serv["ora_fine"]
                        mod_salvata = "Completo"
                        
                        if tipo_scelta == "Turno Completo":
                            col_m2.info(f"Coprirai l'intero servizio dalle {serv['ora_inizio']} alle {serv['ora_fine']} ({serv['ore_servizio']}h).")
                            
                        elif tipo_scelta == "Fascia Oraria Specifica":
                            mod_salvata = "Fascia Specifica"
                            sub_c1, sub_c2 = col_m2.columns(2)
                            h_ini_scelta = str(sub_c1.time_input("Da ore:", time(9, 0), key=f"ti_{serv['id']}"))[:5]
                            h_fine_scelta = str(sub_c2.time_input("A ore:", time(13, 0), key=f"tf_{serv['id']}"))[:5]
                            
                            diff = (datetime.combine(date.today(), datetime.strptime(h_fine_scelta, "%H:%M").time()) - 
                                    datetime.combine(date.today(), datetime.strptime(h_ini_scelta, "%H:%M").time())).total_seconds() / 3600.0
                            ore_da_registrare = max(0.5, round(diff, 1))
                            col_m2.caption(f"Fascia oraria selezionata: **{ore_da_registrare}h** nette.")
                            
                        elif tipo_scelta == "Monte Ore Flessibile (Da concordare)":
                            mod_salvata = "Da Concordare"
                            ore_da_registrare = col_m2.number_input("Quante ore metti a disposizione?", min_value=1.0, max_value=float(serv["ore_servizio"]), value=3.0, step=0.5, key=f"ore_flx_{serv['id']}")
                            col_m2.caption("L'orario esatto verrà armonizzato dal Caposquadra con la squadra operativa.")
                            
                        if st.button("✋ Invia la mia disponibilità", key=f"btn_send_{serv['id']}"):
                            run_query("""
                                INSERT INTO adesioni (servizio_id, volontario_id, stato, modalita, ora_inizio_disp, ora_fine_disp, note, ore_effettive)
                                VALUES (?, ?, 'Confermato', ?, ?, ?, '', ?)
                            """, (int(serv["id"]), int(utente_id), mod_salvata, h_ini_scelta, h_fine_scelta, ore_da_registrare), fetch=False)
                            
                            if utente_email and "@" in str(utente_email):
                                corpo_mail = f"""
                                <div style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #0b0f17; color: #e2e8f0; padding: 26px; border-radius: 8px; max-width: 580px; margin: auto; border: 1px solid #1e293b;">
                                    <div style="text-align: center; border-bottom: 2px solid #dc2626; padding-bottom: 14px; margin-bottom: 18px;">
                                        <div style="font-size: 26px; line-height: 1; color: #dc2626;">✠</div>
                                        <div style="font-size: 15px; font-weight: 800; color: #ef4444; letter-spacing: 2px; text-transform: uppercase; margin-top: 5px;">SOVRANO MILITARE ORDINE DI MALTA</div>
                                        <div style="font-size: 12px; font-weight: 600; color: #94a3b8; letter-spacing: 1px;">CORPO ITALIANO DI SOCCORSO DELL'ORDINE DI MALTA</div>
                                        <div style="font-size: 11px; font-weight: 700; color: #3b82f6; margin-top: 3px;">SEZIONE DI GROSSETO — FOGLIO DI SERVIZIO</div>
                                    </div>
                                    <p style="font-size: 14px; margin-bottom: 10px;">Gentile <strong>{utente_nome}</strong>,</p>
                                    <p style="font-size: 12px; color: #cbd5e1; margin-bottom: 14px;">
                                        Inquadramento: <strong>{utente_ruolo}</strong><br>
                                        È stata registrata con successo la tua disponibilità operativa per il seguente intervento:
                                    </p>
                                    <div style="background-color: #111827; border: 1px solid #1f293d; border-radius: 6px; padding: 16px; margin: 16px 0;">
                                        <div style="margin-bottom: 8px;"><strong style="color: #94a3b8;">🎯 MISSIONE:</strong> <span style="font-size: 14px; font-weight: 800; color: #ffffff;">{serv['titolo']}</span></div>
                                        <div style="margin-bottom: 8px;"><strong style="color: #94a3b8;">📍 TEATRO OPERATIVO:</strong> <span style="font-weight: 700; color: #38bdf8;">{serv['luogo']}</span></div>
                                        <div style="margin-bottom: 8px;"><strong style="color: #94a3b8;">📅 DATA:</strong> <span style="font-weight: 700; color: #f8fafc;">{d_it}</span></div>
                                        <div style="margin-bottom: 8px;"><strong style="color: #94a3b8;">⏱️ MODALITÀ:</strong> <span style="color: #cbd5e1;">{tipo_scelta}</span></div>
                                        <div><strong style="color: #94a3b8;">⏳ IMPEGNO ASSEGNATO:</strong> <span style="color: #4ade80; font-weight: 700;">{ore_da_registrare}h</span> (Fascia: {h_ini_scelta} - {h_fine_scelta})</div>
                                    </div>
                                    <div style="border-top: 1px solid #1f293d; padding-top: 12px; font-size: 11px; color: #64748b; text-align: center;">
                                        CISOM Sezione Grosseto — Sovereign Zero Control Tower
                                    </div>
                                </div>
                                """
                                invia_email_notifica(utente_email, f"CISOM Grosseto: Memo Servizio {serv['titolo']} ({d_it})", corpo_mail)

                            st.success("Disponibilità registrata con successo!")
                            st.rerun()

# ----------------------------------------------------
# 4. CONSUNTIVO & MONTE ORE (BONIFICATO)
# ----------------------------------------------------
elif ruolo_accesso == "Consuntivo & Monte Ore":
    st.subheader("📊 Analisi Operativa & Monte Ore Ufficiale CISOM")
    st.caption("I contatori escludono automaticamente le missioni cancellate o revocate")
    
    query_ore = """
        SELECT v.nome AS Membro, 
               v.email AS Email,
               v.macroarea AS Macroarea,
               v.ruolo AS Rango_Qualifica,
               CASE WHEN v.attivo = 1 THEN 'Attivo' ELSE 'Archiviato' END AS Profilo,
               COUNT(CASE WHEN s.stato IN ('Programmato', 'Concluso') THEN a.id END) AS Missioni_Assegnate,
               SUM(CASE WHEN a.validato = 1 AND s.stato = 'Concluso' THEN a.ore_effettive ELSE 0 END) AS Ore_Convalidate,
               SUM(CASE WHEN a.validato = 0 AND a.stato = 'Confermato' AND s.stato = 'Programmato' THEN a.ore_effettive ELSE 0 END) AS Ore_Da_Convalidare
        FROM volontari v
        LEFT JOIN adesioni a ON v.id = a.volontario_id
        LEFT JOIN servizi s ON a.servizio_id = s.id
        GROUP BY v.id
        ORDER BY Ore_Convalidate DESC
    """
    df_report = run_query(query_ore)
    st.dataframe(df_report, width='stretch')
    
    st.divider()
    st.markdown("#### ✅ Convalida Presenze Post-Servizio")
    in_attesa = run_query("""
        SELECT a.id, v.nome, v.ruolo, s.titolo, s.data, a.modalita, a.ore_effettive
        FROM adesioni a
        JOIN volontari v ON a.volontario_id = v.id
        JOIN servizi s ON a.servizio_id = s.id
        WHERE a.validato = 0 AND a.stato = 'Confermato' AND s.stato IN ('Programmato', 'Concluso')
    """)
    
    if in_attesa.empty:
        st.success("Tutte le presenze risultano convalidate a registro.")
    else:
        for _, row in in_attesa.iterrows():
            c_info, c_action = st.columns([4, 1])
            try:
                data_mostra = datetime.strptime(row['data'], "%Y-%m-%d").strftime("%d/%m/%Y")
            except:
                data_mostra = row['data']
            c_info.write(f"👤 **{row['nome']}** [{row['ruolo']}] | {row['titolo']} ({data_mostra}) — Modalità: *{row['modalita']}* (**{row['ore_effettive']}h**)")
            if c_action.button("Convalida Ore", key=f"val_{row['id']}"):
                run_query("UPDATE adesioni SET validato = 1 WHERE id = ?", (int(row["id"]),), fetch=False)
                st.rerun()

# ----------------------------------------------------
# 5. SALA SITUAZIONI
# ----------------------------------------------------
elif ruolo_accesso == "🏛️ Sala Situazioni":
    st.subheader("🏛️ Sala Situazioni & Statistiche")
    st.caption("Control Tower — Livello Operativo e Storico Completo")

    df_stat = run_query("""
        SELECT a.id AS adesione_id, a.servizio_id, s.titolo, s.stato AS stato_servizio,
               a.stato AS stato_adesione, a.ore_effettive, 
               a.pronto_impiego, a.modalita,
               v.nome, v.ruolo, v.macroarea
        FROM adesioni a
        LEFT JOIN volontari v ON a.volontario_id = v.id
        LEFT JOIN servizi s ON a.servizio_id = s.id
        WHERE s.stato NOT LIKE 'Annullato%'
    """)

    if not df_stat.empty:
        c1, c2, c3 = st.columns(3)
        tot_ore = df_stat[df_stat["stato_servizio"] == "Concluso"]["ore_effettive"].dropna().sum()
        attivi = len(df_stat[df_stat["stato_servizio"] == "Programmato"])
        pronti = len(df_stat[df_stat["pronto_impiego"] == 1])

        c1.metric("Monte Ore Effettuato", f"{tot_ore:.1f} h")
        c2.metric("Turni in Corso", attivi)
        c3.metric("Adesioni Totali", len(df_stat))

        st.write("---")
        st.dataframe(df_stat, width='stretch')

        csv_buffer = df_stat.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Scarica Report Operativo (CSV)",
            data=csv_buffer,
            file_name=f"report_cisom_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Nessun dato di servizio attivo al momento.")

# ----------------------------------------------------
# 6. CONFIGURAZIONE, GESTIONE & ARCHIVIO
# ----------------------------------------------------
elif ruolo_accesso == "Configurazione & Gestione":
    tab_servizi, tab_archivio, tab_volontari, tab_presidi = st.tabs([
        "⚙️ Servizi & Eventi", 
        "🗃️ Archivio Distrettuale", 
        "👤 Anagrafica Ufficiale & Ruoli", 
        "📍 Presidi & Basi Operative"
    ])
    
    with tab_servizi:
        st.markdown("#### Inserimento Nuovo Servizio & Ordine Operativo")
        with st.form("form_nuovo_servizio"):
            titolo = st.text_input("Titolo Missione / Evento", placeholder="es. Assistenza Manifestazione, Emergenza Idrogeologica")
            col_l, col_d = st.columns(2)
            coords_attive = get_coordinate_presidi()
            luogo = col_l.selectbox("Località Presidio (Meteo Nowcasting)", list(coords_attive.keys()))
            d = col_d.date_input("Data Evento", date.today())

            col_p, col_h1, col_h2 = st.columns(3)
            posti = col_p.number_input("Target Volontari/Fascia", min_value=1, value=2)
            t_ini = col_h1.time_input("Ora Inizio", time(9, 0))
            t_fine = col_h2.time_input("Ora Fine", time(17, 0))
            
            pausa_min = st.selectbox("Pausa Operativa / Cambio Turno", [0, 30, 60, 90], format_func=lambda x: f"{x} min" if x > 0 else "Nessuna")
            
            diff_h = (datetime.combine(date.today(), t_fine) - datetime.combine(date.today(), t_ini)).total_seconds() / 3600.0
            ore_calc = max(0.5, round(diff_h - (pausa_min / 60.0), 2))
            st.info(f"⏱️ Durata Netta: **{ore_calc} ore**")
            
            st.markdown("##### 📦 Dotazioni, Logistica e Mezzi Assegnati")
            col_d1, col_d2 = st.columns(2)
            dotazioni_scelte = col_d1.multiselect(
                "Seleziona Mezzi e Strutture:",
                [
                    "🚑 Ambulanza Soccorso (MSB)",
                    "🚙 Fuoristrada Protezione Civile 4x4",
                    "🚐 Furgone Logistico",
                    "⛺ Gazebo Istituzionale CISOM (3x3)",
                    "🪑 Tavolo + Panchine da campo",
                    "💡 Generatore Elettrico / Torre Faro"
                ],
                default=["🚑 Ambulanza Soccorso (MSB)", "⛺ Gazebo Istituzionale CISOM (3x3)"]
            )
            
            presidi_scelti = col_d2.multiselect(
                "Seleziona Presidi Sanitari, TLC & Divisa:",
                [
                    "📻 Radio Portatili VHF/UHF",
                    "🎒 Zaino Soccorso Avanzato + DAE",
                    "🩺 Aspiratore secreti + Bombola O2",
                    "🦺 Divisa Operativa Alta Visibilità CISOM",
                    "🥾 Scarponi Antinfortunistici Obbligatori",
                    "🌧️ Giacca Antipioggia / Mantella"
                ],
                default=["📻 Radio Portatili VHF/UHF", "🎒 Zaino Soccorso Avanzato + DAE", "🦺 Divisa Operativa Alta Visibilità CISOM"]
            )
            
            note_operative = st.text_area(
                "📝 Disposizioni Particolari / Ordini di Servizio del Capogruppo", 
                placeholder="es. Ritrovo ore 07:30 in sede per carico materiali. Pranzo al sacco fornito dall'organizzazione."
            )
            
            invia_circolare = st.checkbox("📢 Spedisci Dispaccio Operativo circolare a TUTTI i volontari attivi via email", value=True)

            if st.form_submit_button("Pubblica Missione & Notifica") and titolo:
                dot_unite = ", ".join(dotazioni_scelte + presidi_scelti)
                sql_ins = """
                    INSERT INTO servizi (titolo, luogo, data, ora_inizio, ora_fine, posti_richiesti, ore_servizio, pausa_minuti, stato, dotazioni, note_servizio) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Programmato', ?, ?)
                """
                run_query(sql_ins, (titolo, luogo, str(d), str(t_ini), str(t_fine), posti, ore_calc, pausa_min, dot_unite, note_operative), fetch=False)
                
                if invia_circolare:
                    volontari_dest = run_query("SELECT nome, email FROM volontari WHERE attivo = 1 AND email != ''")
                    if not volontari_dest.empty:
                        d_mostra = d.strftime("%d/%m/%Y")
                        for _, vol in volontari_dest.iterrows():
                            dest_m = vol["email"]
                            dest_n = vol["nome"]
                            if "@" in str(dest_m):
                                corpo_dispaccio = f"""
                                <div style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #0b0f17; color: #e2e8f0; padding: 26px; border-radius: 8px; max-width: 580px; margin: auto; border: 1px solid #1e293b;">
                                    <div style="text-align: center; border-bottom: 2px solid #dc2626; padding-bottom: 14px; margin-bottom: 18px;">
                                        <div style="font-size: 26px; line-height: 1; color: #dc2626;">✠</div>
                                        <div style="font-size: 15px; font-weight: 800; color: #ef4444; letter-spacing: 2px; text-transform: uppercase; margin-top: 5px;">SOVRANO MILITARE ORDINE DI MALTA</div>
                                        <div style="font-size: 12px; font-weight: 600; color: #94a3b8; letter-spacing: 1px;">CORPO ITALIANO DI SOCCORSO DELL'ORDINE DI MALTA</div>
                                        <div style="font-size: 11px; font-weight: 700; color: #3b82f6; margin-top: 3px;">SEZIONE DI GROSSETO — DISPACCIO OPERATIVO CONVOCAZIONE</div>
                                    </div>
                                    <p style="font-size: 14px;">Gentile <strong>{dest_n}</strong>,</p>
                                    <p style="font-size: 13px; color: #cbd5e1;">È stato pubblicato un nuovo ordine di servizio operativo per la Sezione. Si richiede la massima adesione da parte dei volontari idonei:</p>
                                    
                                    <div style="background-color: #111827; border: 1px solid #1f293d; border-radius: 6px; padding: 16px; margin: 16px 0;">
                                        <div style="margin-bottom: 8px;"><strong style="color: #94a3b8;">🎯 MISSIONE:</strong> <span style="font-size: 15px; font-weight: 800; color: #ffffff;">{titolo}</span></div>
                                        <div style="margin-bottom: 8px;"><strong style="color: #94a3b8;">📍 TEATRO OPERATIVO:</strong> <span style="font-weight: 700; color: #38bdf8;">{luogo}</span></div>
                                        <div style="margin-bottom: 8px;"><strong style="color: #94a3b8;">📅 DATA:</strong> <span style="font-weight: 700; color: #f8fafc;">{d_mostra}</span></div>
                                        <div style="margin-bottom: 8px;"><strong style="color: #94a3b8;">⏱️ ORARIO:</strong> <span style="color: #cbd5e1;">{t_ini} - {t_fine} ({ore_calc}h nette)</span></div>
                                        <div style="margin-bottom: 8px;"><strong style="color: #94a3b8;">👥 FABBISOGNO TARGET:</strong> <span style="color: #f59e0b; font-weight: 700;">{posti} volontari</span></div>
                                        <div style="margin-bottom: 8px;"><strong style="color: #94a3b8;">📦 MATERIALI ASSEGNATI:</strong> <span style="color: #93c5fd; font-size: 12px;">{dot_unite if dot_unite else 'Standard da campo'}</span></div>
                                        <div><strong style="color: #94a3b8;">📝 DISPOSIZIONI COMANDO:</strong> <span style="color: #e2e8f0; font-size: 12px;">{note_operative if note_operative else 'Vedi istruzioni del Caposquadra in loco.'}</span></div>
                                    </div>
                                    
                                    <div style="text-align: center; margin: 24px 0;">
                                        <a href="{APP_URL}" style="background-color: #dc2626; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: 800; font-size: 13px; display: inline-block; letter-spacing: 0.5px;">
                                            👉 APRI LA CONTROL TOWER & CANDIDATI ORA
                                        </a>
                                    </div>
                                    
                                    <div style="border-top: 1px solid #1f293d; padding-top: 12px; font-size: 11px; color: #64748b; text-align: center;">
                                        CISOM Sezione Grosseto — Sovereign Zero Control Tower
                                    </div>
                                </div>
                                """
                                invia_email_notifica(dest_m, f"DISPACCIO OPERATIVO CISOM: {titolo} ({d_mostra})", corpo_dispaccio)

                st.success("Servizio inserito e dispaccio circolare inviato alla forza attiva!")
                st.rerun()

        st.divider()
        st.markdown("#### 🎛️ Gestione Direttivo: Ciclo di Vita Missioni Attive")
        servizi_attivi = run_query("SELECT * FROM servizi WHERE stato = 'Programmato' ORDER BY data ASC")
        if servizi_attivi.empty:
            st.info("Nessuna attività in corso.")
        else:
            for _, s_row in servizi_attivi.iterrows():
                try:
                    dt_v = datetime.strptime(s_row['data'], "%Y-%m-%d").strftime("%d/%m/%Y")
                except:
                    dt_v = s_row['data']
                    
                with st.expander(f"📅 {dt_v} — {s_row['titolo']} ({s_row['luogo']})"):
                    def notifica_squadra_annullamento(serv_id, titolo_ev, data_ev, motivo_testo):
                        iscritti = run_query("""
                            SELECT v.nome, v.email 
                            FROM adesioni a 
                            JOIN volontari v ON a.volontario_id = v.id 
                            WHERE a.servizio_id = ?
                        """, (int(serv_id),))
                        
                        if not iscritti.empty:
                            for _, iscr in iscritti.iterrows():
                                e_mail = iscr['email']
                                n_ome = iscr['nome']
                                if e_mail and "@" in str(e_mail):
                                    corpo_annullo = f"""
                                    <div style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #0b0f17; color: #e2e8f0; padding: 26px; border-radius: 8px; max-width: 580px; margin: auto; border: 1px solid #1e293b;">
                                        <div style="text-align: center; border-bottom: 2px solid #ef4444; padding-bottom: 14px; margin-bottom: 18px;">
                                            <div style="font-size: 26px; line-height: 1; color: #ef4444;">✠</div>
                                            <div style="font-size: 15px; font-weight: 800; color: #ef4444; letter-spacing: 2px; text-transform: uppercase; margin-top: 5px;">SOVRANO MILITARE ORDINE DI MALTA</div>
                                            <div style="font-size: 12px; font-weight: 600; color: #94a3b8; letter-spacing: 1px;">CORPO ITALIANO DI SOCCORSO DELL'ORDINE DI MALTA</div>
                                            <div style="font-size: 11px; font-weight: 700; color: #ef4444; margin-top: 3px;">NOTIFICA UFFICIALE: MISSIONE ANNULLATA / SOSPESA</div>
                                        </div>
                                        <p style="font-size: 14px;">Gentile <strong>{n_ome}</strong>,</p>
                                        <p style="font-size: 13px; color: #cbd5e1;">Si comunica che il servizio operativo <strong>{titolo_ev}</strong> programmato per il giorno <strong>{data_ev}</strong> è stato <strong>ANNULLATO DALLA SEGRETERIA OPERATIVA</strong>.</p>
                                        <div style="background-color: #111827; border-left: 4px solid #ef4444; padding: 12px 16px; margin: 16px 0; border-radius: 4px;">
                                            <strong style="color: #f87171;">MOTIVAZIONE UFFICIALE:</strong><br>
                                            <span style="color: #ffffff; font-size: 13px;">{motivo_testo}</span>
                                        </div>
                                        <p style="font-size: 12px; color: #94a3b8;">La tua disponibilità per questa data è stata svincolata dal registro e non dovrai presentarti al presidio.</p>
                                        <div style="border-top: 1px solid #1f293d; padding-top: 12px; font-size: 11px; color: #64748b; text-align: center; margin-top: 18px;">
                                            CISOM Sezione Grosseto — Sovereign Zero Control Tower
                                        </div>
                                    </div>
                                    """
                                    invia_email_notifica(e_mail, f"CISOM Grosseto: AVVISO ANNULLAMENTO Servizio {titolo_ev}", corpo_annullo)

                    c_act1, c_act2, c_act3 = st.columns(3)
                    
                    if c_act1.button("✅ Concludi e Convalida (Svolta)", key=f"end_{s_row['id']}"):
                        run_query("UPDATE servizi SET stato = 'Concluso' WHERE id = ?", (int(s_row["id"]),), fetch=False)
                        st.success("Missione contrassegnata come Conclusa.")
                        st.rerun()
                        
                    if c_act2.button("🌧️ Annulla: Allerta Meteo", key=f"w_{s_row['id']}"):
                        notifica_squadra_annullamento(s_row['id'], s_row['titolo'], dt_v, "Allerta Meteo e condizioni avverse incompatibili con lo svolgimento in sicurezza.")
                        run_query("UPDATE servizi SET stato = 'Annullato per Allerta Meteo' WHERE id = ?", (int(s_row["id"]),), fetch=False)
                        st.warning("Archiviata per causa meteo e squadra avvisata via email.")
                        st.rerun()
                        
                    if c_act3.button("👥 Annulla: Mancato Quorum", key=f"q_{s_row['id']}"):
                        notifica_squadra_annullamento(s_row['id'], s_row['titolo'], dt_v, "Mancato raggiungimento del contingente minimo operativo (quorum non raggiunto).")
                        run_query("UPDATE servizi SET stato = 'Annullato per Mancato Quorum' WHERE id = ?", (int(s_row["id"]),), fetch=False)
                        st.warning("Archiviata per quorum e squadra avvisata via email.")
                        st.rerun()
                        
                    st.write("")
                    col_del1, col_del2 = st.columns([3, 1])
                    if col_del2.button("🗑️ Elimina Definitivamente", key=f"hard_del_{s_row['id']}"):
                        notifica_squadra_annullamento(s_row['id'], s_row['titolo'], dt_v, "Cancellazione definitiva dell'ordine di servizio dai piani operativi.")
                        run_query("DELETE FROM adesioni WHERE servizio_id = ?", (int(s_row["id"]),), fetch=False)
                        run_query("DELETE FROM servizi WHERE id = ?", (int(s_row["id"]),), fetch=False)
                        st.info("Servizio eliminato e squadra notificata.")
                        st.rerun()

    # --- TAB ARCHIVIO DISTRETTUALE CON CANCELLAZIONE DEI TEST ---
    with tab_archivio:
        st.markdown("#### 🗃️ Registro Storico & Archivio Distrettuale")
        st.caption("Conserva e gestisce la memoria delle missioni svolte o annullate. Da qui puoi anche eliminare i dati di prova.")
        
        storico_servizi = run_query("""
            SELECT id, titolo, luogo, data, posti_richiesti, ore_servizio, stato 
            FROM servizi 
            WHERE stato != 'Programmato' 
            ORDER BY data DESC
        """)
        
        if storico_servizi.empty:
            st.info("Nessuna missione archiviata a registro.")
        else:
            col_t_btn1, col_t_btn2 = st.columns([3, 1])
            with col_t_btn2:
                if st.button("🧹 Svuota Tutto l'Archivio Storico", key="clean_all_archive"):
                    run_query("DELETE FROM adesioni WHERE servizio_id IN (SELECT id FROM servizi WHERE stato != 'Programmato')", fetch=False)
                    run_query("DELETE FROM servizi WHERE stato != 'Programmato'", fetch=False)
                    st.toast("Archivio storico completamente azzerato!")
                    st.rerun()

            st.write("")
            for _, r_arch in storico_servizi.iterrows():
                try:
                    d_arch_fmt = datetime.strptime(r_arch['data'], "%Y-%m-%d").strftime("%d/%m/%Y")
                except:
                    d_arch_fmt = r_arch['data']
                    
                col_a1, col_a2, col_a3 = st.columns([3, 1, 1])
                stato_lbl = r_arch['stato']
                if "Concluso" in stato_lbl:
                    badge_esito = f"🟢 **{stato_lbl}**"
                elif "Meteo" in stato_lbl:
                    badge_esito = f"🌧️ **{stato_lbl}**"
                elif "Quorum" in stato_lbl:
                    badge_esito = f"👥 **{stato_lbl}**"
                else:
                    badge_esito = f"⚪ **{stato_lbl}**"
                    
                col_a1.write(f"📁 **{r_arch['titolo']}** ({r_arch['luogo']}) — Data: `{d_arch_fmt}` | {r_arch['ore_servizio']}h")
                col_a2.write(badge_esito)
                
                if col_a3.button("🗑️ Elimina Record", key=f"del_arch_{r_arch['id']}"):
                    run_query("DELETE FROM adesioni WHERE servizio_id = ?", (int(r_arch['id']),), fetch=False)
                    run_query("DELETE FROM servizi WHERE id = ?", (int(r_arch['id']),), fetch=False)
                    st.toast(f"Record '{r_arch['titolo']}' rimosso definitivamente.")
                    st.rerun()

    with tab_volontari:
        st.markdown("#### Registrazione Membro / Inquadramento Istituzionale")
        
        macroarea_sel = st.selectbox(
            "1. Seleziona Macroarea Istituzionale",
            list(STRUTTURA_ISTITUZIONALE_SMOM_CISOM.keys())
        )
        gradi_disponibili = STRUTTURA_ISTITUZIONALE_SMOM_CISOM[macroarea_sel]
        
        with st.form("form_nuovo_membro"):
            col_n, col_e = st.columns(2)
            nome = col_n.text_input("Nome e Cognome")
            email = col_e.text_input("Indirizzo E-mail (per notifiche e memo)", placeholder="nome.cognome@email.it")
            
            col_g1, col_g2 = st.columns(2)
            grado_scelto = col_g1.selectbox("2. Grado / Titolo Ufficiale", gradi_disponibili)
            
            ruolo_operativo = col_g2.selectbox(
                "Funzione Operativa sul Campo",
                ["Nessuna (Rango Istituzionale / Rappresentanza)"] + STRUTTURA_ISTITUZIONALE_SMOM_CISOM["4. Corpo Operativo, Sanitario & Protezione Civile"]
            )
            
            qualifica_finale = grado_scelto
            if ruolo_operativo != "Nessuna (Rango Istituzionale / Rappresentanza)" and ruolo_operativo != grado_scelto:
                qualifica_finale += f" | {ruolo_operativo}"
                
            submit_reg = st.form_submit_button("Registra nel Ruolo Generale Ufficiale")
            if submit_reg and nome:
                email_clean = str(email).strip()
                run_query("INSERT INTO volontari (nome, email, macroarea, ruolo, attivo) VALUES (?, ?, ?, ?, 1)", 
                          (nome, email_clean, macroarea_sel, qualifica_finale), fetch=False)
                
                if email_clean and "@" in email_clean:
                    corpo_benvenuto = f"""
                    <div style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #0b0f17; color: #e2e8f0; padding: 26px; border-radius: 8px; max-width: 580px; margin: auto; border: 1px solid #1e293b;">
                        <div style="text-align: center; border-bottom: 2px solid #dc2626; padding-bottom: 14px; margin-bottom: 18px;">
                            <div style="font-size: 26px; line-height: 1; color: #dc2626;">✠</div>
                            <div style="font-size: 15px; font-weight: 800; color: #ef4444; letter-spacing: 2px; text-transform: uppercase; margin-top: 5px;">SOVRANO MILITARE ORDINE DI MALTA</div>
                            <div style="font-size: 12px; font-weight: 600; color: #94a3b8; letter-spacing: 1px;">CORPO ITALIANO DI SOCCORSO DELL'ORDINE DI MALTA</div>
                            <div style="font-size: 11px; font-weight: 700; color: #3b82f6; margin-top: 3px;">SEZIONE DI GROSSETO — REGISTRO UFFICIALE</div>
                        </div>
                        <p style="font-size: 14px; margin-bottom: 10px;">Gentile <strong>{nome}</strong>,</p>
                        <p style="font-size: 12px; color: #cbd5e1; margin-bottom: 14px;">
                            Si attesta l'avvenuta iscrizione a registro nel portale operativo <strong>Sovereign Zero Control Tower</strong>:
                        </p>
                        <div style="background-color: #111827; border: 1px solid #1f293d; border-radius: 6px; padding: 16px; margin: 16px 0;">
                            <div style="margin-bottom: 8px;"><strong style="color: #94a3b8;">🏛️ MACROAREA:</strong> <span style="font-weight: 700; color: #ffffff;">{macroarea_sel}</span></div>
                            <div style="margin-bottom: 8px;"><strong style="color: #94a3b8;">✠ RANGO / QUALIFICA:</strong> <span style="font-weight: 700; color: #ef4444;">{qualifica_finale}</span></div>
                            <div><strong style="color: #94a3b8;">✉️ RECAPITO NOTIFICHE:</strong> <span style="color: #38bdf8;">{email_clean}</span></div>
                        </div>
                        <div style="background-color: rgba(59, 130, 246, 0.08); border-left: 3px solid #3b82f6; padding: 8px 12px; border-radius: 4px; font-size: 12px; color: #93c5fd; margin-bottom: 18px;">
                            ℹ️ Il tuo profilo è ora operativo per la consultazione degli ordini di servizio e la disponibilità alle missioni.
                        </div>
                        <div style="border-top: 1px solid #1f293d; padding-top: 12px; font-size: 11px; color: #64748b; text-align: center;">
                            CISOM Sezione Grosseto — Servizio TLC & Sistemi Informativi
                        </div>
                    </div>
                    """
                    esito, dtl = invia_email_notifica(email_clean, "CISOM Grosseto: Conferma Registrazione nel Ruolo Ufficiale", corpo_benvenuto)
                    if esito:
                        st.success(f"Registrato con successo! E-mail di conferma inviata a {email_clean}")
                    else:
                        st.warning(f"Membro salvato a registro, avviso e-mail: {dtl}")
                else:
                    st.info(f"Registrato: {nome} [{qualifica_finale}] (Senza e-mail)")

                st.rerun()

        st.divider()
        st.markdown("#### 🛡️ Anagrafica & Gestione Membri")
        volontari_db = run_query("SELECT * FROM volontari ORDER BY attivo DESC, nome ASC")
        
        if volontari_db.empty:
            st.info("Nessun membro presente a registro.")
        else:
            for _, v in volontari_db.iterrows():
                col_v1, col_v2, col_v3 = st.columns([3, 1, 1])
                stato_txt = "🟢 Attivo" if v.get("attivo", 1) == 1 else "⚪ Disattivato (Storico conservato)"
                email_val = v.get("email", "") if hasattr(v, "get") else ""
                em_label = f" — ✉️ {email_val}" if email_val and str(email_val) != "None" else ""

                col_v1.write(f"👤 **{v['nome']}** — *{v['ruolo']}*{em_label} ({stato_txt})")
                
                if v.get("attivo", 1) == 1:
                    if col_v2.button("Disattiva", key=f"dis_{v['id']}"):
                        run_query("UPDATE volontari SET attivo = 0 WHERE id = ?", (int(v["id"]),), fetch=False)
                        if email_val and "@" in str(email_val):
                            corpo_sosp = f"""
                            <div style="font-family: Arial, sans-serif; background-color: #0b0f17; color: #e2e8f0; padding: 22px; border-radius: 8px; border: 1px solid #1e293b;">
                                <h3 style="color: #f59e0b; border-bottom: 2px solid #f59e0b; padding-bottom: 6px;">CISOM — STATO PROFILO SOSPESO</h3>
                                <p>Gentile <strong>{v['nome']}</strong>,</p>
                                <p>La Segreteria ha impostato il tuo profilo operativo come <strong>SOSPESO / DISATTIVATO</strong>.</p>
                                <p>Il tuo storico missioni e ore prestate resta custodito. Contatta il Direttivo per informazioni.</p>
                            </div>
                            """
                            invia_email_notifica(email_val, "CISOM Grosseto: Modifica Stato Profilo", corpo_sosp)
                        st.rerun()
                else:
                    if col_v2.button("Riattiva", key=f"riatt_{v['id']}"):
                        run_query("UPDATE volontari SET attivo = 1 WHERE id = ?", (int(v["id"]),), fetch=False)
                        if email_val and "@" in str(email_val):
                            corpo_riatt = f"""
                            <div style="font-family: Arial, sans-serif; background-color: #0b0f17; color: #e2e8f0; padding: 22px; border-radius: 8px; border: 1px solid #1e293b;">
                                <h3 style="color: #10b981; border-bottom: 2px solid #10b981; padding-bottom: 6px;">CISOM — PROFILO RIATTIVATO</h3>
                                <p>Gentile <strong>{v['nome']}</strong>,</p>
                                <p>Il tuo profilo operativo è stato <strong>RIATTIVATO</strong>. Puoi nuovamente dare disponibilità per le missioni.</p>
                            </div>
                            """
                            invia_email_notifica(email_val, "CISOM Grosseto: Profilo Riattivato", corpo_riatt)
                        st.rerun()
                
                if col_v3.button("Elimina Def.", key=f"del_def_{v['id']}"):
                    email_dest = email_val
                    nome_dest = v['nome']
                    if email_dest and "@" in str(email_dest):
                        corpo_canc = f"""
                        <div style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #0b0f17; color: #e2e8f0; padding: 26px; border-radius: 8px; max-width: 580px; margin: auto; border: 1px solid #1e293b;">
                            <div style="text-align: center; border-bottom: 2px solid #ef4444; padding-bottom: 14px; margin-bottom: 18px;">
                                <div style="font-size: 26px; line-height: 1; color: #ef4444;">✠</div>
                                <div style="font-size: 15px; font-weight: 800; color: #ef4444; letter-spacing: 2px; text-transform: uppercase; margin-top: 5px;">SOVRANO MILITARE ORDINE DI MALTA</div>
                                <div style="font-size: 12px; font-weight: 600; color: #94a3b8; letter-spacing: 1px;">CORPO ITALIANO DI SOCCORSO DELL'ORDINE DI MALTA</div>
                                <div style="font-size: 11px; font-weight: 700; color: #ef4444; margin-top: 3px;">NOTIFICA DE-REGISTRAZIONE UFFICIALE</div>
                            </div>
                            <p style="font-size: 14px;">Gentile <strong>{nome_dest}</strong>,</p>
                            <p style="font-size: 13px; color: #cbd5e1;">Si notifica l'avvenuta <strong>cancellazione definitiva</strong> del tuo profilo anagrafico dal Ruolo Generale della Sezione.</p>
                            <p style="font-size: 12px; color: #94a3b8;">Se la revoca è avvenuta per errore materiale o refuso di gestione, rispondi direttamente a questa comunicazione per consentire il ripristino immediato dei tuoi dati.</p>
                            <div style="border-top: 1px solid #1f293d; padding-top: 12px; font-size: 11px; color: #64748b; text-align: center; margin-top: 18px;">
                                CISOM Sezione Grosseto — Sovereign Zero Control Tower
                            </div>
                        </div>
                        """
                        invia_email_notifica(email_dest, "CISOM Grosseto: Cancellazione Registro Ruolo", corpo_canc)
                    
                    run_query("DELETE FROM adesioni WHERE volontario_id = ?", (int(v["id"]),), fetch=False)
                    run_query("DELETE FROM volontari WHERE id = ?", (int(v["id"]),), fetch=False)
                    st.rerun()

    with tab_presidi:
        st.markdown("#### 📍 Presidi Territoriali, Basi e Rete CISOM")

        vista_mappa = st.radio(
            "Seleziona Livello Operativo:",
            ["🔴 Presidi & Distaccamenti di Sezione (Locali)", "🇮🇹 Rete Nazionale & Sezioni Ufficiali", "🌐 Visione Complessiva"],
            horizontal=True
        )

        df_naz = pd.DataFrame(RETE_ISTITUZIONALE_CISOM)
        presidi_db = run_query("SELECT * FROM presidi ORDER BY sezione ASC, nome_presidio ASC")

        if vista_mappa == "🇮🇹 Rete Nazionale & Sezioni Ufficiali":
            st.caption("Visualizzazione dei Raggruppamenti Regionali e Sezioni Ufficiali CISOM in Italia")
            df_map_naz = df_naz[['lat', 'lon']].rename(columns={'lat': 'latitude', 'lon': 'longitude'})
            st.map(df_map_naz)
            st.dataframe(df_naz[['nome', 'tipo', 'livello']], width='stretch')

        elif vista_mappa == "🔴 Presidi & Distaccamenti di Sezione (Locali)":
            st.caption("Visualizzazione presidi, distaccamenti e basi operative censite per la Sezione")
            if not presidi_db.empty:
                df_map_loc = presidi_db[['latitudine', 'longitudine']].rename(columns={'latitudine': 'latitude', 'longitudine': 'longitude'})
                st.map(df_map_loc)
            else:
                st.info("Nessun distaccamento locale censito a registro.")

        else:
            st.caption("Panoramica Integrata: Rete Istituzionale Nazionale + Presidi Locali di Sezione")
            punti = []
            for _, r in df_naz.iterrows():
                punti.append({"latitude": r["lat"], "longitude": r["lon"]})
            if not presidi_db.empty:
                for _, r in presidi_db.iterrows():
                    punti.append({"latitude": r["latitudine"], "longitude": r["longitudine"]})
            if punti:
                st.map(pd.DataFrame(punti))

        st.divider()
        st.markdown("##### ➕ Registra Nuovo Presidio / Distaccamento di Sezione")
        with st.form("form_nuovo_presidio"):
            col_amb, col_n = st.columns([1, 2])
            p_sezione = col_amb.selectbox(
                "Ambito Operativo / Sezione",
                [
                    "CISOM Sezione Grosseto",
                    "Distaccamento Costiero / Follonica",
                    "Presidio Amiata / Castell'Azzara",
                    "Presidio Argentario",
                    "Altro Ambito Territoriale"
                ]
            )
            p_nome = col_n.text_input("Nome Presidio / Base Operativa", placeholder="es. Distaccamento Follonica, Base Logistica")
            
            col_la, col_lo = st.columns(2)
            p_lat = col_la.number_input("Latitudine", value=42.7634, format="%.5f")
            p_lon = col_lo.number_input("Longitudine", value=11.1118, format="%.5f")
            
            if st.form_submit_button("Aggiungi Presidio") and p_nome:
                run_query(
                    "INSERT OR REPLACE INTO presidi (sezione, nome_presidio, latitudine, longitudine) VALUES (?, ?, ?, ?)", 
                    (p_sezione, p_nome, p_lat, p_lon), 
                    fetch=False
                )
                st.success(f"Presidio '{p_nome}' registrato con successo!")
                st.rerun()

        st.divider()
        if not presidi_db.empty:
            st.markdown("##### 📋 Elenco Basi e Presidi di Sezione Censiti")
            for _, pr in presidi_db.iterrows():
                cp1, cp2 = st.columns([4, 1])
                sez_txt = f"[{pr['sezione']}] " if 'sezione' in pr and pr['sezione'] else ""
                cp1.write(f"📍 **{sez_txt}{pr['nome_presidio']}** — Coord: `{pr['latitudine']:.4f}, {pr['longitudine']:.4f}`")
                if cp2.button("Rimuovi Presidio", key=f"del_pres_{pr['id']}"):
                    run_query("DELETE FROM presidi WHERE id = ?", (int(pr["id"]),), fetch=False)
                    st.rerun()
