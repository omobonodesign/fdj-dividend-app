# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import os # Importa il modulo os per verificare l'esistenza del file

# --- Configurazione Pagina ---
st.set_page_config(
    page_title="Analisi Dividendi FDJ",
    page_icon="💰",
    layout="wide" # Utilizza l'intera larghezza della pagina
)

# --- Dati Chiave Estratti (da Testo e PDF) ---
TICKER = "FDJ.PA"
NOME_SOCIETA = "Française des Jeux"
ULTIMO_DPS_PAGATO_VAL = 1.78 # Relativo all'esercizio 2023 [source: 4]
ANNO_ULTIMO_DPS = 2023
PREZZO_RIFERIMENTO_APPROX = 30.0 # Prezzo approssimativo menzionato nel testo [source: 13]
POLITICA_PAYOUT = "80-90% Utile Netto (dal 2022)" # [source: 3]
DPS_ATTESO_2024_VAL = 2.05 # [source: 54]
CRESCITA_ATTESA_DPS_2024 = "+15%" # [source: 54]
IMPATTO_KINDRED_DIVIDENDO = "+10% addizionale dal 2026 (utile 2025)" # [source: 57]
RISCHIO_TASSE_2025 = "€90M impatto EBITDA/anno da metà 2025" # [source: 180, 181]
MITIGAZIONE_TASSE = "Piani per compensare impatto entro 2027" # [source: 183]

# Dati storici Dividendo Per Azione (DPS) [source: 4, 5, 6]
dps_storico_data = {
    'Anno Esercizio': [2019, 2020, 2021, 2022, 2023],
    'DPS (€)': [0.45, 0.90, 1.24, 1.37, 1.78]
}
df_dps = pd.DataFrame(dps_storico_data)

# Dati Finanziari Chiave (Estratti da PDF - 31/12 date) [source: 300, 306, 307]
# Usiamo 2021, 2022, 2023, LTM (che nel PDF è colonna 31/12/24)
fin_data = {
    'Metrica': [
        'Ricavi Totali (€M)',
        'Utile Netto (€M)',
        'EPS Diluito (€)',
        'Cash Flow Operativo (CFO, €M)',
        'Capex (€M)',
        'Free Cash Flow (FCF, €M)',
        'Debito Netto / EBITDA (Leva)',
        'Dividendo per Azione (DPS, €)'
    ],
    '2021': [
        2255.7, # Revenue
        294.2,  # Net Income
        1.54,   # Diluted EPS
        602.9,  # CFO
        -75.5,  # Capex (negativo nel PDF Cash Flow, ma è un outflow)
        527.4,  # FCF (CFO + Capex - assumendo Capex sia negativo)
        "Cassa Netta", # FDJ aveva cassa netta fino a fine 2023 [source: 254]
        1.24    # DPS [source: 9]
        ],
    '2022': [
        2461.1, # Revenue
        307.9,  # Net Income
        1.61,   # Diluted EPS
        406.1,  # CFO
        -104.1, # Capex
        302.0,  # FCF
        "Cassa Netta", # [source: 254]
        1.37    # DPS [source: 9]
        ],
    '2023': [
        2621.5, # Revenue
        425.1,  # Net Income
        2.23,   # Diluted EPS
        628.9,  # CFO
        -124.7, # Capex
        504.2,  # FCF
        "Cassa Netta", # Fine 2023 [source: 254]
        1.78    # DPS [source: 10]
        ],
     # LTM nel PDF corrisponde alla colonna 31/12/24
     # Nota: L'utile netto 2024 LTM nel PDF (398.8) è inferiore al 2023 (425.1).
     # La leva è indicata come ~2x post-Kindred (2025) [source: 263]
    'LTM (31/12/24 PDF)': [
        3065.1, # Revenue
        398.8,  # Net Income
        2.16,   # Diluted EPS
        577.0,  # CFO
        -149.9, # Capex
        427.1,  # FCF
        "~2.0-2.2x (prospettico post-Kindred)", # [source: 263]
        "2.05 (atteso ex. 2024)" # [source: 54]
        ]
}
df_fin = pd.DataFrame(fin_data)

# Calcolo Trailing Dividend Yield
trailing_yield = (ULTIMO_DPS_PAGATO_VAL / PREZZO_RIFERIMENTO_APPROX) * 100 if PREZZO_RIFERIMENTO_APPROX else None

# --- Titolo e Header ---
st.title(f"💰 Analisi Dividendi: {NOME_SOCIETA} ({TICKER})")
st.caption(f"Analisi aggiornata al: April 15, 2024. Dati finanziari storici fino a LTM (31/12/2024 dal PDF).")
st.markdown("---")

# --- Metriche Chiave Dividendo ---
st.subheader("📊 Indicatori Chiave del Dividendo")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label=f"Ultimo DPS Pagato (Esercizio {ANNO_ULTIMO_DPS})",
        value=f"€ {ULTIMO_DPS_PAGATO_VAL:.2f}",
        help="Dividendo pagato nel 2024 relativo all'esercizio 2023."
    )
with col2:
    st.metric(
        label=f"Dividend Yield (Trailing Approx.)",
        value=f"{trailing_yield:.1f}%" if trailing_yield is not None else "N/A",
        help=f"Basato sull'ultimo DPS (€{ULTIMO_DPS_PAGATO_VAL:.2f}) e un prezzo di riferimento approssimativo di €{PREZZO_RIFERIMENTO_APPROX:.2f}. Il testo menziona stime forward yield del 6-7% [source: 13, 14]."
    )
with col3:
    st.metric(
        label="Politica di Payout",
        value=POLITICA_PAYOUT,
        help="Politica dichiarata dalla società per la distribuzione degli utili netti. [source: 3]"
    )
with col4:
    st.metric(
        label="DPS Atteso (Esercizio 2024)",
        value=f"€ {DPS_ATTESO_2024_VAL:.2f} ({CRESCITA_ATTESA_DPS_2024})",
        help=f"Previsione basata su analisi [source: 54]. Ulteriore potenziale rialzo {IMPATTO_KINDRED_DIVIDENDO} [source: 57]."
    )
st.markdown("---")

# --- Grafico Storico DPS ---
st.subheader("📈 Crescita Storica del Dividendo per Azione (DPS)")
fig_dps = px.line(
    df_dps,
    x='Anno Esercizio',
    y='DPS (€)',
    title="Andamento DPS FDJ (Esercizi 2019-2023)",
    markers=True,
    text='DPS (€)' # Mostra i valori sul grafico
)
fig_dps.update_traces(textposition="top center")
fig_dps.update_layout(xaxis_title="Anno Esercizio Fiscale", yaxis_title="Dividendo per Azione (€)")
st.plotly_chart(fig_dps, use_container_width=True)
st.caption("Fonte: Dati estratti da Analisi_FDJ.txt [source: 4, 5, 6] e TIKR PDF [source: 300]. Nota la forte crescita post-IPO.")
st.markdown("---")

# --- Tabella Finanziaria Riassuntiva ---
st.subheader("🔢 Tabella Finanziaria Riassuntiva")
st.dataframe(df_fin.set_index('Metrica'), use_container_width=True)
st.caption("Fonte: Dati estratti da TIKR PDF (colonna 31/12/24 usata come LTM) [source: 300, 303, 306]. FCF calcolato come CFO - Capex. Leva Finanziaria indicata come da testo analisi. L'Utile Netto LTM 2024 è risultato inferiore al 2023 nel PDF.")
st.markdown("---")

# --- Sezioni Analisi Testuale ---
st.subheader("📝 Analisi Dettagliata (dal file Analisi_FDJ.txt)")

# Legge il contenuto del file di analisi
analysis_file_path = 'Analisi_FDJ.txt'
analysis_content = ""
# Verifica se il file esiste prima di provare a leggerlo
if os.path.exists(analysis_file_path):
    try:
        with open(analysis_file_path, 'r', encoding='utf-8') as f:
            analysis_content = f.read()
            # Sostituisce i tag [source: ...] con un formato più leggibile o li rimuove
            import re
            analysis_content = re.sub(r'\s*\[source:\s*\d+.*?\]', '', analysis_content) # Rimuove i tag source
    except FileNotFoundError:
        st.error(f"Errore: File '{analysis_file_path}' non trovato. Assicurati che sia nella stessa cartella dello script.")
        analysis_content = "Contenuto dell'analisi non disponibile."
    except Exception as e:
        st.error(f"Errore nella lettura del file '{analysis_file_path}': {e}")
        analysis_content = "Errore nel caricamento del contenuto dell'analisi."
else:
    st.warning(f"Attenzione: File '{analysis_file_path}' non trovato. L'analisi testuale non può essere visualizzata.")
    analysis_content = "Contenuto dell'analisi non disponibile (file non trovato)."


# Suddivisione approssimativa del contenuto basata sui titoli nell'analisi
# Nota: Questa è una suddivisione euristica, potrebbe necessitare aggiustamenti
sections = {}
current_section = "Introduzione"
sections[current_section] = ""

# Regex per trovare i titoli principali (## Titolo o # Titolo) e i sottotitoli numerati (## N. Titolo)
title_pattern = re.compile(r"^(#+\s*\d*\.?\s*\*?.*?\*?)$", re.MULTILINE)

last_index = 0
for match in title_pattern.finditer(analysis_content):
    title = match.group(1).strip().replace('#', '').replace('*','').strip()
    start_index = match.start()

    # Aggiunge il testo precedente alla sezione corrente
    sections[current_section] += analysis_content[last_index:start_index].strip()

    # Pulisce il titolo da eventuali numeri iniziali e punti per creare la chiave
    clean_title = re.sub(r"^\d+\.\s+", "", title)
    current_section = clean_title
    sections[current_section] = "" # Inizia una nuova sezione
    last_index = match.end()

# Aggiunge l'ultimo pezzo di testo all'ultima sezione
sections[current_section] += analysis_content[last_index:].strip()

# Visualizza le sezioni con expander
for title, content in sections.items():
    if content.strip(): # Mostra solo sezioni con contenuto
        with st.expander(f"**{title}**", expanded=(title=="Introduzione" or "Dividendi storici" in title)): # Espande le prime sezioni di default
            st.markdown(content, unsafe_allow_html=True)


# --- Conclusioni Specifiche per Investitore Dividend ---
st.subheader("🎯 Conclusioni per l'Investitore Orientato ai Dividendi")
st.markdown(f"""
Basato sull'analisi fornita:

**Punti di Forza (Pro-Dividendo):**
* ✅ **Politica Dividendi Generosa:** Payout target 80-90% dell'utile netto. [source: 3]
* ✅ **Storico di Crescita Robusto:** Il DPS è aumentato significativamente dall'IPO (da €0.45 a €1.78). [source: 4, 5]
* ✅ **Yield Attraente:** Rendimento attuale (trailing ~5.9%, forward stimato 6-7%) superiore alla media di mercato. [source: 13, 14, 15]
* ✅ **Flussi di Cassa Stabili:** Il core business delle lotterie (monopolio fino 2044) garantisce cassa prevedibile e resiliente. [source: 65, 67, 69, 79]
* ✅ **Prospettive di Crescita Dividendo:** Atteso aumento per il 2024 (€2.05) e potenziale boost da Kindred nel 2026. [source: 54, 57]
* ✅ **Solidità Finanziaria:** Rating Investment Grade (Baa1 Moody's) [source: 78, 259] e leva finanziaria gestibile post-acquisizioni (~2x). [source: 263, 266]

**Rischi e Considerazioni (Contro-Dividendo):**
* ⚠️ **Nuove Tasse 2025:** Impatto negativo atteso di **€90M/anno sull'EBITDA** da metà 2025, che potrebbe temporaneamente frenare la crescita degli utili/dividendi. [source: 173, 180, 181, 185]
* ⚠️ **Piani di Mitigazione Tasse:** La società punta a compensare l'impatto fiscale entro il 2027, ma l'efficacia è da verificare. [source: 183]
* ⚠️ **Rischi Integrazione M&A:** L'acquisizione di Kindred è trasformativa ma comporta rischi di esecuzione e integrazione. [source: 45, 117, 118]
* ⚠️ **Concorrenza Online:** Il segmento scommesse/giochi online è competitivo e ha margini più bassi e volatili rispetto alle lotterie. [source: 102, 105, 110]
* ⚠️ **Rischio Normativo:** Oltre alle tasse, il settore è soggetto a cambiamenti regolatori in Francia e UE (es. restrizioni pubblicità, revisione concessioni). [source: 112, 191, 198]

**In Sintesi:** FDJ presenta un profilo interessante per l'investitore da dividendo grazie a yield elevato, crescita storica e solidità del business principale. Tuttavia, l'impatto delle nuove tasse nel 2025 è un fattore chiave da monitorare attentamente, così come il successo dell'integrazione di Kindred per sostenere la crescita futura del dividendo.
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Disclaimer: Questa è un'analisi basata sui dati forniti. Non costituisce consulenza finanziaria. Effettuare sempre le proprie ricerche.")