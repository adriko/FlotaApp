import streamlit as st
import pandas as pd
import datetime
import database as db

st.set_page_config(page_title="B&B TRANS - Flota", layout="wide")

# ==============================================================================
# 🔐 ZARZĄDZANIE SESJĄ I AUTORYZACJĄ
# ==============================================================================
if "zalogowany" not in st.session_state:
    st.session_state["zalogowany"] = False

# Nawigacja w lewym panelu bocznym
st.sidebar.title("🚛 Menu floty")
menu = st.sidebar.radio(
    "Wybierz sekcję:",
    ["📊 Pulpit / Alerty", "Ciągniki siodłowe", "Naczepy", "Pojazdy inne", "Kierowcy"]
)

# Panel logowania administratora w pasku bocznym
st.sidebar.markdown("---")
if not st.session_state["zalogowany"]:
    with st.sidebar.expander("🔐 Logowanie administratora"):
        haslo = st.text_input("Hasło:", type="password", key="admin_pass_input")
        if st.button("Zaloguj"):
            poprawne_haslo = st.secrets.get("ADMIN_PASSWORD", "")
            if haslo == poprawne_haslo and poprawne_haslo != "":
                st.session_state["zalogowany"] = True
                st.success("Zalogowano pomyślnie!")
                st.rerun()
            else:
                st.error("Nieprawidłowe hasło!")
else:
    st.sidebar.success("👤 Zalogowano: Administrator")
    if st.sidebar.button("Wyloguj"):
        st.session_state["zalogowany"] = False
        st.rerun()

st.title("🚚 B&B TRANS Sp. z o.o. - System zarządzania flotą")

# Pomocnicza funkcja do bezpiecznego parsowania dat
def parsuj_date(data_str):
    if not data_str:
        return None
    try:
        return datetime.datetime.strptime(str(data_str)[:10], "%Y-%m-%d").date()
    except Exception:
        return None

# Pomocnicza funkcja do sprawdzania terminów badań i ubezpieczeń pojazdów
def sprawdz_terminy(lista_obiektow, typ_pojazdu):
    alerty = []
    dzisiaj = datetime.date.today()
    za_30_dni = dzisiaj + datetime.timedelta(days=30)
    
    for obj in lista_obiektow:
        nazwa_ident = obj.get('nr_rej') or obj.get('typ_pojazdu') or obj.get('nazwa') or f"ID {obj.get('id')}"
        
        # Przegląd techniczny
        p_dt = parsuj_date(obj.get('przeglad_data'))
        if p_dt:
            if p_dt < dzisiaj:
                alerty.append({"Typ": typ_pojazdu, "Identyfikator": nazwa_ident, "Zdarzenie": "Przegląd techniczny PO TERMINIE!", "Data": p_dt, "Status": "🔴 Przekroczono"})
            elif dzisiaj <= p_dt <= za_30_dni:
                alerty.append({"Typ": typ_pojazdu, "Identyfikator": nazwa_ident, "Zdarzenie": "Przegląd techniczny kończy się wkrótce", "Data": p_dt, "Status": "🟡 Wkrótce"})

        # Ubezpieczenie OC
        oc_dt = parsuj_date(obj.get('oc_data'))
        if oc_dt:
            if oc_dt < dzisiaj:
                alerty.append({"Typ": typ_pojazdu, "Identyfikator": nazwa_ident, "Zdarzenie": "Ubezpieczenie OC PO TERMINIE!", "Data": oc_dt, "Status": "🔴 Przekroczono"})
            elif dzisiaj <= oc_dt <= za_30_dni:
                alerty.append({"Typ": typ_pojazdu, "Identyfikator": nazwa_ident, "Zdarzenie": "Ubezpieczenie OC kończy się wkrótce", "Data": oc_dt, "Status": "🟡 Wkrótce"})
                
    return alerty

# Pomocnicza funkcja do sprawdzania zezwoleń kierowców (ostrzeżenie z 60-dniowym wyprzedzeniem)
def sprawdz_terminy_kierowcow(lista_kierowcow):
    alerty = []
    dzisiaj = datetime.date.today()
    za_60_dni = dzisiaj + datetime.timedelta(days=60)
    
    for k in lista_kierowcow:
        nazwisko_imie = f"{k.get('nazwisko', '')} {k.get('imie', '')}".strip() or f"ID {k.get('id')}"
        z_dt = parsuj_date(k.get('zezwolenie_data'))
        if z_dt:
            if z_dt < dzisiaj:
                alerty.append({"Typ": "Kierowca", "Identyfikator": nazwisko_imie, "Zdarzenie": "Zezwolenie na pracę PO TERMINIE!", "Data": z_dt, "Status": "🔴 Przekroczono"})
            elif dzisiaj <= z_dt <= za_60_dni:
                alerty.append({"Typ": "Kierowca", "Identyfikator": nazwisko_imie, "Zdarzenie": "Zezwolenie na pracę kończy się wkrótce (do 60 dni)", "Data": z_dt, "Status": "🟡 Wkrótce"})
                
    return alerty

# ==============================================================================
# 1. PULPIT / ALERTY
# ==============================================================================
if menu == "📊 Pulpit / Alerty":
    st.header("📊 Pulpit – nadchodzące i przekroczone terminy")
    
    ciagniki = db.pobierz_ciagniki()
    naczepy = db.pobierz_naczepy()
    inne = db.pobierz_inne_pojazdy()
    kierowcy = db.pobierz_kierowcow()
    
    wszystkie_alerty = []
    wszystkie_alerty.extend(sprawdz_terminy(ciagniki, "Ciągnik siodłowy"))
    wszystkie_alerty.extend(sprawdz_terminy(naczepy, "Naczepa"))
    wszystkie_alerty.extend(sprawdz_terminy(inne, "Pojazd inny"))
    wszystkie_alerty.extend(sprawdz_terminy_kierowcow(kierowcy))
    
    if wszystkie_alerty:
        df_alerty = pd.DataFrame(wszystkie_alerty)
        
        przekroczone = df_alerty[df_alerty['Status'].str.contains('🔴')]
        wskrotce = df_alerty[df_alerty['Status'].str.contains('🟡')]
        
        if not przekroczone.empty:
            st.error(f"⚠️ Znaleziono {len(przekroczone)} przeterminowanych dokumentów / badań!")
            st.dataframe(przekroczone, use_container_width=True, hide_index=True)
            
        if not wskrotce.empty:
            st.warning(f"🔔 Znaleziono {len(wskrotce)} terminów upływających w najbliższym czasie:")
            st.dataframe(wskrotce, use_container_width=True, hide_index=True)
    else:
        st.success("✅ Wszystkie ubezpieczenia, przeglądy oraz zezwolenia są aktualne!")

# ==============================================================================
# 2. CIĄGNIKI SIODŁOWE
# ==============================================================================
elif menu == "Ciągniki siodłowe":
    st.header("🚛 Ciągniki siodłowe")
    ciagniki_list = db.pobierz_ciagniki()
    
    if st.session_state["zalogowany"]:
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("➕ Dodaj ciągnik"):
                with st.form("form_dodaj_ciagnik", clear_on_submit=True):
                    nr_rej = st.text_input("Numer rejestracyjny")
                    vin = st.text_input("Numer VIN")
                    przeglad = st.date_input("Termin przeglądu technicznego", value=datetime.date.today())
                    oc = st.date_input("Termin ubezpieczenia OC", value=datetime.date.today())
                    if st.form_submit_button("Zapisz ciągnik"):
                        if nr_rej:
                            ok, msg = db.dodaj_ciagnik(nr_rej, vin, przeglad, oc)
                            if ok:
                                st.success("Dodano ciągnik!")
                                st.rerun()
                            else:
                                st.error(f"Błąd zapisu: {msg}")
                        else:
                            st.error("Numer rejestracyjny jest wymagany!")

        with col2:
            if len(ciagniki_list) > 0:
                with st.expander("✏️ Edytuj / Usuń ciągnik"):
                    options = {f"{c.get('nr_rej', '')} (VIN: {c.get('vin', '')})": c for c in ciagniki_list}
                    wybrany_label = st.selectbox("Wybierz ciągnik do edycji", list(options.keys()))
                    wybrany = options[wybrany_label]
                    
                    with st.form("form_edytuj_ciagnik"):
                        e_nr_rej = st.text_input("Numer rejestracyjny", value=wybrany.get('nr_rej', ''))
                        e_vin = st.text_input("Numer VIN", value=wybrany.get('vin', ''))
                        
                        p_val = parsuj_date(wybrany.get('przeglad_data')) or datetime.date.today()
                        oc_val = parsuj_date(wybrany.get('oc_data')) or datetime.date.today()
                        
                        e_przeglad = st.date_input("Termin przeglądu technicznego", value=p_val)
                        e_oc = st.date_input("Termin ubezpieczenia OC", value=oc_val)
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.form_submit_button("Zapisz zmiany"):
                                ok, msg = db.edytuj_ciagnik(wybrany['id'], e_nr_rej, e_vin, e_przeglad, e_oc)
                                if ok:
                                    st.success("Zaktualizowano dane ciągnika!")
                                    st.rerun()
                                else:
                                    st.error(f"Błąd: {msg}")
                        with col_btn2:
                            if st.form_submit_button("🗑️ Usuń ciągnik"):
                                ok, msg = db.usun_ciagnik(wybrany['id'])
                                if ok:
                                    st.warning("Usunięto ciągnik!")
                                    st.rerun()
                                else:
                                    st.error(f"Błąd: {msg}")

    st.subheader("Lista ciągników")
    if len(ciagniki_list) > 0:
        df_c = pd.DataFrame(ciagniki_list)
        kolumny_c = ["nr_rej", "vin", "przeglad_data", "oc_data"]
        dostepne_c = [col for col in kolumny_c if col in df_c.columns]
        df_c = df_c[dostepne_c].fillna("-")
        df_c = df_c.rename(columns={
            "nr_rej": "Numer rejestracyjny",
            "vin": "VIN",
            "przeglad_data": "Przegląd techniczny",
            "oc_data": "Ubezpieczenie OC"
        })
        st.dataframe(df_c, use_container_width=True, hide_index=True)
    else:
        st.info("Brak ciągników w bazie.")

# ==============================================================================
# 3. NACZEPY
# ==============================================================================
elif menu == "Naczepy":
    st.header("🚚 Naczepy")
    naczepy_list = db.pobierz_naczepy()
    
    if st.session_state["zalogowany"]:
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("➕ Dodaj naczepę"):
                with st.form("form_dodaj_naczepe", clear_on_submit=True):
                    nr_rej = st.text_input("Numer rejestracyjny")
                    vin = st.text_input("Numer VIN")
                    przeglad = st.date_input("Termin przeglądu technicznego", value=datetime.date.today())
                    oc = st.date_input("Termin ubezpieczenia OC", value=datetime.date.today())
                    if st.form_submit_button("Zapisz naczepę"):
                        if nr_rej:
                            ok, msg = db.dodaj_naczepe(nr_rej, vin, przeglad, oc)
                            if ok:
                                st.success("Dodano naczepę!")
                                st.rerun()
                            else:
                                st.error(f"Błąd zapisu: {msg}")
                        else:
                            st.error("Numer rejestracyjny jest wymagany!")

        with col2:
            if len(naczepy_list) > 0:
                with st.expander("✏️ Edytuj / Usuń naczepę"):
                    options_n = {f"{n.get('nr_rej', '')} (VIN: {n.get('vin', '')})": n for n in naczepy_list}
                    wybrany_label_n = st.selectbox("Wybierz naczepę do edycji", list(options_n.keys()))
                    wybrana_n = options_n[wybrany_label_n]
                    
                    with st.form("form_edytuj_naczepe"):
                        e_nr_rej = st.text_input("Numer rejestracyjny", value=wybrana_n.get('nr_rej', ''))
                        e_vin = st.text_input("Numer VIN", value=wybrana_n.get('vin', ''))
                        
                        p_val = parsuj_date(wybrana_n.get('przeglad_data')) or datetime.date.today()
                        oc_val = parsuj_date(wybrana_n.get('oc_data')) or datetime.date.today()
                        
                        e_przeglad = st.date_input("Termin przeglądu technicznego", value=p_val)
                        e_oc = st.date_input("Termin ubezpieczenia OC", value=oc_val)
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.form_submit_button("Zapisz zmiany"):
                                ok, msg = db.edytuj_naczepe(wybrana_n['id'], e_nr_rej, e_vin, e_przeglad, e_oc)
                                if ok:
                                    st.success("Zaktualizowano dane naczepy!")
                                    st.rerun()
                                else:
                                    st.error(f"Błąd: {msg}")
                        with col_btn2:
                            if st.form_submit_button("🗑️ Usuń naczepę"):
                                ok, msg = db.usun_naczepe(wybrana_n['id'])
                                if ok:
                                    st.warning("Usunięto naczepę!")
                                    st.rerun()
                                else:
                                    st.error(f"Błąd: {msg}")

    st.subheader("Lista naczep")
    if len(naczepy_list) > 0:
        df_n = pd.DataFrame(naczepy_list)
        kolumny_n = ["nr_rej", "vin", "przeglad_data", "oc_data"]
        dostepne_n = [col for col in kolumny_n if col in df_n.columns]
        df_n = df_n[dostepne_n].fillna("-")
        df_n = df_n.rename(columns={
            "nr_rej": "Numer rejestracyjny",
            "vin": "VIN",
            "przeglad_data": "Przegląd techniczny",
            "oc_data": "Ubezpieczenie OC"
        })
        st.dataframe(df_n, use_container_width=True, hide_index=True)
    else:
        st.info("Brak naczep w bazie.")

# ==============================================================================
# 4. POJAZDY INNE
# ==============================================================================
elif menu == "Pojazdy inne":
    st.header("🚗 Pojazdy inne")
    inne_list = db.pobierz_inne_pojazdy()
    
    if st.session_state["zalogowany"]:
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("➕ Dodaj pojazd"):
                with st.form("form_dodaj_inny", clear_on_submit=True):
                    typ_pojazdu = st.text_input("Model / opis pojazdu")
                    nr_rej = st.text_input("Numer rejestracyjny")
                    vin = st.text_input("Numer VIN")
                    przeglad = st.date_input("Termin przeglądu technicznego", value=datetime.date.today())
                    oc = st.date_input("Termin ubezpieczenia OC", value=datetime.date.today())
                    if st.form_submit_button("Zapisz pojazd"):
                        if typ_pojazdu or nr_rej:
                            ok, msg = db.dodaj_inny_pojazd(typ_pojazdu, nr_rej, vin, przeglad, oc)
                            if ok:
                                st.success("Dodano pojazd!")
                                st.rerun()
                            else:
                                st.error(f"Błąd zapisu: {msg}")
                        else:
                            st.error("Model lub numer rejestracyjny są wymagane!")

        with col2:
            if len(inne_list) > 0:
                with st.expander("✏️ Edytuj / Usuń pojazd"):
                    options_i = {f"{i.get('typ_pojazdu', 'Pojazd')} - {i.get('nr_rej', '')}": i for i in inne_list}
                    wybrany_label_i = st.selectbox("Wybierz pojazd do edycji", list(options_i.keys()))
                    wybrany_i = options_i[wybrany_label_i]
                    
                    with st.form("form_edytuj_inny"):
                        e_typ_pojazdu = st.text_input("Model / opis", value=wybrany_i.get('typ_pojazdu', ''))
                        e_nr_rej = st.text_input("Numer rejestracyjny", value=wybrany_i.get('nr_rej', ''))
                        e_vin = st.text_input("Numer VIN", value=wybrany_i.get('vin', ''))
                        
                        p_val = parsuj_date(wybrany_i.get('przeglad_data')) or datetime.date.today()
                        oc_val = parsuj_date(wybrany_i.get('oc_data')) or datetime.date.today()
                        
                        e_przeglad = st.date_input("Termin przeglądu technicznego", value=p_val)
                        e_oc = st.date_input("Termin ubezpieczenia OC", value=oc_val)
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.form_submit_button("Zapisz zmiany"):
                                ok, msg = db.edytuj_inny_pojazd(wybrany_i['id'], e_typ_pojazdu, e_nr_rej, e_vin, e_przeglad, e_oc)
                                if ok:
                                    st.success("Zaktualizowano dane pojazdu!")
                                    st.rerun()
                                else:
                                    st.error(f"Błąd: {msg}")
                        with col_btn2:
                            if st.form_submit_button("🗑️ Usuń pojazd"):
                                ok, msg = db.usun_inny_pojazd(wybrany_i['id'])
                                if ok:
                                    st.warning("Usunięto pojazd!")
                                    st.rerun()
                                else:
                                    st.error(f"Błąd: {msg}")

    st.subheader("Lista innych pojazdów")
    if len(inne_list) > 0:
        df_i = pd.DataFrame(inne_list)
        kolumny_i = ["typ_pojazdu", "nr_rej", "vin", "przeglad_data", "oc_data"]
        dostepne_i = [col for col in kolumny_i if col in df_i.columns]
        df_i = df_i[dostepne_i].fillna("-")
        df_i = df_i.rename(columns={
            "typ_pojazdu": "Model / opis",
            "nr_rej": "Numer rejestracyjny",
            "vin": "VIN",
            "przeglad_data": "Przegląd techniczny",
            "oc_data": "Ubezpieczenie OC"
        })
        st.dataframe(df_i, use_container_width=True, hide_index=True)
    else:
        st.info("Brak pojazdów w bazie.")

# ==============================================================================
# 5. KIEROWCY
# ==============================================================================
elif menu == "Kierowcy":
    st.header("👨‍✈️ Kierowcy")
    kierowcy_list = db.pobierz_kierowcow()
    
    if st.session_state["zalogowany"]:
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("➕ Dodaj kierowcę"):
                with st.form("form_dodaj_kierowce", clear_on_submit=True):
                    nazwisko = st.text_input("Nazwisko")
                    imie = st.text_input("Imię")
                    pesel = st.text_input("PESEL")
                    paszport = st.text_input("Paszport")
                    dowod = st.text_input("Dowód osobisty")
                    prawo_jazdy = st.text_input("Prawo jazdy")
                    
                    ma_zezwolenie = st.checkbox("Obcokrajowiec (zezwolenie na pracę / oświadczenie)")
                    zezwolenie_data = None
                    if ma_zezwolenie:
                        zezwolenie_data = st.date_input("Termin ważności zezwolenia", value=datetime.date.today())
                    
                    if st.form_submit_button("Zapisz kierowcę"):
                        if nazwisko or imie:
                            ok, msg = db.dodaj_kierowce(nazwisko, imie, pesel, paszport, dowod, prawo_jazdy, zezwolenie_data)
                            if ok:
                                st.success("Dodano kierowcę!")
                                st.rerun()
                            else:
                                st.error(f"Błąd bazy danych: {msg}")
                        else:
                            st.error("Nazwisko lub imię są wymagane!")

        with col2:
            if len(kierowcy_list) > 0:
                with st.expander("✏️ Edytuj / Usuń kierowcę"):
                    options_k = {f"{k.get('nazwisko', '')} {k.get('imie', '')} (PESEL: {k.get('pesel', '-')})": k for k in kierowcy_list}
                    wybrany_label_k = st.selectbox("Wybierz kierowcę do edycji", list(options_k.keys()))
                    wybrany_k = options_k[wybrany_label_k]
                    
                    with st.form("form_edytuj_kierowce"):
                        e_nazwisko = st.text_input("Nazwisko", value=wybrany_k.get('nazwisko', ''))
                        e_imie = st.text_input("Imię", value=wybrany_k.get('imie', ''))
                        e_pesel = st.text_input("PESEL", value=wybrany_k.get('pesel', ''))
                        e_paszport = st.text_input("Paszport", value=wybrany_k.get('paszport', ''))
                        e_dowod = st.text_input("Dowód osobisty", value=wybrany_k.get('dowod_osobisty', ''))
                        e_prawo_jazdy = st.text_input("Prawo jazdy", value=wybrany_k.get('prawo_jazdy', ''))
                        
                        aktualne_zezwolenie = parsuj_date(wybrany_k.get('zezwolenie_data'))
                        e_ma_zezwolenie = st.checkbox("Obcokrajowiec (zezwolenie na pracę)", value=(aktualne_zezwolenie is not None))
                        e_zezwolenie_data = None
                        if e_ma_zezwolenie:
                            e_zezwolenie_data = st.date_input("Termin ważności zezwolenia", value=aktualne_zezwolenie or datetime.date.today())
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.form_submit_button("Zapisz zmiany"):
                                ok, msg = db.edytuj_kierowce(
                                    wybrany_k['id'], e_nazwisko, e_imie, e_pesel, e_paszport, e_dowod, e_prawo_jazdy, e_zezwolenie_data
                                )
                                if ok:
                                    st.success("Zaktualizowano dane kierowcy!")
                                    st.rerun()
                                else:
                                    st.error(f"Błąd: {msg}")
                        with col_btn2:
                            if st.form_submit_button("🗑️ Usuń kierowcę"):
                                ok, msg = db.usun_kierowce(wybrany_k['id'])
                                if ok:
                                    st.warning("Usunięto kierowcę!")
                                    st.rerun()
                                else:
                                    st.error(f"Błąd: {msg}")

    st.subheader("Lista kierowców")
    if len(kierowcy_list) > 0:
        df_k = pd.DataFrame(kierowcy_list)
        kolumny_kolejnosc = ["nazwisko", "imie", "pesel", "paszport", "dowod_osobisty", "prawo_jazdy", "zezwolenie_data"]
        dostepne_kolumny = [col for col in kolumny_kolejnosc if col in df_k.columns]
        df_k = df_k[dostepne_kolumny].fillna("-")
        df_k = df_k.rename(columns={
            "nazwisko": "Nazwisko",
            "imie": "Imię",
            "pesel": "PESEL",
            "paszport": "Paszport",
            "dowod_osobisty": "Dowód osobisty",
            "prawo_jazdy": "Prawo jazdy",
            "zezwolenie_data": "Termin zezwolenia"
        })
        st.dataframe(df_k, use_container_width=True, hide_index=True)
    else:
        st.info("Brak kierowców w bazie.")