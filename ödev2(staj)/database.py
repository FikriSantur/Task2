import sqlite3

def create_table():
    conn = sqlite3.connect('files.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dosyalar (
            id INTEGER PRIMARY KEY,
            dosya_adi TEXT,
            yazar TEXT,
            olusturma_tarihi TEXT,
            sahibi TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_file(dosya_adi, yazar, olusturma_tarihi, sahibi):
    conn = sqlite3.connect('files.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO dosyalar (dosya_adi, yazar, olusturma_tarihi, sahibi)
        VALUES (?, ?, ?, ?)
    ''', (dosya_adi, yazar, olusturma_tarihi, sahibi))
    conn.commit()
    conn.close()

def clear_all_data():
    conn = sqlite3.connect('files.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dosyalar")
    conn.commit()
    conn.close()
