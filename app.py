import streamlit as st
import pandas as pd
from datetime import date, datetime
import importlib
import database as db

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

# --- EKRAN LOGOWANIA ---
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
                
    st.info("Domyślne dane dostępowe:\n- **Admin:** login `admin` / hasło `admin123`\n- **Spedytor:** login `spedytor` / hasło `spedytor123`")

# --- APLIKACJA GŁÓWNA ---
else:
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

    # Helper do parsowania dat
    def parse_date(d_val):
        if pd.isna(d_val) or not d_val:
            return date.today()
        if isinstance(d_val, str):
            return datetime.strptime(d_val, "%Y-%m-%d").date()
        return d_val

    # -----------------------------------------
    # KIEROWCY
    # -----------------------------------------
    if zakladka == "Kierowcy 👤":
        st.subheader("Baza Kierowców")
        df = db.pobierz_kierowcow()

        if jest_adminem:
            col_a, col_b = st.columns(2)
            
            # Dodawanie
            with col_a:
                with st.expander("➕ Dodaj nowego kierowcę"):
                    with st.form("form_kierowca_add", clear_on_submit=True):
                        imie = st.text_input("Imię i nazwisko")
                        pesel = st.text_input("PESEL")
                        nr_pj = st.text_input("Numer prawa jazdy")
                        waznosc_karty = st.date_input("Ważność karty kierowcy")
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

            # Edycja
            with col_b:
                with st.expander("✏️ Edytuj dane kierowcy"):
                    if not df.empty:
                        opcje_k = {f"{row['imie_nazwisko']} (ID: {row['id']})": row['id'] for _, row in df.iterrows()}
                        wybrany_label = st.selectbox("Wybierz kierowcę do edycji", list(opcje_k.keys()))
                        wybrany_id = opcje_k[wybrany_label]
                        row_k = df[df['id'] == wybrany_id].iloc[0]

                        with st.form("form_kierowca_edit"):
                            e_imie = st.text_input("Imię i nazwisko", value=row_k['imie_nazwisko'])
                            e_pesel = st.text_input("PESEL", value=row_k['pesel'])
                            e_nr_pj = st.text_input("Numer prawa jazdy", value=row_k['nr_prawo_jazdy'])
                            e_waznosc_karty = st.date_input("Ważność karty kierowcy", value=parse_date(row_k['waznosc_karty_kierowcy']))
                            e_typ_doc = st.selectbox("Typ dokumentu", ["Paszport", "Dowód osobisty"], index=0 if row_k['typ_dokumentu'] == "Paszport" else 1)
                            e_nr_doc = st.text_input("Numer dokumentu", value=row_k['nr_dokumentu'])
                            e_waznosc_doc = st.date_input("Ważność dokumentu", value=parse_date(row_k['waznosc_dokumentu']))

                            if st.form_submit_button("Zapisz zmiany"):
                                db.edytuj_kierowce(wybrany_id, e_imie, e_pesel, e_nr_pj, e_typ_doc, e_nr_doc, e_waznosc_doc, e_waznosc_karty)
                                st.success("Zaktualizowano dane kierowcy!")
                                st.rerun()

        # Wyszukiwarka
        st.write("### Lista Kierowców")
        szukaj = st.text_input("🔍 Szukaj kierowcy (imię, PESEL, dokument):", key="szukaj_kierowcy")
        if szukaj and not df.empty:
            df = df[df.apply(lambda r: szukaj.lower() in str(r.values).lower(), axis=1)]
        st.dataframe(df, use_container_width=True, hide_index=True)

    # -----------------------------------------
    # CIĄGNIKI
    # -----------------------------------------
    elif zakladka == "Ciągniki 🚛":
        st.subheader("Ciągniki Siodłowe")
        df = db.pobierz_ciagniki()

        if jest_adminem:
            col_a, col_b = st.columns(2)
            with col_a:
                with st.expander("➕ Dodaj ciągnik"):
                    with st.form("form_c_add", clear_on_submit=True):
                        nr_rej = st.text_input("Numer rejestracyjny")
                        vin = st.text_input("Numer VIN")
                        przeglad = st.date_input("Termin przeglądu technicznego")
                        oc = st.date_input("Termin ubezpieczenia OC")
                        if st.form_submit_button("Zapisz ciągnik"):
                            if nr_rej:
                                db.dodaj_ciagnik(nr_rej, vin, przeglad, oc)
                                st.success(f"Dodano ciągnik: {nr_rej}")
                                st.rerun()

            with col_b:
                with st.expander("✏️ Edytuj ciągnik"):
                    if not df.empty:
                        opcje_c = {f"{row['nr_rej']} (VIN: {row['vin']})": row['id'] for _, row in df.iterrows()}
                        wybrany_label = st.selectbox("Wybierz ciągnik do edycji", list(opcje_c.keys()))
                        wybrany_id = opcje_c[wybrany_label]
                        row_c = df[df['id'] == wybrany_id].iloc[0]

                        with st.form("form_c_edit"):
                            e_nr_rej = st.text_input("Numer rejestracyjny", value=row_c['nr_rej'])
                            e_vin = st.text_input("Numer VIN", value=row_c['vin'])
                            e_przeglad = st.date_input("Przegląd", value=parse_date(row_c['przeglad_data']))
                            e_oc = st.date_input("Ubezpieczenie OC", value=parse_date(row_c['oc_data']))
                            if st.form_submit_button("Zapisz zmiany"):
                                db.edytuj_ciagnik(wybrany_id, e_nr_rej, e_vin, e_przeglad, e_oc)
                                st.success("Zaktualizowano dane ciągnika!")
                                st.rerun()

        st.write("### Lista Ciągników")
        szukaj = st.text_input("🔍 Szukaj ciągnika (nr rej, VIN):", key="szukaj_ciagnika")
        if szukaj and not df.empty:
            df = df[df.apply(lambda r: szukaj.lower() in str(r.values).lower(), axis=1)]
        st.dataframe(df, use_container_width=True, hide_index=True)

    # -----------------------------------------
    # NACZEPY
    # -----------------------------------------
    elif zakladka == "Naczepy 📦":
        st.subheader("Naczepy")
        df = db.pobierz_naczepy()

        if jest_adminem:
            col_a, col_b = st.columns(2)
            with col_a:
                with st.expander("➕ Dodaj naczepę"):
                    with st.form("form_n_add", clear_on_submit=True):
                        nr_rej = st.text_input("Numer rejestracyjny")
                        przeglad = st.date_input("Termin przeglądu technicznego")
                        oc = st.date_input("Termin ubezpieczenia OC")
                        if st.form_submit_button("Zapisz naczepę"):
                            if nr_rej:
                                db.dodaj_naczepe(nr_rej, przeglad, oc)
                                st.success(f"Dodano naczepę: {nr_rej}")
                                st.rerun()

            with col_b:
                with st.expander("✏️ Edytuj naczepę"):
                    if not df.empty:
                        opcje_n = {f"{row['nr_rej']}": row['id'] for _, row in df.iterrows()}
                        wybrany_label = st.selectbox("Wybierz naczepę do edycji", list(opcje_n.keys()))
                        wybrany_id = opcje_n[wybrany_label]
                        row_n = df[df['id'] == wybrany_id].iloc[0]

                        with st.form("form_n_edit"):
                            e_nr_rej = st.text_input("Numer rejestracyjny", value=row_n['nr_rej'])
                            e_przeglad = st.date_input("Przegląd", value=parse_date(row_n['przeglad_data']))
                            e_oc = st.date_input("Ubezpieczenie OC", value=parse_date(row_n['oc_data']))
                            if st.form_submit_button("Zapisz zmiany"):
                                db.edytuj_naczepe(wybrany_id, e_nr_rej, e_przeglad, e_oc)
                                st.success("Zaktualizowano naczepę!")
                                st.rerun()

        st.write("### Lista Naczep")
        szukaj = st.text_input("🔍 Szukaj naczepy (nr rej):", key="szukaj_naczepy")
        if szukaj and not df.empty:
            df = df[df.apply(lambda r: szukaj.lower() in str(r.values).lower(), axis=1)]
        st.dataframe(df, use_container_width=True, hide_index=True)

    # -----------------------------------------
    # INNE POJAZDY
    # -----------------------------------------
    elif zakladka == "Inne Pojazdy 🚗":
        st.subheader("Inne Pojazdy (Osobowe, Busy, Przyczepy)")
        df = db.pobierz_inne_pojazdy()

        if jest_adminem:
            col_a, col_b = st.columns(2)
            with col_a:
                with st.expander("➕ Dodaj inny pojazd"):
                    with st.form("form_i_add", clear_on_submit=True):
                        typ = st.selectbox("Typ pojazdu", ["Osobowy", "Bus", "Przyczepa", "Inny"])
                        nr_rej = st.text_input("Numer rejestracyjny")
                        vin = st.text_input("Numer VIN (opcjonalnie)")
                        przeglad = st.date_input("Termin przeglądu technicznego")
                        oc = st.date_input("Termin ubezpieczenia OC")
                        if st.form_submit_button("Zapisz pojazd"):
                            if nr_rej:
                                db.dodaj_inny_pojazd(typ, nr_rej, vin, przeglad, oc)
                                st.success(f"Dodano pojazd: {nr_rej}")
                                st.rerun()

            with col_b:
                with st.expander("✏️ Edytuj pojazd"):
                    if not df.empty:
                        opcje_i = {f"{row['typ_pojazdu']} - {row['nr_rej']}": row['id'] for _, row in df.iterrows()}
                        wybrany_label = st.selectbox("Wybierz pojazd do edycji", list(opcje_i.keys()))
                        wybrany_id = opcje_i[wybrany_label]
                        row_i = df[df['id'] == wybrany_id].iloc[0]

                        with st.form("form_i_edit"):
                            e_typ = st.selectbox("Typ pojazdu", ["Osobowy", "Bus", "Przyczepa", "Inny"], index=["Osobowy", "Bus", "Przyczepa", "Inny"].index(row_i['typ_pojazdu']) if row_i['typ_pojazdu'] in ["Osobowy", "Bus", "Przyczepa", "Inny"] else 0)
                            e_nr_rej = st.text_input("Numer rejestracyjny", value=row_i['nr_rej'])
                            e_vin = st.text_input("VIN", value=row_i['vin'])
                            e_przeglad = st.date_input("Przegląd", value=parse_date(row_i['przeglad_data']))
                            e_oc = st.date_input("Ubezpieczenie OC", value=parse_date(row_i['oc_data']))
                            if st.form_submit_button("Zapisz zmiany"):
                                db.edytuj_inny_pojazd(wybrany_id, e_typ, e_nr_rej, e_vin, e_przeglad, e_oc)
                                st.success("Zaktualizowano pojazd!")
                                st.rerun()

        st.write("### Lista Innych Pojazdów")
        szukaj = st.text_input("🔍 Szukaj pojazdu (typ, nr rej, VIN):", key="szukaj_innego")
        if szukaj and not df.empty:
            df = df[df.apply(lambda r: szukaj.lower() in str(r.values).lower(), axis=1)]
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
                    dt_doc = parse_date(row['waznosc_dokumentu'])
                    dni_doc = (dt_doc - dzisiaj).days
                    if dni_doc <= 30:
                        st.warning(f"👤 **{row['imie_nazwisko']}** – Ważność dokumentu ({row['typ_dokumentu']}) kończy się za {dni_doc} dni! ({dt_doc})")
                        wszystko_ok = False

                if row['waznosc_karty_kierowcy']:
                    dt_karta = parse_date(row['waznosc_karty_kierowcy'])
                    dni_karta = (dt_karta - dzisiaj).days
                    if dni_karta <= 30:
                        st.warning(f"💳 **{row['imie_nazwisko']}** – Ważność **Karty Kierowcy** kończy się za {dni_karta} dni! ({dt_karta})")
                        wszystko_ok = False

        df_c = db.pobierz_ciagniki()
        if not df_c.empty:
            for _, row in df_c.iterrows():
                if row['przeglad_data']:
                    dt_p = parse_date(row['przeglad_data'])
                    dni_p = (dt_p - dzisiaj).days
                    if dni_p <= 30:
                        st.warning(f"🚛 **Ciągnik {row['nr_rej']}** – Przegląd kończy się za {dni_p} dni! ({dt_p})")
                        wszystko_ok = False

                if row['oc_data']:
                    dt_oc = parse_date(row['oc_data'])
                    dni_oc = (dt_oc - dzisiaj).days
                    if dni_oc <= 30:
                        st.warning(f"🛡️ **Ciągnik {row['nr_rej']}** – Ubezpieczenie OC kończy się za {dni_oc} dni! ({dt_oc})")
                        wszystko_ok = False

        df_n = db.pobierz_naczepy()
        if not df_n.empty:
            for _, row in df_n.iterrows():
                if row['przeglad_data']:
                    dt_p = parse_date(row['przeglad_data'])
                    dni_p = (dt_p - dzisiaj).days
                    if dni_p <= 30:
                        st.warning(f"📦 **Naczepa {row['nr_rej']}** – Przegląd kończy się za {dni_p} dni! ({dt_p})")
                        wszystko_ok = False

                if row['oc_data']:
                    dt_oc = parse_date(row['oc_data'])
                    dni_oc = (dt_oc - dzisiaj).days
                    if dni_oc <= 30:
                        st.warning(f"🛡️ **Naczepa {row['nr_rej']}** – Ubezpieczenie OC kończy się za {dni_oc} dni! ({dt_oc})")
                        wszystko_ok = False

        df_i = db.pobierz_inne_pojazdy()
        if not df_i.empty:
            for _, row in df_i.iterrows():
                if row['przeglad_data']:
                    dt_p = parse_date(row['przeglad_data'])
                    dni_p = (dt_p - dzisiaj).days
                    if dni_p <= 30:
                        st.warning(f"🚗 **{row['typ_pojazdu']} {row['nr_rej']}** – Przegląd kończy się za {dni_p} dni! ({dt_p})")
                        wszystko_ok = False

        if wszystko_ok:
            st.success("Wszystkie dokumenty, karty kierowców, ubezpieczenia i przeglądy są w pełni aktualne! 🎉")