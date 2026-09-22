import sqlite3
import pandas as pd

def get_connection():
    return sqlite3.connect("baza_floty.db", check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # 1. Tabela Kierowców (zaktualizowane pola)
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
    
    # 2. Tabela Ciągników
    c.execute('''
        CREATE TABLE IF NOT EXISTS ciagniki (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nr_rej TEXT,
            vin TEXT,
            przeglad_data DATE,
            oc_data DATE
        )
    ''')
    
    # 3. Tabela Naczep
    c.execute('''
        CREATE TABLE IF NOT EXISTS naczepy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nr_rej TEXT,
            przeglad_data DATE,
            oc_data DATE
        )
    ''')

    # 4. Tabela Inne Pojazdy (busy, osobowe, przyczepy)
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
    conn.close()

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