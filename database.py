import sqlite3
import pandas as pd
import hashlib

def get_connection():
    return sqlite3.connect("baza_floty.db", check_same_thread=False)

# Helper do szyfrowania haseł
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # 1. Tabela Użytkowników
    c.execute('''
        CREATE TABLE IF NOT EXISTS uzytkownicy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE,
            haslo TEXT,
            rola TEXT
        )
    ''')
    
    # 2. Tabela Kierowców
    c.execute('''
        CREATE TABLE IF NOT EXISTS kierowcy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imie_nazwisko TEXT,
            pesel TEXT,
            nr_prawo_jazdy TEXT,
            typ_dokumentu TEXT,
            nr_dokumentu TEXT,
            waznosc_dokumentu DATE,
            waznosc_karty_kierowcy DATE
        )
    ''')
    
    # 3. Tabela Ciągników
    c.execute('''
        CREATE TABLE IF NOT EXISTS ciagniki (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nr_rej TEXT,
            vin TEXT,
            przeglad_data DATE,
            oc_data DATE
        )
    ''')
    
    # 4. Tabela Naczep
    c.execute('''
        CREATE TABLE IF NOT EXISTS naczepy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nr_rej TEXT,
            przeglad_data DATE,
            oc_data DATE
        )
    ''')

    # 5. Tabela Inne Pojazdy
    c.execute('''
        CREATE TABLE IF NOT EXISTS inne_pojazdy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            typ_pojazdu TEXT,
            nr_rej TEXT,
            vin TEXT,
            przeglad_data DATE,
            oc_data DATE
        )
    ''')
    
    conn.commit()

    # Tworzenie domyślnych kont, jeśli tabela użytkowników jest pusta
    c.execute("SELECT COUNT(*) FROM uzytkownicy")
    if c.fetchone()[0] == 0:
        # Domyślny admin: admin / admin123
        c.execute("INSERT INTO uzytkownicy (login, haslo, rola) VALUES (?, ?, ?)",
                  ("admin", make_hashes("admin123"), "admin"))
        # Domyślny użytkownik odczytu: spedytor / spedytor123
        c.execute("INSERT INTO uzytkownicy (login, haslo, rola) VALUES (?, ?, ?)",
                  ("spedytor", make_hashes("spedytor123"), "odczyt"))
        conn.commit()

    conn.close()

# --- FUNKCJE LOGOWANIA ---
def zaloguj_uzytkownika(login, haslo):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT rola, haslo FROM uzytkownicy WHERE login = ?", (login,))
    data = c.fetchone()
    conn.close()
    if data:
        rola, hashed_pw = data[0], data[1]
        if check_hashes(haslo, hashed_pw):
            return rola
    return None

# --- FUNKCJE DLA KIEROWCÓW ---
def dodaj_kierowce(imie, pesel, nr_pj, typ_doc, nr_doc, waznosc_doc, waznosc_karty):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO kierowcy 
        (imie_nazwisko, pesel, nr_prawo_jazdy, typ_dokumentu, nr_dokumentu, waznosc_dokumentu, waznosc_karty_kierowcy) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (imie, pesel, nr_pj, typ_doc, nr_doc, waznosc_doc, waznosc_karty))
    conn.commit()
    conn.close()

def pobierz_kierowcow():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM kierowcy", conn)
    conn.close()
    return df

# --- FUNKCJE DLA CIĄGNIKÓW ---
def dodaj_ciagnik(nr_rej, vin, przeglad, oc):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO ciagniki (nr_rej, vin, przeglad_data, oc_data) VALUES (?, ?, ?, ?)', (nr_rej, vin, przeglad, oc))
    conn.commit()
    conn.close()

def pobierz_ciagniki():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM ciagniki", conn)
    conn.close()
    return df

# --- FUNKCJE DLA NACZEP ---
def dodaj_naczepe(nr_rej, przeglad, oc):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO naczepy (nr_rej, przeglad_data, oc_data) VALUES (?, ?, ?)', (nr_rej, przeglad, oc))
    conn.commit()
    conn.close()

def pobierz_naczepy():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM naczepy", conn)
    conn.close()
    return df

# --- FUNKCJE DLA INNYCH POJAZDÓW ---
def dodaj_inny_pojazd(typ, nr_rej, vin, przeglad, oc):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO inne_pojazdy (typ_pojazdu, nr_rej, vin, przeglad_data, oc_data) VALUES (?, ?, ?, ?, ?)', (typ, nr_rej, vin, przeglad, oc))
    conn.commit()
    conn.close()

def pobierz_inne_pojazdy():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM inne_pojazdy", conn)
    conn.close()
    return df