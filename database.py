import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    try:
        import streamlit as st
        SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
        SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")
    except Exception:
        pass

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# ==================== CIĄGNIKI ====================
def pobierz_ciagniki():
    if not supabase: return []
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
    try:
        supabase.table("ciagniki").insert(data).execute()
        return True, "Sukces"
    except Exception as e:
        return False, str(e)

def edytuj_ciagnik(id_ciagnika, nr_rej, vin, przeglad_data, oc_data):
    data = {
        "nr_rej": nr_rej,
        "vin": vin,
        "przeglad_data": str(przeglad_data) if przeglad_data else None,
        "oc_data": str(oc_data) if oc_data else None
    }
    try:
        supabase.table("ciagniki").update(data).eq("id", id_ciagnika).execute()
        return True, "Sukces"
    except Exception as e:
        return False, str(e)

def usun_ciagnik(id_ciagnika):
    try:
        supabase.table("ciagniki").delete().eq("id", id_ciagnika).execute()
        return True, "Sukces"
    except Exception as e:
        return False, str(e)

# ==================== NACZEPY ====================
def pobierz_naczepy():
    if not supabase: return []
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
    try:
        supabase.table("naczepy").insert(data).execute()
        return True, "Sukces"
    except Exception as e:
        return False, str(e)

def edytuj_naczepe(id_naczepy, nr_rej, vin, przeglad_data, oc_data):
    data = {
        "nr_rej": nr_rej,
        "vin": vin,
        "przeglad_data": str(przeglad_data) if przeglad_data else None,
        "oc_data": str(oc_data) if oc_data else None
    }
    try:
        supabase.table("naczepy").update(data).eq("id", id_naczepy).execute()
        return True, "Sukces"
    except Exception as e:
        return False, str(e)

def usun_naczepe(id_naczepy):
    try:
        supabase.table("naczepy").delete().eq("id", id_naczepy).execute()
        return True, "Sukces"
    except Exception as e:
        return False, str(e)

# ==================== POJAZDY INNE ====================
def pobierz_inne_pojazdy():
    if not supabase: return []
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
        try:
            supabase.table("inne_pojazdy").insert(data).execute()
        except Exception:
            supabase.table("pojazdy_inne").insert(data).execute()
        return True, "Sukces"
    except Exception as e:
        return False, str(e)

def edytuj_inny_pojazd(id_pojazdu, nazwa, nr_rej, vin, przeglad_data, oc_data):
    data = {
        "nazwa": nazwa,
        "nr_rej": nr_rej,
        "vin": vin,
        "przeglad_data": str(przeglad_data) if przeglad_data else None,
        "oc_data": str(oc_data) if oc_data else None
    }
    try:
        try:
            supabase.table("inne_pojazdy").update(data).eq("id", id_pojazdu).execute()
        except Exception:
            supabase.table("pojazdy_inne").update(data).eq("id", id_pojazdu).execute()
        return True, "Sukces"
    except Exception as e:
        return False, str(e)

def usun_inny_pojazd(id_pojazdu):
    try:
        try:
            supabase.table("inne_pojazdy").delete().eq("id", id_pojazdu).execute()
        except Exception:
            supabase.table("pojazdy_inne").delete().eq("id", id_pojazdu).execute()
        return True, "Sukces"
    except Exception as e:
        return False, str(e)

# ==================== KIEROWCY ====================
def pobierz_kierowcow():
    if not supabase: return []
    try:
        res = supabase.table("kierowcy").select("*").order("nazwisko").execute()
        return res.data if res.data is not None else []
    except Exception as e:
        print("Błąd pobierania kierowców:", e)
        return []

def dodaj_kierowce(nazwisko, imie, pesel, paszport, dowod_osobisty, prawo_jazdy, zezwolenie_data=None):
    data = {
        "nazwisko": nazwisko if nazwisko else None,
        "imie": imie if imie else None,
        "pesel": pesel if pesel else None,
        "paszport": paszport if paszport else None,
        "dowod_osobisty": dowod_osobisty if dowod_osobisty else None,
        "prawo_jazdy": prawo_jazdy if prawo_jazdy else None,
        "zezwolenie_data": str(zezwolenie_data) if zezwolenie_data else None
    }
    try:
        supabase.table("kierowcy").insert(data).execute()
        return True, "Sukces"
    except Exception as e:
        return False, str(e)

def edytuj_kierowce(id_kierowcy, nazwisko, imie, pesel, paszport, dowod_osobisty, prawo_jazdy, zezwolenie_data=None):
    data = {
        "nazwisko": nazwisko if nazwisko else None,
        "imie": imie if imie else None,
        "pesel": pesel if pesel else None,
        "paszport": paszport if paszport else None,
        "dowod_osobisty": dowod_osobisty if dowod_osobisty else None,
        "prawo_jazdy": prawo_jazdy if prawo_jazdy else None,
        "zezwolenie_data": str(zezwolenie_data) if zezwolenie_data else None
    }
    try:
        supabase.table("kierowcy").update(data).eq("id", id_kierowcy).execute()
        return True, "Sukces"
    except Exception as e:
        return False, str(e)

def usun_kierowce(id_kierowcy):
    try:
        supabase.table("kierowcy").delete().eq("id", id_kierowcy).execute()
        return True, "Sukces"
    except Exception as e:
        return False, str(e)