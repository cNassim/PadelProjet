import sqlite3

def vider_table():
    conn = None
    try:
        conn = sqlite3.connect('padel_corpo.db')
        cursor = conn.cursor()

        cursor.execute("DELETE FROM login_attempts")
        
        cursor.execute("""
            UPDATE sqlite_sequence 
            SET seq = 0 
            WHERE name = 'login_attempts'
        """)
        
        conn.commit()
        print("✅ La table 'login_attempts' a été vidée !")
        
    except sqlite3.OperationalError as e:
        if "no such table: sqlite_sequence" in str(e):
            conn.commit()
            print("✅ La table a été vidée (aucun compteur d'ID à réinitialiser).")
        else:
            print(f" Erreur SQLite : {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    vider_table()