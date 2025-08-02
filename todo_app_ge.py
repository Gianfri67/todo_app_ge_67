import streamlit as st
import json
import os
from datetime import date, datetime
from uuid import uuid4

FILE_TASK = "attivita.json"
FILE_CONTESTI = "contesti.json"

# Funzione di caricamento sicuro JSON
def carica_json_sicuro(percorso, default):
    if os.path.exists(percorso):
        try:
            with open(percorso, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return default
    return default

# Funzione di caricamento dei colori/contesti personalizzati
def carica_contesti():
    return carica_json_sicuro(FILE_CONTESTI, {
        "Evomotor": "#D1E8FF",
        "Personale": "#FFD1DC",
        "Famiglia": "#E2F0CB",
        "Futura": "#E8DAFF",
        "Investimenti": "#FFFACD"
    })

def salva_contesti(dati):
    with open(FILE_CONTESTI, "w") as f:
        json.dump(dati, f, indent=2, ensure_ascii=False)

def genera_colore_unico(existing_colors):
    from random import randint
    while True:
        colore = f"#{randint(0, 255):02X}{randint(0, 255):02X}{randint(0, 255):02X}"
        if colore not in existing_colors:
            return colore

COLORI_CONTESTO = carica_contesti()

# Funzioni di gestione dati

def carica_attivita():
    return carica_json_sicuro(FILE_TASK, [])

def salva_attivita(attivita):
    with open(FILE_TASK, "w") as f:
        json.dump(attivita, f, indent=2, ensure_ascii=False)

def ordina_attivita(attivita):
    return sorted(attivita, key=lambda x: x["scadenza"])

def aggiorna_scadenze(attivita):
    oggi = date.today()
    aggiornato = False
    for a in attivita:
        if a["stato"] == "attiva" and datetime.fromisoformat(a["scadenza"]).date() < oggi:
            a["stato"] = "scaduta"
            aggiornato = True
    return attivita, aggiornato

# Interfaccia Streamlit
st.set_page_config(page_title="Gestione Attività - Gianmario")

# Adattamento dinamico stile per dispositivi
st.markdown("""
    <style>
    @media screen and (max-width: 600px) {
        h1, .element-container h1 { font-size: 22px !important; }
        h2, .element-container h2 { font-size: 22px !important; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🗂️ Gestione Attività - Gianmario")

# Navigazione tra pagine
pagina = st.sidebar.selectbox("Naviga tra le sezioni", ["Agenda", "Completate", "Eliminate", "Contesti"])

attivita = carica_attivita()
attivita, notifica_scadenza = aggiorna_scadenze(attivita)
salva_attivita(attivita)

if notifica_scadenza:
    st.toast("⚠️ Alcune attività sono passate a scadute")

# Filtro per contesto
contesto_filtro = st.sidebar.selectbox("Filtra per contesto", ["Tutti"] + list(set(a["contesto"] for a in attivita)))

def filtra_per_contesto(lista):
    if contesto_filtro == "Tutti":
        return lista
    return [a for a in lista if a["contesto"] == contesto_filtro]

# Pagina AGENDA
if pagina == "Agenda":
    st.subheader("➕ Aggiungi nuova attività")

    with st.form("aggiungi_attivita"):
        titolo = st.text_input("Titolo attività")
        descrizione = st.text_area("Descrizione attività")
        contesto = st.selectbox("Contesto", list(COLORI_CONTESTO.keys()))
        scadenza = st.date_input("Data scadenza")
        submitted = st.form_submit_button("Aggiungi attività")

        if submitted:
            if not titolo or not contesto or not scadenza:
                st.error("Compila tutti i campi obbligatori (Titolo, Contesto, Scadenza).")
            else:
                nuova = {
                    "id": str(uuid4()),
                    "titolo": titolo,
                    "descrizione": descrizione,
                    "contesto": contesto,
                    "scadenza": scadenza.isoformat(),
                    "stato": "attiva"
                }
                attivita.append(nuova)
                salva_attivita(attivita)
                st.success("Attività aggiunta con successo.")
                st.rerun()

    st.subheader("📌 Attività attive")
    attive = filtra_per_contesto(ordina_attivita([a for a in attivita if a["stato"] == "attiva"]))
    for a in attive:
        with st.container(border=True):
            st.markdown(f"<div style='background-color:{COLORI_CONTESTO.get(a['contesto'], '#F0F0F0')}; padding: 10px; border-radius: 8px;'>", unsafe_allow_html=True)
            st.markdown(f"**{a['titolo']}**")
            st.caption(a["descrizione"])
            st.write(f"_Scadenza: {a['scadenza']}_")
            col1, col2 = st.columns(2)
            if col1.button("✅ Fatto", key="done" + a["id"]):
                a["stato"] = "completata"
                salva_attivita(attivita)
                st.rerun()
            if col2.button("🗑️ Elimina", key="del" + a["id"]):
                a["stato"] = "eliminata"
                salva_attivita(attivita)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("⏰ Attività scadute")
    scadute = filtra_per_contesto(ordina_attivita([a for a in attivita if a["stato"] == "scaduta"]))
    for a in scadute:
        with st.container(border=True):
            st.markdown(f"<div style='background-color:{COLORI_CONTESTO.get(a['contesto'], '#F0F0F0')}; padding: 10px; border-radius: 8px;'>", unsafe_allow_html=True)
            st.markdown(f"**{a['titolo']}**")
            st.caption(a["descrizione"])
            st.write(f"_Scadenza: {a['scadenza']}_")
            col1, col2 = st.columns(2)
            if col1.button("✅ Fatto", key="done_scaduta" + a["id"]):
                a["stato"] = "completata"
                salva_attivita(attivita)
                st.rerun()
            if col2.button("🗑️ Elimina", key="del_scaduta" + a["id"]):
                a["stato"] = "eliminata"
                salva_attivita(attivita)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# Pagina COMPLETATE
elif pagina == "Completate":
    st.subheader("✅ Attività completate")
    completate = filtra_per_contesto(ordina_attivita([a for a in attivita if a["stato"] == "completata"]))
    for a in completate:
        with st.container():
            st.markdown(f"**{a['titolo']}**")
            st.caption(a["descrizione"])
            st.write(f"_Completata il: {a['scadenza']}_")
            if st.button("🔁 Ripristina", key="ripr_comp" + a["id"]):
                a["stato"] = "attiva"
                salva_attivita(attivita)
                st.rerun()

# Pagina ELIMINATE
elif pagina == "Eliminate":
    st.subheader("🗑️ Attività eliminate")
    eliminate = filtra_per_contesto(ordina_attivita([a for a in attivita if a["stato"] == "eliminata"]))
    for a in eliminate:
        with st.container():
            st.markdown(f"**{a['titolo']}**")
            st.caption(a["descrizione"])
            st.write(f"_Scadenza originale: {a['scadenza']}_")
            if st.button("🔁 Ripristina", key="ripr_elim" + a["id"]):
                a["stato"] = "attiva"
                salva_attivita(attivita)
                st.rerun()

# Pagina CONTESTI
elif pagina == "Contesti":
    st.subheader("🎨 Personalizza contesti")
    contesti_keys = list(COLORI_CONTESTO.keys())
    nuovo_nome = st.text_input("Aggiungi nuovo contesto")
    nuovo_colore = st.color_picker("Scegli colore", value=genera_colore_unico(COLORI_CONTESTO.values()))
    if st.button("➕ Aggiungi contesto") and nuovo_nome:
        if nuovo_nome in COLORI_CONTESTO:
            st.warning("Contesto già esistente.")
        elif nuovo_colore in COLORI_CONTESTO.values():
            st.warning("Colore già utilizzato.")
        else:
            COLORI_CONTESTO[nuovo_nome] = nuovo_colore
            salva_contesti(COLORI_CONTESTO)
            st.success("Contesto aggiunto con successo.")
            st.rerun()

    for nome in contesti_keys:
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(nome)
        nuovo_valore = col2.color_picker("", COLORI_CONTESTO[nome], key="picker" + nome)
        if nuovo_valore != COLORI_CONTESTO[nome]:
            if nuovo_valore in COLORI_CONTESTO.values():
                st.warning("Colore già utilizzato da un altro contesto.")
            else:
                COLORI_CONTESTO[nome] = nuovo_valore
                salva_contesti(COLORI_CONTESTO)
        # Protezione da eliminazione se usato
        if any(a["contesto"] == nome for a in attivita):
            col3.markdown("🔒")
        else:
            if col3.button("❌", key="del_contesto" + nome):
                del COLORI_CONTESTO[nome]
                salva_contesti(COLORI_CONTESTO)
                st.rerun()
