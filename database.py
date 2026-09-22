import os
from supabase import create_client, Client

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
    raise ValueError("Brak konfiguracji SUPABASE_URL lub SUPABASE_KEY!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==================== CIĄGNIKI ====================
def pobierz_ciagniki():
    try:
        res = supabase.table("ciagniki").select("*").order("nr_rej").execute()
        return res.data if res.data is not None else []
    except Exception as e:
        print("Błąd pobierania ciągników:", e)
        return []

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

# ==================== NACZEPY ====================
def pobierz_naczepy():
    try:
        res = supabase.table("naczepy").select("*").order("nr_rej").execute()
        return res.data if res.data is not None else []
    except Exception as e:
        print("Błąd pobierania naczep:", e)
        return []

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

# ==================== POJAZDY INNE ====================
def pobierz_inne_pojazdy():
    try:
        res = supabase.table("inne_pojazdy").select("*").execute()
        return res.data if res.data is not None else []
    except Exception:
        try:
            res = supabase.table("pojazdy_inne").select("*").execute()
            return res.data if res.data is not None else []
        except Exception as e:
            print("Błąd pobierania innych pojazdów:", e)
            return []

def dodaj_inny_pojazd(nazwa, nr_rej, vin, przeglad_data, oc_data):
    data = {
        "nazwa": nazwa,
        "nr_rej": nr_rej,
        "vin": vin,
        "przeglad_data": str(przeglad_data) if przeglad_data else None,
        "oc_data": str(oc_data) if oc_data else None
    }
    try:
        supabase.table("inne_pojazdy").insert(data).execute()
    except Exception:
        supabase.table("pojazdy_inne").insert(data).execute()

def edytuj_inny_pojazd(id_pojazdu, nazwa, nr_rej, vin, przeglad_data, oc_data):
    data = {
        "nazwa": nazwa,
        "nr_rej": nr_rej,
        "vin": vin,
        "przeglad_data": str(przeglad_data) if przeglad_data else None,
        "oc_data": str(oc_data) if oc_data else None
    }
    try:
        supabase.table("inne_pojazdy").update(data).eq("id", id_pojazdu).execute()
    except Exception:
        supabase.table("pojazdy_inne").update(data).eq("id", id_pojazdu).execute()

def usun_inny_pojazd(id_pojazdu):
    try:
        supabase.table("inne_pojazdy").delete().eq("id", id_pojazdu).execute()
    except Exception:
        supabase.table("pojazdy_inne").delete().eq("id", id_pojazdu).execute()

# ==================== KIEROWCY ====================
def pobierz_kierowcow():
    try:
        res = supabase.table("kierowcy").select("*").execute()
        return res.data if res.data is not None else []
    except Exception as e:
        print("Błąd pobierania kierowców:", e)
        return []

def dodaj_kierowce(nazwisko, imie, pesel, paszport, dowod_osobisty, prawo_jazdy):
    full_name = f"{imie} {nazwisko}".strip()
    
    data = {
        "imie_nazwisko": full_name,
        "nazwisko": nazwisko,
        "imie": imie,
        "pesel": pesel,
        "paszport": paszport,
        "dowod_osobisty": dowod_osobisty,
        "nr_prawo_jazdy": prawo_jazdy,
        "prawo_jazdy": prawo_jazdy
    }
    
    # Obsługa uniwersalnych pól dla paszportu / dowodu
    if paszport:
        data["typ_dokumentu"] = "Paszport"
        data["nr_dokumentu"] = paszport
    elif dowod_osobisty:
        data["typ_dokumentu"] = "Dowód osobisty"
        data["nr_dokumentu"] = dowod_osobisty

    supabase.table("kierowcy").insert(data).execute()

def edytuj_kierowce(id_kierowcy, nazwisko, imie, pesel, paszport, dowod_osobisty, prawo_jazdy):
    full_name = f"{imie} {nazwisko}".strip()
    
    data = {
        "imie_nazwisko": full_name,
        "nazwisko": nazwisko,
        "imie": imie,
        "pesel": pesel,
        "paszport": paszport,
        "dowod_osobisty": dowod_osobisty,
        "nr_prawo_jazdy": prawo_jazdy,
        "prawo_jazdy": prawo_jazdy
    }
    
    if paszport:
        data["typ_dokumentu"] = "Paszport"
        data["nr_dokumentu"] = paszport
    elif dowod_osobisty:
        data["typ_dokumentu"] = "Dowód osobisty"
        data["nr_dokumentu"] = dowod_osobisty

    supabase.table("kierowcy").update(data).eq("id", id_kierowcy).execute()

def usun_kierowce(id_kierowcy):
    supabase.table("kierowcy").delete().eq("id", id_kierowcy).execute()