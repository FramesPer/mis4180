import sqlite3

# FIXME: sqlite3.IntegrityError: UNIQUE constraint failed: users_table.username
def init_backend():
    con = sqlite3.connect("backend.db")
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS user (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            password TEXT NOT NULL);""")
    con.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS hologram (
                hologram_id INTEGER PRIMARY KEY UNIQUE,
                building_dimensions TEXT NOT NULL,
                building_style TEXT NOT NULL,
                building_type TEXT NOT NULL,
                purpose TEXT,
                additional_info TEXT,
                status TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id)
                    REFERENCES user (user_id)
                );""")

    con.commit()
    con.close()

def unsafe_db_init():
    con = sqlite3.connect("backend_unsafe.db")
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS unsafe_holo (
                hologram_id INTEGER PRIMARY KEY UNIQUE,
                building_dimensions TEXT,
                building_style TEXT NOT NULL,
                building_type TEXT NOT NULL,
                purpose TEXT,
                additional_info TEXT
                );""")

    con.commit()
    con.close()

def fetch_email(user):
    con = sqlite3.connect("backend.db")
    cur = con.cursor()
    cur.execute("""SELECT email FROM user WHERE username = ?""", (user,))
    user_email = cur.fetchone()
    con.close()
    return user_email

def recent_order_number(username):
    con = sqlite3.connect("backend.db")
    cur = con.cursor()
    cur.execute("""
        SELECT h.hologram_id
        FROM hologram h
        JOIN user u ON h.user_id = u.user_id
        WHERE u.username = ?
        ORDER BY h.hologram_id DESC
        LIMIT 1
    """, (username,))
    last_order = cur.fetchone()
    con.close()

    return last_order[0] if last_order else None

def update_database_status(updates):
    con = sqlite3.connect("backend.db")
    cur = con.cursor()
    for change in updates:
        print("[DIFF] {}".format(change))
        cur.execute("""
            UPDATE hologram 
            SET status = ?
            WHERE hologram_id = ?
        """, (change[len(change)-1], change[0]))

    con.commit()
    con.close()
