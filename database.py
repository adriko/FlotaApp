import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Inicjalizacja połączenia z Supabase
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

def init_db():
    """Tabele tworzymy w panelu Supabase (SQL Editor), ta funkcja dba o inicjalizację."""
    pass

# --- LOGOWANIE ---
def zaloguj_uzytkownika(login, haslo):
    # Domyślne logowanie awaryjne
    if login == "admin" and haslo == "admin123":
        return "admin"
    elif login == "spedytor" and haslo == "spedytor123":
        return "odczyt"
    
    # Lub sprawdzanie w bazie Supabase
    res = supabase.table("uzytkownicy").select("*").eq("login", login).eq("haslo", haslo).execute()
    if res.data:
        return res.data[0]["rola"]
    return None

# --- KIEROWCY ---
def dodaj_kierowce(imie, pesel, nr_pj, typ_doc, nr_doc, waznosc_doc, waznosc_karty):
    data = {
        "imie_nazwisko": imie,
        "pesel": pesel,
        "nr_prawo_jazdy": nr_pj,
        "typ_dokumentu": typ_doc,
        "nr_dokumentu": nr_doc,
        "waznosc_dokumentu": str(waznosc_doc),
        "waznosc_karty_kierowcy": str(waznosc_karty)
    }
    supabase.table("kierowcy").insert(data).execute()

def edytuj_kierowce(rec_id, imie, pesel, nr_pj, typ_doc, nr_doc, waznosc_doc, waznosc_karty):
    data = {
        "imie_nazwisko": imie,
        "pesel": pesel,
        "nr_prawo_jazdy": nr_pj,
        "typ_dokumentu": typ_doc,
        "nr_dokumentu": nr_doc,
        "waznosc_dokumentu": str(waznosc_doc),
        "waznosc_karty_kierowcy": str(waznosc_karty)
    }
    supabase.table("kierowcy").update(data).eq("id", rec_id).execute()

def pobierz_kierowcow():
    res = supabase.table("kierowcy").select("*").execute()
    return pd.DataFrame(res.data)

# --- CIĄGNIKI ---
def dodaj_ciagnik(nr_rej, vin, przeglad, oc):
    data = {
        "nr_rej": nr_rej,
        "vin": vin,
        "przeglad_data": str(przeglad),
        "oc_data": str(oc)
    }
    supabase.table("ciagniki").insert(data).execute()

def edytuj_ciagnik(rec_id, nr_rej, vin, przeglad, oc):
    data = {
        "nr_rej": nr_rej,
        "vin": vin,
        "przeglad_data": str(przeglad),
        "oc_data": str(oc)
    }
    supabase.table("ciagniki").update(data).eq("id", rec_id).execute()

def pobierz_ciagniki():
    res = supabase.table("ciagniki").select("*").execute()
    return pd.DataFrame(res.data)

# --- NACZEPY ---
def dodaj_naczepe(nr_rej, przeglad, oc):
    data = {
        "nr_rej": nr_rej,
        "przeglad_data": str(przeglad),
        "oc_data": str(oc)
    }
    supabase.table("naczepy").insert(data).execute()

def edytuj_naczepe(rec_id, nr_rej, przeglad, oc):
    data = {
        "nr_rej": nr_rej,
        "przeglad_data": str(przeglad),
        "oc_data": str(oc)
    }
    supabase.table("naczepy").update(data).eq("id", rec_id).execute()

def pobierz_naczepy():
    res = supabase.table("naczepy").select("*").execute()
    return pd.DataFrame(res.data)

# --- INNE POJAZDY ---
def dodaj_inny_pojazd(typ, nr_rej, vin, przeglad, oc):
    data = {
        "typ_pojazdu": typ,
        "nr_rej": nr_rej,
        "vin": vin,
        "przeglad_data": str(przeglad),
        "oc_data": str(oc)
    }
    supabase.table("inne_pojazdy").insert(data).execute()

def edytuj_inny_pojazd(rec_id, typ, nr_rej, vin, przeglad, oc):
    data = {
        "typ_pojazdu": typ,
        "nr_rej": nr_rej,
        "vin": vin,
        "przeglad_data": str(przeglad),
        "oc_data": str(oc)
    }
    supabase.table("inne_pojazdy").update(data).eq("id", rec_id).execute()

def pobierz_inne_pojazdy():
    res = supabase.table("inne_pojazdy").select("*").execute()
    return pd.DataFrame(res.data)