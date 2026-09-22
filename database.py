import os
from supabase import create_client, Client

# Pobieranie poświadczeń do Supabase z zmiennych środowiskowych / secrets
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==================== KIEROWCY ====================

def pobierz_kierowcow():
    try:
        res = supabase.table("kierowcy").select("*").order("id").execute()
        return res.data if res.data is not None else []
    except Exception as e:
        print("Błąd pobierania kierowców:", e)
        return []

def dodaj_kierowce(nazwisko, imie, pesel, paszport, dowod_osobisty, prawo_jazdy):
    data = {
        "nazwisko": nazwisko if nazwisko else None,
        "imie": imie if imie else None,
        "pesel": pesel if pesel else None,
        "paszport": paszport if paszport else None,
        "dowod_osobisty": dowod_osobisty if dowod_osobisty else None,
        "prawo_jazdy": prawo_jazdy if prawo_jazdy else None
    }
    try:
        supabase.table("kierowcy").insert(data).execute()
        return True, "Sukces"
    except Exception as e:
        print("Błąd dodawania kierowcy:", e)
        return False, str(e)

def edytuj_kierowce(id_kierowcy, nazwisko, imie, pesel, paszport, dowod_osobisty, prawo_jazdy):
    data = {
        "nazwisko": nazwisko if nazwisko else None,
        "imie": imie if imie else None,
        "pesel": pesel if pesel else None,
        "paszport": paszport if paszport else None,
        "dowod_osobisty": dowod_osobisty if dowod_osobisty else None,
        "prawo_jazdy": prawo_jazdy if prawo_jazdy else None
    }
    try:
        supabase.table("kierowcy").update(data).eq("id", id_kierowcy).execute()
        return True, "Sukces"
    except Exception as e:
        print("Błąd edycji kierowcy:", e)
        return False, str(e)

def usun_kierowce(id_kierowcy):
    try:
        supabase.table("kierowcy").delete().eq("id", id_kierowcy).execute()
        return True, "Sukces"
    except Exception as e:
        print("Błąd usuwania kierowcy:", e)
        return False, str(e)

# ==================== CIĄGNIKI ====================

def pobierz_ciagniki():
    try:
        res = supabase.table("ciagniki").select("*").order("id").execute()
        return res.data if res.data is not None else []
    except Exception as e:
        print("Błąd pobierania ciągników:", e)
        return []

# ==================== NACZEPY ====================

def pobierz_naczepy():
    try:
        res = supabase.table("naczepy").select("*").order("id").execute()
        return res.data if res.data is not None else []
    except Exception as e:
        print("Błąd pobierania naczep:", e)
        return []