import os
from supabase import create_client, Client

# Pobieranie danych logowania do Supabase z sekretów Streamlit / zmiennych środowiskowych
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    try:
        import streamlit as st
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    except Exception:
        pass

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Brak konfiguracji SUPABASE_URL lub SUPABASE_KEY w secrets/env!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==================== CIĄGNIKI ====================
def pobierz_ciagniki():
    res = supabase.table("ciagniki").select("*").order("nr_rej").execute()
    return res.data if res.data is not None else []

def dodaj_ciagnik(nr_rej, vin, przeglad_data, oc_data):
    data = {
        "nr_rej": nr_rej,
        "vin": vin,
        "przeglad_data": str(przeglad_data) if przeglad_data else None,
        "oc_data": str(oc_data) if oc_data else None
    }
    supabase.table("ciagniki").insert(data).execute()

def edytuj_ciagnik(id_ciagnika, nr_rej, vin, przeglad_data, oc_data):
    data = {
        "nr_rej": nr_rej,
        "vin": vin,
        "przeglad_data": str(przeglad_data) if przeglad_data else None,
        "oc_data": str(oc_data) if oc_data else None
    }
    supabase.table("ciagniki").update(data).eq("id", id_ciagnika).execute()

def usun_ciagnik(id_ciagnika):
    supabase.table("ciagniki").delete().eq("id", id_ciagnika).execute()

# ==================== KIEROWCY ====================
def pobierz_kierowcow():
    res = supabase.table("kierowcy").select("*").order("nazwisko", desc=False).execute()
    return res.data if res.data is not None else []

def dodaj_kierowce(nazwisko, imie, pesel, dowod_osobisty, paszport, prawo_jazdy):
    data = {
        "nazwisko": nazwisko,
        "imie": imie,
        "pesel": pesel,
        "dowod_osobisty": dowod_osobisty,
        "paszport": paszport,
        "prawo_jazdy": prawo_jazdy
    }
    supabase.table("kierowcy").insert(data).execute()

def edytuj_kierowce(id_kierowcy, nazwisko, imie, pesel, dowod_osobisty, paszport, prawo_jazdy):
    data = {
        "nazwisko": nazwisko,
        "imie": imie,
        "pesel": pesel,
        "dowod_osobisty": dowod_osobisty,
        "paszport": paszport,
        "prawo_jazdy": prawo_jazdy
    }
    supabase.table("kierowcy").update(data).eq("id", id_kierowcy).execute()

def usun_kierowce(id_kierowcy):
    supabase.table("kierowcy").delete().eq("id", id_kierowcy).execute()

# ==================== NACZEPY ====================
def pobierz_naczepy():
    res = supabase.table("naczepy").select("*").order("nr_rej").execute()
    return res.data if res.data is not None else []

def dodaj_naczepe(nr_rej, vin, przeglad_data, oc_data):
    data = {
        "nr_rej": nr_rej,
        "vin": vin,
        "przeglad_data": str(przeglad_data) if przeglad_data else None,
        "oc_data": str(oc_data) if oc_data else None
    }
    supabase.table("naczepy").insert(data).execute()

def edytuj_naczepe(id_naczepy, nr_rej, vin, przeglad_data, oc_data):
    data = {
        "nr_rej": nr_rej,
        "vin": vin,
        "przeglad_data": str(przeglad_data) if przeglad_data else None,
        "oc_data": str(oc_data) if oc_data else None
    }
    supabase.table("naczepy").update(data).eq("id", id_naczepy).execute()

def usun_naczepe(id_naczepy):
    supabase.table("naczepy").delete().eq("id", id_naczepy).execute()

# ==================== INNE POJAZDY ====================
def pobierz_inne_pojazdy():
    res = supabase.table("inne_pojazdy").select("*").order("nazwa").execute()
    return res.data if res.data is not None else []

def dodaj_inny_pojazd(nazwa, nr_rej, vin, przeglad_data, oc_data):
    data = {
        "nazwa": nazwa,
        "nr_rej": nr_rej,
        "vin": vin,
        "przeglad_data": str(przeglad_data) if przeglad_data else None,
        "oc_data": str(oc_data) if oc_data else None
    }
    supabase.table("inne_pojazdy").insert(data).execute()

def edytuj_inny_pojazd(id_pojazdu, nazwa, nr_rej, vin, przeglad_data, oc_data):
    data = {
        "nazwa": nazwa,
        "nr_rej": nr_rej,
        "vin": vin,
        "przeglad_data": str(przeglad_data) if przeglad_data else None,
        "oc_data": str(oc_data) if oc_data else None
    }
    supabase.table("inne_pojazdy").update(data).eq("id", id_pojazdu).execute()

def usun_inny_pojazd(id_pojazdu):
    supabase.table("inne_pojazdy").delete().eq("id", id_pojazdu).execute()