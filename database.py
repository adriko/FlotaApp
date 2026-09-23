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

# ==================== FUNKCJE POMOCNICZE ====================
def czy_pojazd_istnieje(tabela, vin, nr_rej):
    """
    Sprawdza unikalność:
    1. Najpierw sprawdza VIN (jeśli wpisany).
    2. Jeśli brakuje VIN – sprawdza numer rejestracyjny.
    """
    if not supabase:
        return False, ""
    
    # 1. Sprawdzenie po VIN
    if vin and str(vin).strip():
        res = supabase.table(tabela).select("id").eq("vin", str(vin).strip()).execute()
        if res.data and len(res.data) > 0:
            return True, f"Pojazd o numerze VIN '{vin}' już istnieje w bazie!"

    # 2. Sprawdzenie po numerze rejestracyjnym (tylko gdy brak VIN)
    elif nr_rej and str(nr_rej).strip():
        res = supabase.table(tabela).select("id").eq("nr_rej", str(nr_rej).strip()).execute()
        if res.data and len(res.data) > 0:
            return True, f"Pojazd o numerze rejestracyjnym '{nr_rej}' już istnieje w bazie!"

    return False, ""

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
    istnieje, msg = czy_pojazd_istnieje("ciagniki", vin, nr_rej)
    if istnieje:
        return False, msg

    data = {
        "nr_rej": nr_rej.strip() if nr_rej else None,
        "vin": vin.strip() if vin and str(vin).strip() else None,
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
        "nr_rej": nr_rej.strip() if nr_rej else None,
        "vin": vin.strip() if vin and str(vin).strip() else None,
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
    istnieje, msg = czy_pojazd_istnieje("naczepy", vin, nr_rej)
    if istnieje:
        return False, msg

    data = {
        "nr_rej": nr_rej.strip() if nr_rej else None,
        "vin": vin.strip() if vin and str(vin).strip() else None,
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
        "nr_rej": nr_rej.strip() if nr_rej else None,
        "vin": vin.strip() if vin and str(vin).strip() else None,
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
    except Exception as e:
        print("Błąd pobierania innych pojazdów:", e)
        return []

def dodaj_inny_pojazd(typ_pojazdu, nr_rej, vin, przeglad_data, oc_data):
    istnieje, msg = czy_pojazd_istnieje("inne_pojazdy", vin, nr_rej)
    if istnieje:
        return False, msg

    data = {
        "typ_pojazdu": typ_pojazdu.strip() if typ_pojazdu else None,
        "nr_rej": nr_rej.strip() if nr_rej else None,
        "vin": vin.strip() if vin and str(vin).strip() else None,
        "przeglad_data": str(przeglad_data) if przeglad_data else None,
        "oc_data": str(oc_data) if oc_data else None
    }
    try:
        supabase.table("inne_pojazdy").insert(data).execute()
        return True, "Sukces"
    except Exception as e:
        return False, str(e)

def edytuj_inny_pojazd(id_pojazdu, typ_pojazdu, nr_rej, vin, przeglad_data, oc_data):
    data = {
        "typ_pojazdu": typ_pojazdu.strip() if typ_pojazdu else None,
        "nr_rej": nr_rej.strip() if nr_rej else None,
        "vin": vin.strip() if vin and str(vin).strip() else None,
        "przeglad_data": str(przeglad_data) if przeglad_data else None,
        "oc_data": str(oc_data) if oc_data else None
    }
    try:
        supabase.table("inne_pojazdy").update(data).eq("id", id_pojazdu).execute()
        return True, "Sukces"
    except Exception as e:
        return False, str(e)

def usun_inny_pojazd(id_pojazdu):
    try:
        supabase.table("inne_pojazdy").delete().eq("id", id_pojazdu).execute()
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
        "nazwisko": nazwisko.strip() if nazwisko else None,
        "imie": imie.strip() if imie else None,
        "pesel": pesel.strip() if pesel else None,
        "paszport": paszport.strip() if paszport else None,
        "dowod_osobisty": dowod_osobisty.strip() if dowod_osobisty else None,
        "prawo_jazdy": prawo_jazdy.strip() if prawo_jazdy else None,
        "zezwolenie_data": str(zezwolenie_data) if zezwolenie_data else None
    }
    try:
        supabase.table("kierowcy").insert(data).execute()
        return True, "Sukces"
    except Exception as e:
        return False, str(e)

def edytuj_kierowce(id_kierowcy, nazwisko, imie, pesel, paszport, dowod_osobisty, prawo_jazdy, zezwolenie_data=None):
    data = {
        "nazwisko": nazwisko.strip() if nazwisko else None,
        "imie": imie.strip() if imie else None,
        "pesel": pesel.strip() if pesel else None,
        "paszport": paszport.strip() if paszport else None,
        "dowod_osobisty": dowod_osobisty.strip() if dowod_osobisty else None,
        "prawo_jazdy": prawo_jazdy.strip() if prawo_jazdy else None,
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