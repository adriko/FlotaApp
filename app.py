import streamlit as st
import database as db

st.set_page_config(page_title="Zarządzanie Flotą", layout="wide")

st.title("🚛 System Zarządzania Flotą")

tab_kierowcy, tab_pojazdy = st.tabs(["👨‍✈️ Kierowcy", "🚚 Pojazdy"])

# =========================================================
# TAB: KIEROWCY
# =========================================================
with tab_kierowcy:
    st.header("Zarządzanie Kierowcami")

    # --- Formularz dodawania nowego kierowcy ---
    with st.expander("➕ Dodaj nowego kierowca", expanded=False):
        with st.form("form_dodaj_kierowce", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                imie = st.text_input("Imię")
                nazwisko = st.text_input("Nazwisko")
                pesel = st.text_input("PESEL")
            with col2:
                paszport = st.text_input("Paszport")
                dowod = st.text_input("Dowód osobisty")
                prawo_jazdy = st.text_input("Prawo jazdy")

            submit_dodaj = st.form_submit_button("Zapisz kierowcę")
            if submit_dodaj:
                if nazwisko or imie:
                    ok, msg = db.dodaj_kierowce(nazwisko, imie, pesel, paszport, dowod, prawo_jazdy)
                    if ok:
                        st.success("Dodano kierowcę pomyślnie!")
                        st.rerun()
                    else:
                        st.error(f"Błąd podczas dodawania do bazy danych: {msg}")
                else:
                    st.warning("Wymagane jest podanie przynajmniej imienia lub nazwiska!")

    st.divider()

    # --- Lista i edycja kierowców ---
    kierowcy = db.pobierz_kierowcow()

    if not kierowcy:
        st.info("Brak kierowców w bazie danych.")
    else:
        st.subheader("Lista kierowców")
        
        for k in kierowcy:
            k_id = k.get("id")
            k_imie = k.get("imie") or ""
            k_nazwisko = k.get("nazwisko") or ""
            k_pesel = k.get("pesel") or ""
            k_paszport = k.get("paszport") or ""
            k_dowod = k.get("dowod_osobisty") or ""
            k_pj = k.get("prawo_jazdy") or ""

            label = f"ID {k_id}: {k_imie} {k_nazwisko}".strip()
            
            with st.expander(label):
                with st.form(f"form_edytuj_kierowce_{k_id}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        e_imie = st.text_input("Imię", value=k_imie, key=f"imie_{k_id}")
                        e_nazwisko = st.text_input("Nazwisko", value=k_nazwisko, key=f"nazwisko_{k_id}")
                        e_pesel = st.text_input("PESEL", value=k_pesel, key=f"pesel_{k_id}")
                    with c2:
                        e_paszport = st.text_input("Paszport", value=k_paszport, key=f"paszport_{k_id}")
                        e_dowod = st.text_input("Dowód osobisty", value=k_dowod, key=f"dowod_{k_id}")
                        e_pj = st.text_input("Prawo jazdy", value=k_pj, key=f"pj_{k_id}")

                    col_btn1, col_btn2 = st.columns([1, 1])
                    with col_btn1:
                        submit_edytuj = st.form_submit_button("💾 Zapisz zmiany")
                    with col_btn2:
                        submit_usun = st.form_submit_button("🗑️ Usuń kierowcę", type="primary")

                    if submit_edytuj:
                        ok, msg = db.edytuj_kierowce(k_id, e_nazwisko, e_imie, e_pesel, e_paszport, e_dowod, e_pj)
                        if ok:
                            st.success("Zaktualizowano dane kierowcy!")
                            st.rerun()
                        else:
                            st.error(f"Błąd edycji: {msg}")

                    if submit_usun:
                        ok, msg = db.usun_kierowce(k_id)
                        if ok:
                            st.success("Usunięto kierowcę!")
                            st.rerun()
                        else:
                            st.error(f"Błąd usuwania: {msg}")

# =========================================================
# TAB: POJAZDY
# =========================================================
with tab_pojazdy:
    st.header("Flota Pojazdów")
    st.write("Sekcja w budowie...")