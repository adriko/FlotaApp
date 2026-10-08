import datetime

import pandas as pd
import streamlit as st

import database as db

st.set_page_config(page_title="Flota i Dokumenty", layout="wide")

# ==================== STAN LOGOWANIA ====================
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

# Nawigacja w lewym panelu bocznym
st.sidebar.title("🚛 Menu Floty")
menu = st.sidebar.radio(
    "Wybierz sekcję:",
    [
        "📊 Pulpit / Alerty",
        "📋 Zestawienie / Składy",
        "Ciągniki Siodłowe",
        "Naczepy",
        "Pojazdy Inne",
        "Kierowcy",
    ],
)

# Panel logowania w sidebarze
st.sidebar.divider()
if not st.session_state["is_admin"]:
    with st.sidebar.expander("🔒 Logowanie administratora"):
        haslo_input = st.text_input("Hasło:", type="password", key="login_pass_input")
        if st.button("Zaloguj", key="btn_login"):
            if db.sprawdz_haslo_admina(haslo_input):
                st.session_state["is_admin"] = True
                st.sidebar.success("Zalogowano!")
                st.rerun()
            else:
                st.sidebar.error("Błędne hasło!")
else:
    st.sidebar.success("🔓 Zalogowano jako Administrator")
    if st.sidebar.button("Wyloguj", key="btn_logout"):
        st.session_state["is_admin"] = False
        st.rerun()

st.title("🚚 Zarządzanie flotą B&B TRANS")

def dzisiejsza_data() -> datetime.date:
    return datetime.datetime.now(tz=datetime.timezone.utc).date()

def parsuj_date(data_str: str | None) -> datetime.date | None:
    if not data_str:
        return None
    try:
        return datetime.date.fromisoformat(str(data_str)[:10])
    except (ValueError, TypeError):
        return None

# Pomocnicza funkcja do sprawdzania terminów badań i ubezpieczeń
def sprawdz_terminy(lista_obiektow, typ_pojazdu):
    alerty = []
    dzisiaj = dzisiejsza_data()
    za_30_dni = dzisiaj + datetime.timedelta(days=30)

    for obj in lista_obiektow:
        nazwa_ident = obj.get("nr_rej") or obj.get("nazwa") or f"ID {obj.get('id')}"

        # Przegląd techniczny
        p_dt = parsuj_date(obj.get("przeglad_data"))
        if p_dt:
            if p_dt < dzisiaj:
                alerty.append({
                    "Typ": typ_pojazdu,
                    "Identyfikator": nazwa_ident,
                    "Zdarzenie": "Przegląd PO TERMINIE!",
                    "Data": p_dt,
                    "Status": "🔴 Przekroczono",
                })
            elif dzisiaj <= p_dt <= za_30_dni:
                alerty.append({
                    "Typ": typ_pojazdu,
                    "Identyfikator": nazwa_ident,
                    "Zdarzenie": "Przegląd kończy się niedługo",
                    "Data": p_dt,
                    "Status": "🟡 Wkrótce",
                })

        # Ubezpieczenie OC
        oc_dt = parsuj_date(obj.get("oc_data"))
        if oc_dt:
            if oc_dt < dzisiaj:
                alerty.append({
                    "Typ": typ_pojazdu,
                    "Identyfikator": nazwa_ident,
                    "Zdarzenie": "OC PO TERMINIE!",
                    "Data": oc_dt,
                    "Status": "🔴 Przekroczono",
                })
            elif dzisiaj <= oc_dt <= za_30_dni:
                alerty.append({
                    "Typ": typ_pojazdu,
                    "Identyfikator": nazwa_ident,
                    "Zdarzenie": "OC kończy się niedługo",
                    "Data": oc_dt,
                    "Status": "🟡 Wkrótce",
                })

    return alerty

# ==============================================================================
# 1. PULPIT / ALERTY
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

        przekroczone = df_alerty[df_alerty["Status"].str.contains("🔴")]
        wskrotce = df_alerty[df_alerty["Status"].str.contains("🟡")]

        if not przekroczone.empty:
            st.error(f"⚠️ Znaleziono {len(przekroczone)} przeterminowanych opłat / badań!")
            st.dataframe(przekroczone, use_container_width=True, hide_index=True)

        if not wskrotce.empty:
            st.warning(f"🔔 Znaleziono {len(wskrotce)} terminów upływających w ciągu najbliższych 30 dni:")
            st.dataframe(wskrotce, use_container_width=True, hide_index=True)
    else:
        st.success("✅ Wszystkie ubezpieczenia i przeglądy są aktualne!")

# ==============================================================================
# 2. ZESTAWIENIE / SKŁADY
# ==============================================================================
elif menu == "📋 Zestawienie / Składy":
    st.header("📋 Zestawienie Kierowca - Ciągnik - Naczepa")

    przypisania_list = db.pobierz_przypisania()

    if st.session_state["is_admin"]:
        kierowcy_list = db.pobierz_kierowcow()
        ciagniki_list = db.pobierz_ciagniki()
        naczepy_list = db.pobierz_naczepy()

        opcje_kierowcy = {"-- Brak / Nieprzypisany --": None}
        opcje_kierowcy.update({
            f"{k.get('nazwisko', '')} {k.get('imie', '')} (PESEL: {k.get('pesel', '-')})": k["id"]
            for k in kierowcy_list
        })

        opcje_ciagniki = {"-- Brak / Nieprzypisany --": None}
        opcje_ciagniki.update({
            f"{c.get('nr_rej', '')} (VIN: {c.get('vin', '-')})": c["id"]
            for c in ciagniki_list
        })

        opcje_naczepy = {"-- Brak / Nieprzypisany --": None}
        opcje_naczepy.update({
            f"{n.get('nr_rej', '')} (VIN: {n.get('vin', '-')})": n["id"]
            for n in naczepy_list
        })

        col1, col2 = st.columns(2)
        with col1, st.expander("➕ Dodaj / Przypisz skład"), st.form("form_dodaj_przypisanie", clear_on_submit=True):
            kier_wybor = st.selectbox("Kierowca", list(opcje_kierowcy.keys()))
            ciag_wybor = st.selectbox("Ciągnik siodłowy", list(opcje_ciagniki.keys()))
            nacz_wybor = st.selectbox("Naczepa", list(opcje_naczepy.keys()))
            uwagi_wpis = st.text_area("Uwagi (np. naczepa tymczasowa, zamiana kierowcy)")

            if st.form_submit_button("Zapisz przypisanie"):
                ok, msg = db.dodaj_przypisanie(
                    opcje_kierowcy[kier_wybor],
                    opcje_ciagniki[ciag_wybor],
                    opcje_naczepy[nacz_wybor],
                    uwagi_wpis,
                )
                if ok:
                    st.success("Zapisano przypisanie!")
                    st.rerun()
                else:
                    st.error(f"Błąd zapisu: {msg}")

        with col2:
            if len(przypisania_list) > 0:
                mapa_zestawow = {}
                for p in przypisania_list:
                    k_nazwa = f"{p['kierowcy']['nazwisko']} {p['kierowcy']['imie']}" if p.get("kierowcy") else "Brak kierowcy"
                    c_nazwa = p["ciagniki"]["nr_rej"] if p.get("ciagniki") else "Brak ciągnika"
                    n_nazwa = p["naczepy"]["nr_rej"] if p.get("naczepy") else "Brak naczepy"
                    etykieta = f"ID {p['id']}: {k_nazwa} | {c_nazwa} | {n_nazwa}"
                    mapa_zestawow[etykieta] = p

                with st.expander("✏️ Edytuj / Usuń przypisanie"):
                    wybrany_zestaw_label = st.selectbox("Wybierz zestaw do modyfikacji", list(mapa_zestawow.keys()))
                    wybrany_zestaw = mapa_zestawow[wybrany_zestaw_label]

                    with st.form("form_edytuj_przypisanie"):
                        k_id = wybrany_zestaw.get("kierowca_id")
                        c_id = wybrany_zestaw.get("ciagnik_id")
                        n_id = wybrany_zestaw.get("naczepa_id")

                        k_keys = list(opcje_kierowcy.keys())
                        c_keys = list(opcje_ciagniki.keys())
                        n_keys = list(opcje_naczepy.keys())

                        idx_k = [i for i, k in enumerate(k_keys) if opcje_kierowcy[k] == k_id]
                        idx_c = [i for i, k in enumerate(c_keys) if opcje_ciagniki[k] == c_id]
                        idx_n = [i for i, k in enumerate(n_keys) if opcje_naczepy[k] == n_id]

                        e_kier = st.selectbox("Kierowca", k_keys, index=idx_k[0] if idx_k else 0)
                        e_ciag = st.selectbox("Ciągnik siodłowy", c_keys, index=idx_c[0] if idx_c else 0)
                        e_nacz = st.selectbox("Naczepa", n_keys, index=idx_n[0] if idx_n else 0)
                        e_uwagi = st.text_area("Uwagi", value=wybrany_zestaw.get("uwagi") or "")

                        btn_c1, btn_c2 = st.columns(2)
                        with btn_c1:
                            if st.form_submit_button("Zapisz zmiany"):
                                ok, msg = db.edytuj_przypisanie(
                                    wybrany_zestaw["id"],
                                    opcje_kierowcy[e_kier],
                                    opcje_ciagniki[e_ciag],
                                    opcje_naczepy[e_nacz],
                                    e_uwagi,
                                )
                                if ok:
                                    st.success("Zaktualizowano przypisanie!")
                                    st.rerun()
                                else:
                                    st.error(f"Błąd: {msg}")
                        with btn_c2:
                            if st.form_submit_button("🗑️ Usuń przypisanie"):
                                ok, msg = db.usun_przypisanie(wybrany_zestaw["id"])
                                if ok:
                                    st.warning("Usunięto przypisanie!")
                                    st.rerun()
                                else:
                                    st.error(f"Błąd: {msg}")
    else:
        # Gość – możliwość edycji samych uwag
        if len(przypisania_list) > 0:
            mapa_uwag = {}
            for p in przypisania_list:
                k_nazwa = f"{p['kierowcy']['nazwisko']} {p['kierowcy']['imie']}" if p.get("kierowcy") else "Brak kierowcy"
                c_nazwa = p["ciagniki"]["nr_rej"] if p.get("ciagniki") else "Brak ciągnika"
                n_nazwa = p["naczepy"]["nr_rej"] if p.get("naczepy") else "Brak naczepy"
                etykieta = f"{k_nazwa} | Ciągnik: {c_nazwa} | Naczepa: {n_nazwa}"
                mapa_uwag[etykieta] = p

            with st.expander("📝 Dodaj / Zmień uwagę do zestawu (dostępne dla każdego)"):
                wybrany_zestaw_u = st.selectbox("Wybierz zestaw:", list(mapa_uwag.keys()), key="guest_select_zestaw")
                obj_zestaw = mapa_uwag[wybrany_zestaw_u]
                with st.form("form_uwaga_gosc"):
                    nowa_uwaga = st.text_area("Treść uwagi:", value=obj_zestaw.get("uwagi") or "")
                    if st.form_submit_button("Zapisz uwagę"):
                        ok, msg = db.edytuj_uwagi_przypisania(obj_zestaw["id"], nowa_uwaga)
                        if ok:
                            st.success("Zapisano uwagę!")
                            st.rerun()
                        else:
                            st.error(f"Błąd zapisu: {msg}")

    st.subheader("Aktualne zestawienie składów")
    szukaj_z = st.text_input("🔍 Szukaj składu (kierowca, nr rej, uwagi):", key="search_z")
    if przypisania_list:
        tabela_dane = []
        for p in przypisania_list:
            tabela_dane.append({
                "Kierowca": f"{p['kierowcy']['nazwisko']} {p['kierowcy']['imie']}" if p.get("kierowcy") else "—",
                "Ciągnik": p["ciagniki"]["nr_rej"] if p.get("ciagniki") else "—",
                "Naczepa": p["naczepy"]["nr_rej"] if p.get("naczepy") else "—",
                "Uwagi": p.get("uwagi") or "",
            })
        df_przypisania = pd.DataFrame(tabela_dane)
        if szukaj_z:
            df_przypisania = df_przypisania[df_przypisania.apply(lambda r: szukaj_z.lower() in str(r.values).lower(), axis=1)]
        st.dataframe(df_przypisania, use_container_width=True, hide_index=True)
    else:
        st.info("Brak aktywnych przypisań.")

# ==============================================================================
# 3. CIĄGNIKI SIODŁOWE
# ==============================================================================
elif menu == "Ciągniki Siodłowe":
    st.header("🚛 Ciągniki Siodłowe")
    ciagniki_list = db.pobierz_ciagniki()

    if st.session_state["is_admin"]:
        col1, col2 = st.columns(2)
        with col1, st.expander("➕ Dodaj ciągnik"), st.form("form_dodaj_ciagnik", clear_on_submit=True):
            nr_rej = st.text_input("Numer rejestracyjny")
            vin = st.text_input("Numer VIN")
            przeglad = st.date_input("Termin przeglądu technicznego", value=dzisiejsza_data())
            oc = st.date_input("Termin ubezpieczenia OC", value=dzisiejsza_data())
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
                options = {f"{c.get('nr_rej', '')} (VIN: {c.get('vin', '')})": c for c in ciagniki_list}
                with st.expander("✏️ Edytuj / Usuń ciągnik"):
                    wybrany_label = st.selectbox("Wybierz ciągnik do edycji", list(options.keys()))
                    wybrany = options[wybrany_label]

                    with st.form("form_edytuj_ciagnik"):
                        e_nr_rej = st.text_input("Numer rejestracyjny", value=wybrany.get("nr_rej", ""))
                        e_vin = st.text_input("Numer VIN", value=wybrany.get("vin", ""))

                        p_val = parsuj_date(wybrany.get("przeglad_data")) or dzisiejsza_data()
                        oc_val = parsuj_date(wybrany.get("oc_data")) or dzisiejsza_data()

                        e_przeglad = st.date_input("Termin przeglądu", value=p_val)
                        e_oc = st.date_input("Termin OC", value=oc_val)

                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.form_submit_button("Zapisz zmiany"):
                                ok, msg = db.edytuj_ciagnik(wybrany["id"], e_nr_rej, e_vin, e_przeglad, e_oc)
                                if ok:
                                    st.success("Zaktualizowano!")
                                    st.rerun()
                                else:
                                    st.error(f"Błąd: {msg}")
                        with col_btn2:
                            if st.form_submit_button("🗑️ Usuń ciągnik"):
                                ok, msg = db.usun_ciagnik(wybrany["id"])
                                if ok:
                                    st.warning("Usunięto ciągnik!")
                                    st.rerun()
                                else:
                                    st.error(f"Błąd: {msg}")

    st.subheader("Lista Ciągników")
    szukaj_c = st.text_input("🔍 Szukaj ciągnika (nr rej, VIN):", key="search_c")
    if len(ciagniki_list) > 0:
        df_c = pd.DataFrame(ciagniki_list)
        if szukaj_c:
            df_c = df_c[df_c.apply(lambda r: szukaj_c.lower() in str(r.values).lower(), axis=1)]
        if not df_c.empty and "id" in df_c.columns:
            st.dataframe(df_c.drop(columns=["id"]), use_container_width=True, hide_index=True)
        else:
            st.dataframe(df_c, use_container_width=True, hide_index=True)
    else:
        st.info("Brak ciągników w bazie.")

# ==============================================================================
# 4. NACZEPY
# ==============================================================================
elif menu == "Naczepy":
    st.header("🚚 Naczepy")
    naczepy_list = db.pobierz_naczepy()

    if st.session_state["is_admin"]:
        col1, col2 = st.columns(2)
        with col1, st.expander("➕ Dodaj naczepę"), st.form("form_dodaj_naczepe", clear_on_submit=True):
            nr_rej = st.text_input("Numer rejestracyjny")
            vin = st.text_input("Numer VIN")
            przeglad = st.date_input("Termin przeglądu technicznego", value=dzisiejsza_data())
            oc = st.date_input("Termin ubezpieczenia OC", value=dzisiejsza_data())
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
                options_n = {f"{n.get('nr_rej', '')} (VIN: {n.get('vin', '')})": n for n in naczepy_list}
                with st.expander("✏️ Edytuj / Usuń naczepę"):
                    wybrany_label_n = st.selectbox("Wybierz naczepę do edycji", list(options_n.keys()))
                    wybrana_n = options_n[wybrany_label_n]

                    with st.form("form_edytuj_naczepe"):
                        e_nr_rej = st.text_input("Numer rejestracyjny", value=wybrana_n.get("nr_rej", ""))
                        e_vin = st.text_input("Numer VIN", value=wybrana_n.get("vin", ""))

                        p_val = parsuj_date(wybrana_n.get("przeglad_data")) or dzisiejsza_data()
                        oc_val = parsuj_date(wybrana_n.get("oc_data")) or dzisiejsza_data()

                        e_przeglad = st.date_input("Termin przeglądu", value=p_val)
                        e_oc = st.date_input("Termin OC", value=oc_val)

                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.form_submit_button("Zapisz zmiany"):
                                ok, msg = db.edytuj_naczepe(wybrana_n["id"], e_nr_rej, e_vin, e_przeglad, e_oc)
                                if ok:
                                    st.success("Zaktualizowano!")
                                    st.rerun()
                                else:
                                    st.error(f"Błąd: {msg}")
                        with col_btn2:
                            if st.form_submit_button("🗑️ Usuń naczepę"):
                                ok, msg = db.usun_naczepe(wybrana_n["id"])
                                if ok:
                                    st.warning("Usunięto naczepę!")
                                    st.rerun()
                                else:
                                    st.error(f"Błąd: {msg}")

    st.subheader("Lista Naczep")
    szukaj_n = st.text_input("🔍 Szukaj naczepy (nr rej, VIN):", key="search_n")
    if len(naczepy_list) > 0:
        df_n = pd.DataFrame(naczepy_list)
        if szukaj_n:
            df_n = df_n[df_n.apply(lambda r: szukaj_n.lower() in str(r.values).lower(), axis=1)]
        if not df_n.empty and "id" in df_n.columns:
            st.dataframe(df_n.drop(columns=["id"]), use_container_width=True, hide_index=True)
        else:
            st.dataframe(df_n, use_container_width=True, hide_index=True)
    else:
        st.info("Brak naczep w bazie.")

# ==============================================================================
# 5. POJAZDY INNE
# ==============================================================================
elif menu == "Pojazdy Inne":
    st.header("🚗 Pojazdy Inne")
    inne_list = db.pobierz_inne_pojazdy()

    if st.session_state["is_admin"]:
        col1, col2 = st.columns(2)
        with col1, st.expander("➕ Dodaj inny pojazd"), st.form("form_dodaj_inny", clear_on_submit=True):
            nazwa = st.text_input("Model / Opis pojazdu")
            nr_rej = st.text_input("Numer rejestracyjny")
            vin = st.text_input("Numer VIN")
            przeglad = st.date_input("Termin przeglądu technicznego", value=dzisiejsza_data())
            oc = st.date_input("Termin ubezpieczenia OC", value=dzisiejsza_data())
            if st.form_submit_button("Zapisz pojazd"):
                if nazwa or nr_rej:
                    ok, msg = db.dodaj_inny_pojazd(nazwa, nr_rej, vin, przeglad, oc)
                    if ok:
                        st.success("Dodano pojazd!")
                        st.rerun()
                    else:
                        st.error(f"Błąd zapisu: {msg}")
                else:
                    st.error("Nazwa lub numer rejestracyjny są wymagane!")

        with col2:
            if len(inne_list) > 0:
                options_i = {f"{i.get('nazwa', 'Pojazd')} - {i.get('nr_rej', '')}": i for i in inne_list}
                with st.expander("✏️ Edytuj / Usuń pojazd"):
                    wybrany_label_i = st.selectbox("Wybierz pojazd do edycji", list(options_i.keys()))
                    wybrany_i = options_i[wybrany_label_i]

                    with st.form("form_edytuj_inny"):
                        e_nazwa = st.text_input("Model / Opis", value=wybrany_i.get("nazwa", ""))
                        e_nr_rej = st.text_input("Numer rejestracyjny", value=wybrany_i.get("nr_rej", ""))
                        e_vin = st.text_input("Numer VIN", value=wybrany_i.get("vin", ""))

                        p_val = parsuj_date(wybrany_i.get("przeglad_data")) or dzisiejsza_data()
                        oc_val = parsuj_date(wybrany_i.get("oc_data")) or dzisiejsza_data()

                        e_przeglad = st.date_input("Termin przeglądu", value=p_val)
                        e_oc = st.date_input("Termin OC", value=oc_val)

                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.form_submit_button("Zapisz zmiany"):
                                ok, msg = db.edytuj_inny_pojazd(wybrany_i["id"], e_nazwa, e_nr_rej, e_vin, e_przeglad, e_oc)
                                if ok:
                                    st.success("Zaktualizowano!")
                                    st.rerun()
                                else:
                                    st.error(f"Błąd: {msg}")
                        with col_btn2:
                            if st.form_submit_button("🗑️ Usuń pojazd"):
                                ok, msg = db.usun_inny_pojazd(wybrany_i["id"])
                                if ok:
                                    st.warning("Usunięto pojazd!")
                                    st.rerun()
                                else:
                                    st.error(f"Błąd: {msg}")

    st.subheader("Lista Innych Pojazdów")
    szukaj_i = st.text_input("🔍 Szukaj pojazdu:", key="search_i")
    if len(inne_list) > 0:
        df_i = pd.DataFrame(inne_list)
        if szukaj_i:
            df_i = df_i[df_i.apply(lambda r: szukaj_i.lower() in str(r.values).lower(), axis=1)]
        if not df_i.empty and "id" in df_i.columns:
            st.dataframe(df_i.drop(columns=["id"]), use_container_width=True, hide_index=True)
        else:
            st.dataframe(df_i, use_container_width=True, hide_index=True)
    else:
        st.info("Brak pojazdów w bazie.")

# ==============================================================================
# 6. KIEROWCY
# ==============================================================================
elif menu == "Kierowcy":
    st.header("👨‍✈️ Kierowcy")
    kierowcy_list = db.pobierz_kierowcow()

    if st.session_state["is_admin"]:
        col1, col2 = st.columns(2)
        with col1, st.expander("➕ Dodaj kierowcę"), st.form("form_dodaj_kierowce", clear_on_submit=True):
            nazwisko = st.text_input("Nazwisko")
            imie = st.text_input("Imię")
            pesel = st.text_input("PESEL")
            paszport = st.text_input("Paszport")
            dowod = st.text_input("Dowód osobisty")
            prawo_jazdy = st.text_input("Prawo jazdy")

            if st.form_submit_button("Zapisz kierowcę"):
                if nazwisko or imie:
                    ok, msg = db.dodaj_kierowce(nazwisko, imie, pesel, paszport, dowod, prawo_jazdy)
                    if ok:
                        st.success("Dodano kierowcę!")
                        st.rerun()
                    else:
                        st.error(f"Błąd bazy danych: {msg}")
                else:
                    st.error("Imię lub nazwisko są wymagane!")

        with col2:
            if len(kierowcy_list) > 0:
                options_k = {
                    f"{k.get('nazwisko', '')} {k.get('imie', '')} (PESEL: {k.get('pesel', '-')})": k
                    for k in kierowcy_list
                }
                with st.expander("✏️ Edytuj / Usuń kierowcę"):
                    wybrany_label_k = st.selectbox("Wybierz kierowcę do edycji", list(options_k.keys()))
                    wybrany_k = options_k[wybrany_label_k]

                    with st.form("form_edytuj_kierowce"):
                        e_nazwisko = st.text_input("Nazwisko", value=wybrany_k.get("nazwisko", ""))
                        e_imie = st.text_input("Imię", value=wybrany_k.get("imie", ""))
                        e_pesel = st.text_input("PESEL", value=wybrany_k.get("pesel", ""))
                        e_paszport = st.text_input("Paszport", value=wybrany_k.get("paszport", ""))
                        e_dowod = st.text_input("Dowód osobisty", value=wybrany_k.get("dowod_osobisty", ""))
                        e_prawo_jazdy = st.text_input("Prawo jazdy", value=wybrany_k.get("prawo_jazdy", ""))

                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.form_submit_button("Zapisz zmiany"):
                                ok, msg = db.edytuj_kierowce(
                                    wybrany_k["id"],
                                    e_nazwisko,
                                    e_imie,
                                    e_pesel,
                                    e_paszport,
                                    e_dowod,
                                    e_prawo_jazdy,
                                )
                                if ok:
                                    st.success("Zaktualizowano dane kierowcy!")
                                    st.rerun()
                                else:
                                    st.error(f"Błąd: {msg}")
                        with col_btn2:
                            if st.form_submit_button("🗑️ Usuń kierowcę"):
                                ok, msg = db.usun_kierowce(wybrany_k["id"])
                                if ok:
                                    st.warning("Usunięto kierowcę!")
                                    st.rerun()
                                else:
                                    st.error(f"Błąd: {msg}")

    st.subheader("Lista Kierowców")
    szukaj_k = st.text_input("🔍 Szukaj kierowcy (nazwisko, imię, PESEL):", key="search_k")
    if len(kierowcy_list) > 0:
        df_k = pd.DataFrame(kierowcy_list)

        kolumny_kolejnosc = ["nazwisko", "imie", "pesel", "paszport", "dowod_osobisty", "prawo_jazdy"]
        dostepne_kolumny = [col for col in kolumny_kolejnosc if col in df_k.columns]
        df_k = df_k[dostepne_kolumny]

        df_k = df_k.rename(
            columns={
                "nazwisko": "Nazwisko",
                "imie": "Imię",
                "pesel": "PESEL",
                "paszport": "Paszport",
                "dowod_osobisty": "Dowód osobisty",
                "prawo_jazdy": "Prawo jazdy",
            }
        )

        if szukaj_k:
            df_k = df_k[df_k.apply(lambda r: szukaj_k.lower() in str(r.values).lower(), axis=1)]

        st.dataframe(df_k, use_container_width=True, hide_index=True)
    else:
        st.info("Brak kierowców w bazie.")