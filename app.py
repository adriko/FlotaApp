import streamlit as st
import pandas as pd
import datetime
import database as db

st.set_page_config(page_title="Flota i Dokumenty", layout="wide")

# Menu boczne
st.sidebar.title("🚛 Menu Floty")
menu = st.sidebar.radio(
    "Wybierz sekcję:",
    ["📊 Pulpit / Alerty", "Ciągniki Siodłowe", "Naczepy", "Pojazdy Inne", "Kierowcy"]
)

st.title("🚚 System Zarządzania Flotą i Dokumentami")

# Pomocnicza funkcja do sprawdzania terminów
def sprawdz_terminy(lista_obiektów, typ_pojazdu):
    alerty = []
    dzisiaj = datetime.date.today()
    za_30_dni = dzisiaj + datetime.timedelta(days=30)
    
    for obj in lista_obiektów:
        nazwa_ident = obj.get('nr_rej') or obj.get('nazwa') or f"ID {obj.get('id')}"
        
        # Przegląd
        p_str = obj.get('przeglad_data')
        if p_str:
            try:
                p_dt = datetime.datetime.strptime(str(p_str)[:10], "%Y-%m-%d").date()
                if p_dt < dzisiaj:
                    alerty.append({"Typ": typ_pojazdu, "Pojazd/Kierowca": nazwa_ident, "Zdazenie": "Przegląd PO TERMINIE!", "Data": p_dt, "Status": "🔴 Przekroczono"})
                elif dzisiaj <= p_dt <= za_30_dni:
                    alerty.append({"Typ": typ_pojazdu, "Pojazd/Kierowca": nazwa_ident, "Zdazenie": "Przegląd kończy się niedługo", "Data": p_dt, "Status": "🟡 Wkrótce"})
            except Exception:
                pass

        # OC
        oc_str = obj.get('oc_data')
        if oc_str:
            try:
                oc_dt = datetime.datetime.strptime(str(oc_str)[:10], "%Y-%m-%d").date()
                if oc_dt < dzisiaj:
                    alerty.append({"Typ": typ_pojazdu, "Pojazd/Kierowca": nazwa_ident, "Zdazenie": "OC PO TERMINIE!", "Data": oc_dt, "Status": "🔴 Przekroczono"})
                elif dzisiaj <= oc_dt <= za_30_dni:
                    alerty.append({"Typ": typ_pojazdu, "Pojazd/Kierowca": nazwa_ident, "Zdazenie": "OC kończy się niedługo", "Data": oc_dt, "Status": "🟡 Wkrótce"})
            except Exception:
                pass
                
    return alerty

# ==============================================================================
# 0. PULPIT / ALERTY
# ==============================================================================
if menu == "📊 Pulpit / Alerty":
    st.header("📊 Pulpit - Nadchodzące i Przekroczone Terminy")
    
    ciagniki = db.pobierz_ciagniki()
    naczepy = db.pobierz_naczepy()
    inne = db.pobierz_inne_pojazdy()
    
    wszystkie_alerty = []
    wszystkie_alerty.extend(sprawdz_terminy(ciagniki, "Ciągnik Siodłowy"))
    wszystkie_alerty.extend(sprawdz_terminy(naczepy, "Naczepa"))
    wszystkie_alerty.extend(sprawdz_terminy(inne, "Pojazd Inny"))
    
    if wszystkie_alerty:
        df_alerty = pd.DataFrame(wszystkie_alerty)
        
        przekroczone = df_alerty[df_alerty['Status'].str.contains('🔴')]
        wskrotce = df_alerty[df_alerty['Status'].str.contains('🟡')]
        
        if not przekroczone.empty:
            st.error(f"⚠️ Znaleziono {len(przekroczone)} przeterminowanych opłat / badań!")
            st.dataframe(przekroczone, use_container_width=True, hide_index=True)
            
        if not wskrotce.empty:
            st.warning(f"🔔 Znaleziono {len(wskrotce)} terminów upływających w ciągu najbliższych 30 dni:")
            st.dataframe(wskrotce, use_container_width=True, hide_index=True)
    else:
        st.success("✅ Wszystkie ubezpieczenia i przeglądy są aktualne!")

# ==============================================================================
# 1. CIĄGNIKI SIODŁOWE
# ==============================================================================
elif menu == "Ciągniki Siodłowe":
    st.header("🚛 Ciągniki Siodłowe")
    ciagniki_list = db.pobierz_ciagniki()
    
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
                        db.dodaj_ciagnik(nr_rej, vin, przeglad, oc)
                        st.success("Dodano ciągnik!")
                        st.rerun()
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
                    
                    p_val = datetime.datetime.strptime(str(wybrany['przeglad_data'])[:10], "%Y-%m-%d").date() if wybrany.get('przeglad_data') else datetime.date.today()
                    oc_val = datetime.datetime.strptime(str(wybrany['oc_data'])[:10], "%Y-%m-%d").date() if wybrany.get('oc_data') else datetime.date.today()
                    
                    e_przeglad = st.date_input("Termin przeglądu", value=p_val)
                    e_oc = st.date_input("Termin OC", value=oc_val)
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.form_submit_button("Zapisz zmiany"):
                            db.edytuj_ciagnik(wybrany['id'], e_nr_rej, e_vin, e_przeglad, e_oc)
                            st.success("Zaktualizowano!")
                            st.rerun()
                    with col_btn2:
                        if st.form_submit_button("🗑️ Usuń ciągnik"):
                            db.usun_ciagnik(wybrany['id'])
                            st.warning("Usunięto ciągnik!")
                            st.rerun()

    st.subheader("Lista Ciągników")
    szukaj_c = st.text_input("🔍 Szukaj ciągnika (nr rej, VIN):", key="search_c")
    if len(ciagniki_list) > 0:
        df_c = pd.DataFrame(ciagniki_list)
        if szukaj_c:
            df_c = df_c[df_c.apply(lambda r: szukaj_c.lower() in str(r.values).lower(), axis=1)]
        if not df_c.empty and 'id' in df_c.columns:
            st.dataframe(df_c.drop(columns=['id']), use_container_width=True, hide_index=True)
        else:
            st.dataframe(df_c, use_container_width=True, hide_index=True)
    else:
        st.info("Brak ciągników w bazie.")

# ==============================================================================
# 2. NACZEPY
# ==============================================================================
elif menu == "Naczepy":
    st.header("🚚 Naczepy")
    naczepy_list = db.pobierz_naczepy()
    
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
                        db.dodaj_naczepe(nr_rej, vin, przeglad, oc)
                        st.success("Dodano naczepę!")
                        st.rerun()
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
                    
                    p_val = datetime.datetime.strptime(str(wybrana_n['przeglad_data'])[:10], "%Y-%m-%d").date() if wybrana_n.get('przeglad_data') else datetime.date.today()
                    oc_val = datetime.datetime.strptime(str(wybrana_n['oc_data'])[:10], "%Y-%m-%d").date() if wybrana_n.get('oc_data') else datetime.date.today()
                    
                    e_przeglad = st.date_input("Termin przeglądu", value=p_val)
                    e_oc = st.date_input("Termin OC", value=oc_val)
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.form_submit_button("Zapisz zmiany"):
                            db.edytuj_naczepe(wybrana_n['id'], e_nr_rej, e_vin, e_przeglad, e_oc)
                            st.success("Zaktualizowano!")
                            st.rerun()
                    with col_btn2:
                        if st.form_submit_button("🗑️ Usuń naczepę"):
                            db.usun_naczepe(wybrana_n['id'])
                            st.warning("Usunięto naczepę!")
                            st.rerun()

    st.subheader("Lista Naczep")
    szukaj_n = st.text_input("🔍 Szukaj naczepy (nr rej, VIN):", key="search_n")
    if len(naczepy_list) > 0:
        df_n = pd.DataFrame(naczepy_list)
        if szukaj_n:
            df_n = df_n[df_n.apply(lambda r: szukaj_n.lower() in str(r.values).lower(), axis=1)]
        if not df_n.empty and 'id' in df_n.columns:
            st.dataframe(df_n.drop(columns=['id']), use_container_width=True, hide_index=True)
        else:
            st.dataframe(df_n, use_container_width=True, hide_index=True)
    else:
        st.info("Brak naczep w bazie.")

# ==============================================================================
# 3. POJAZDY INNE
# ==============================================================================
elif menu == "Pojazdy Inne":
    st.header("🚗 Pojazdy Inne")
    inne_list = db.pobierz_inne_pojazdy()
    
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("➕ Dodaj inny pojazd"):
            with st.form("form_dodaj_inny", clear_on_submit=True):
                nazwa = st.text_input("Nazwa / Opis pojazdu")
                nr_rej = st.text_input("Numer rejestracyjny")
                vin = st.text_input("Numer VIN")
                przeglad = st.date_input("Termin przeglądu technicznego", value=datetime.date.today())
                oc = st.date_input("Termin ubezpieczenia OC", value=datetime.date.today())
                if st.form_submit_button("Zapisz pojazd"):
                    if nazwa or nr_rej:
                        db.dodaj_inny_pojazd(nazwa, nr_rej, vin, przeglad, oc)
                        st.success("Dodano pojazd!")
                        st.rerun()
                    else:
                        st.error("Nazwa lub numer rejestracyjny są wymagane!")

    with col2:
        if len(inne_list) > 0:
            with st.expander("✏️ Edytuj / Usuń pojazd"):
                options_i = {f"{i.get('nazwa', 'Pojazd')} - {i.get('nr_rej', '')}": i for i in inne_list}
                wybrany_label_i = st.selectbox("Wybierz pojazd do edycji", list(options_i.keys()))
                wybrany_i = options_i[wybrany_label_i]
                
                with st.form("form_edytuj_inny"):
                    e_nazwa = st.text_input("Nazwa / Opis", value=wybrany_i.get('nazwa', ''))
                    e_nr_rej = st.text_input("Numer rejestracyjny", value=wybrany_i.get('nr_rej', ''))
                    e_vin = st.text_input("Numer VIN", value=wybrany_i.get('vin', ''))
                    
                    p_val = datetime.datetime.strptime(str(wybrany_i['przeglad_data'])[:10], "%Y-%m-%d").date() if wybrany_i.get('przeglad_data') else datetime.date.today()
                    oc_val = datetime.datetime.strptime(str(wybrany_i['oc_data'])[:10], "%Y-%m-%d").date() if wybrany_i.get('oc_data') else datetime.date.today()
                    
                    e_przeglad = st.date_input("Termin przeglądu", value=p_val)
                    e_oc = st.date_input("Termin OC", value=oc_val)
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.form_submit_button("Zapisz zmiany"):
                            db.edytuj_inny_pojazd(wybrany_i['id'], e_nazwa, e_nr_rej, e_vin, e_przeglad, e_oc)
                            st.success("Zaktualizowano!")
                            st.rerun()
                    with col_btn2:
                        if st.form_submit_button("🗑️ Usuń pojazd"):
                            db.usun_inny_pojazd(wybrany_i['id'])
                            st.warning("Usunięto pojazd!")
                            st.rerun()

    st.subheader("Lista Innych Pojazdów")
    szukaj_i = st.text_input("🔍 Szukaj pojazdu:", key="search_i")
    if len(inne_list) > 0:
        df_i = pd.DataFrame(inne_list)
        if szukaj_i:
            df_i = df_i[df_i.apply(lambda r: szukaj_i.lower() in str(r.values).lower(), axis=1)]
        if not df_i.empty and 'id' in df_i.columns:
            st.dataframe(df_i.drop(columns=['id']), use_container_width=True, hide_index=True)
        else:
            st.dataframe(df_i, use_container_width=True, hide_index=True)
    else:
        st.info("Brak pojazdów w bazie.")

# ==============================================================================
# 4. KIEROWCY
# ==============================================================================
elif menu == "Kierowcy":
    st.header("👨‍✈️ Kierowcy")
    kierowcy_list = db.pobierz_kierowcow()
    
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("➕ Dodaj kierowcę"):
            with st.form("form_dodaj_kierowce", clear_on_submit=True):
                nazwisko = st.text_input("Nazwisko")
                imie = st.text_input("Imię")
                pesel = st.text_input("PESEL")
                dowod_osobisty = st.text_input("Numer dowodu osobistego")
                paszport = st.text_input("Numer paszportu")
                prawo_jazdy = st.text_input("Numer prawa jazdy")
                
                if st.form_submit_button("Zapisz kierowcę"):
                    if nazwisko or imie:
                        db.dodaj_kierowce(nazwisko, imie, pesel, dowod_osobisty, paszport, prawo_jazdy)
                        st.success("Dodano kierowcę!")
                        st.rerun()
                    else:
                        st.error("Imię lub nazwisko są wymagane!")

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
                    e_dowod = st.text_input("Numer dowodu osobistego", value=wybrany_k.get('dowod_osobisty', ''))
                    e_paszport = st.text_input("Numer paszportu", value=wybrany_k.get('paszport', ''))
                    e_prawo_jazdy = st.text_input("Numer prawa jazdy", value=wybrany_k.get('prawo_jazdy', ''))
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.form_submit_button("Zapisz zmiany"):
                            db.edytuj_kierowce(
                                wybrany_k['id'], e_nazwisko, e_imie, e_pesel, e_dowod, e_paszport, e_prawo_jazdy
                            )
                            st.success("Zaktualizowano dane kierowcy!")
                            st.rerun()
                    with col_btn2:
                        if st.form_submit_button("🗑️ Usuń kierowcę"):
                            db.usun_kierowce(wybrany_k['id'])
                            st.warning("Usunięto kierowcę!")
                            st.rerun()

    st.subheader("Lista Kierowców")
    szukaj_k = st.text_input("🔍 Szukaj kierowcy (nazwisko, imię, PESEL):", key="search_k")
    if len(kierowcy_list) > 0:
        df_k = pd.DataFrame(kierowcy_list)
        
        # Filtrowanie i usuwanie kolumny 'id' jeśli istnieje
        if 'id' in df_k.columns:
            df_k = df_k.drop(columns=['id'])
            
        if szukaj_k:
            df_k = df_k[df_k.apply(lambda r: szukaj_k.lower() in str(r.values).lower(), axis=1)]
            
        st.dataframe(df_k, use_container_width=True, hide_index=True)
    else:
        st.info("Brak kierowców w bazie.")