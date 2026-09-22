import streamlit as st
import pandas as pd
from datetime import date
import importlib
import database as db

# Wymuszenie przeładowania modułu bazy danych (zapobiega błędom pamięci podręcznej w chmurze)
importlib.reload(db)

db.init_db()

st.set_page_config(page_title="Zarządzanie Flotą", layout="wide")

# --- ZARZĄDZANIE SESJĄ LOGOWANIA ---
if 'zalogowany' not in st.session_state:
    st.session_state['zalogowany'] = False
if 'rola' not in st.session_state:
    st.session_state['rola'] = None
if 'uzytkownik' not in st.session_state:
    st.session_state['uzytkownik'] = None

# -----------------------------------------
# EKRAN LOGOWANIA (jeśli niezalogowany)
# -----------------------------------------
if not st.session_state['zalogowany']:
    st.title("🔐 Logowanie do Systemu Floty")
    
    with st.form("form_login"):
        login_input = st.text_input("Użytkownik")
        haslo_input = st.text_input("Hasło", type="password")
        przycisk_zaloguj = st.form_submit_button("Zaloguj się")
        
        if przycisk_zaloguj:
            rola = db.zaloguj_uzytkownika(login_input, haslo_input)
            if rola:
                st.session_state['zalogowany'] = True
                st.session_state['rola'] = rola
                st.session_state['uzytkownik'] = login_input
                st.success(f"Zalogowano pomyślnie jako: {login_input}")
                st.rerun()
            else:
                st.error("Nieprawidłowy login lub hasło!")
                
    st.info("Domyślne dane dostępowe:\n- **Admin:** login `admin` / hasło `admin123`\n- **Spedytor (tylko odczyt):** login `spedytor` / hasło `spedytor123`")

# -----------------------------------------
# APLIKACJA GŁÓWNA (po zalogowaniu)
# -----------------------------------------
else:
    # Pasek boczny – powitanie i wylogowanie
    st.sidebar.write(f"👤 Zalogowany: **{st.session_state['uzytkownik']}**")
    st.sidebar.write(f"🔑 Rola: **{st.session_state['rola'].upper()}**")
    if st.sidebar.button("🚪 Wyloguj się"):
        st.session_state['zalogowany'] = False
        st.session_state['rola'] = None
        st.session_state['uzytkownik'] = None
        st.rerun()
        
    st.sidebar.markdown("---")
    
    st.title("🚚 System Zarządzania Flotą i Dokumentami")

    zakladka = st.sidebar.radio(
        "Menu główne:",
        ["Pulpit i Alerty ⚠️", "Kierowcy 👤", "Ciągniki 🚛", "Naczepy 📦", "Inne Pojazdy 🚗"]
    )

    jest_adminem = (st.session_state['rola'] == 'admin')

    # -----------------------------------------
    # KIEROWCY
    # -----------------------------------------
    if zakladka == "Kierowcy 👤":
        st.subheader("Baza Kierowców")
        
        # Tylko Admin widzi formularz dodawania!
        if jest_adminem:
            with st.expander("➕ Dodaj nowego kierowcę"):
                with st.form("form_kierowca", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        imie = st.text_input("Imię i nazwisko")
                        pesel = st.text_input("PESEL")
                        nr_pj = st.text_input("Numer prawa jazdy")
                        waznosc_karty = st.date_input("Ważność karty kierowcy")
                    with col2:
                        typ_doc = st.selectbox("Typ dokumentu tożsamości", ["Paszport", "Dowód osobisty"])
                        nr_doc = st.text_input("Numer dokumentu")
                        waznosc_doc = st.date_input("Ważność dokumentu tożsamości")
                        
                    if st.form_submit_button("Zapisz kierowcę"):
                        if imie:
                            db.dodaj_kierowce(imie, pesel, nr_pj, typ_doc, nr_doc, waznosc_doc, waznosc_karty)
                            st.success(f"Dodano kierowcę: {imie}")
                            st.rerun()
                        else:
                            st.error("Uzupełnij imię i nazwisko!")

        st.write("### Lista Kierowców")
        df = db.pobierz_kierowcow()
        st.dataframe(df, use_container_width=True, hide_index=True)

    # -----------------------------------------
    # CIĄGNIKI
    # -----------------------------------------
    elif zakladka == "Ciągniki 🚛":
        st.subheader("Ciągniki Siodłowe")
        
        if jest_adminem:
            with st.expander("➕ Dodaj ciągnik"):
                with st.form("form_ciagnik", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        nr_rej = st.text_input("Numer rejestracyjny")
                        vin = st.text_input("Numer VIN")
                    with col2:
                        przeglad = st.date_input("Termin przeglądu technicznego")
                        oc = st.date_input("Termin ubezpieczenia OC")
                        
                    if st.form_submit_button("Zapisz ciągnik"):
                        if nr_rej:
                            db.dodaj_ciagnik(nr_rej, vin, przeglad, oc)
                            st.success(f"Dodano ciągnik: {nr_rej}")
                            st.rerun()
                        else:
                            st.error("Wpisz numer rejestracyjny!")

        st.write("### Lista Ciągników")
        df = db.pobierz_ciagniki()
        st.dataframe(df, use_container_width=True, hide_index=True)

    # -----------------------------------------
    # NACZEPY
    # -----------------------------------------
    elif zakladka == "Naczepy 📦":
        st.subheader("Naczepy")
        
        if jest_adminem:
            with st.expander("➕ Dodaj naczepę"):
                with st.form("form_naczepa", clear_on_submit=True):
                    nr_rej = st.text_input("Numer rejestracyjny")
                    przeglad = st.date_input("Termin przeglądu technicznego")
                    oc = st.date_input("Termin ubezpieczenia OC")
                        
                    if st.form_submit_button("Zapisz naczepę"):
                        if nr_rej:
                            db.dodaj_naczepe(nr_rej, przeglad, oc)
                            st.success(f"Dodano naczepę: {nr_rej}")
                            st.rerun()
                        else:
                            st.error("Wpisz numer rejestracyjny!")

        st.write("### Lista Naczep")
        df = db.pobierz_naczepy()
        st.dataframe(df, use_container_width=True, hide_index=True)

    # -----------------------------------------
    # INNE POJAZDY
    # -----------------------------------------
    elif zakladka == "Inne Pojazdy 🚗":
        st.subheader("Inne Pojazdy (Osobowe, Busy, Przyczepy)")
        
        if jest_adminem:
            with st.expander("➕ Dodaj inny pojazd"):
                with st.form("form_inny", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        typ = st.selectbox("Typ pojazdu", ["Osobowy", "Bus", "Przyczepa", "Inny"])
                        nr_rej = st.text_input("Numer rejestracyjny")
                        vin = st.text_input("Numer VIN (opcjonalnie)")
                    with col2:
                        przeglad = st.date_input("Termin przeglądu technicznego")
                        oc = st.date_input("Termin ubezpieczenia OC")
                        
                    if st.form_submit_button("Zapisz pojazd"):
                        if nr_rej:
                            db.dodaj_inny_pojazd(typ, nr_rej, vin, przeglad, oc)
                            st.success(f"Dodano pojazd: {nr_rej}")
                            st.rerun()
                        else:
                            st.error("Wpisz numer rejestracyjny!")

        st.write("### Lista Innych Pojazdów")
        df = db.pobierz_inne_pojazdy()
        st.dataframe(df, use_container_width=True, hide_index=True)

    # -----------------------------------------
    # PULPIT I ALERTY
    # -----------------------------------------
    elif zakladka == "Pulpit i Alerty ⚠️":
        st.subheader("Centrum powiadomień o wygasających terminach (30 dni)")
        dzisiaj = date.today()
        wszystko_ok = True

        df_k = db.pobierz_kierowcow()
        if not df_k.empty:
            for _, row in df_k.iterrows():
                if row['waznosc_dokumentu']:
                    dt_doc = pd.to_datetime(row['waznosc_dokumentu']).date()
                    dni_doc = (dt_doc - dzisiaj).days
                    if dni_doc <= 30:
                        st.warning(f"👤 **{row['imie_nazwisko']}** – Ważność dokumentu ({row['typ_dokumentu']}) kończy się za {dni_doc} dni! ({dt_doc})")
                        wszystko_ok = False

                if row['waznosc_karty_kierowcy']:
                    dt_karta = pd.to_datetime(row['waznosc_karty_kierowcy']).date()
                    dni_karta = (dt_karta - dzisiaj).days
                    if dni_karta <= 30:
                        st.warning(f"💳 **{row['imie_nazwisko']}** – Ważność **Karty Kierowcy** kończy się za {dni_karta} dni! ({dt_karta})")
                        wszystko_ok = False

        df_c = db.pobierz_ciagniki()
        if not df_c.empty:
            for _, row in df_c.iterrows():
                dt_przeglad = pd.to_datetime(row['przeglad_data']).date()
                dni_przeglad = (dt_przeglad - dzisiaj).days
                if dni_przeglad <= 30:
                    st.warning(f"🚛 **Ciągnik {row['nr_rej']}** – Przegląd kończy się za {dni_przeglad} dni! ({dt_przeglad})")
                    wszystko_ok = False

                dt_oc = pd.to_datetime(row['oc_data']).date()
                dni_oc = (dt_oc - dzisiaj).days
                if dni_oc <= 30:
                    st.warning(f"🛡️ **Ciągnik {row['nr_rej']}** – Ubezpieczenie OC kończy się za {dni_oc} dni! ({dt_oc})")
                    wszystko_ok = False

        df_n = db.pobierz_naczepy()
        if not df_n.empty:
            for _, row in df_n.iterrows():
                dt_przeglad = pd.to_datetime(row['przeglad_data']).date()
                dni_przeglad = (dt_przeglad - dzisiaj).days
                if dni_przeglad <= 30:
                    st.warning(f"📦 **Naczepa {row['nr_rej']}** – Przegląd kończy się za {dni_przeglad} dni! ({dt_przeglad})")
                    wszystko_ok = False

                dt_oc = pd.to_datetime(row['oc_data']).date()
                dni_oc = (dt_oc - dzisiaj).days
                if dni_oc <= 30:
                    st.warning(f"🛡️ **Naczepa {row['nr_rej']}** – Ubezpieczenie OC kończy się za {dni_oc} dni! ({dt_oc})")
                    wszystko_ok = False

        df_i = db.pobierz_inne_pojazdy()
        if not df_i.empty:
            for _, row in df_i.iterrows():
                dt_przeglad = pd.to_datetime(row['przeglad_data']).date()
                dni_przeglad = (dt_przeglad - dzisiaj).days
                if dni_przeglad <= 30:
                    st.warning(f"🚗 **{row['typ_pojazdu']} {row['nr_rej']}** – Przegląd kończy się za {dni_przeglad} dni! ({dt_przeglad})")
                    wszystko_ok = False

        if wszystko_ok:
            st.success("Wszystkie dokumenty, karty kierowców, ubezpieczenia i przeglądy są w pełni aktualne! 🎉")