import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "forgewise.db"

def init_db(db_path=DB_PATH):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS cost_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            customer TEXT NOT NULL,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            estimated_cost REAL NOT NULL,
            actual_cost REAL,
            variance REAL
        )
        """)

def save_cost_review(customer, product, quantity, estimated_cost, actual_cost=None, db_path=DB_PATH):
    init_db(db_path)
    variance = None if actual_cost is None else actual_cost - estimated_cost
    with sqlite3.connect(db_path) as con:
        cur = con.execute(
            "INSERT INTO cost_reviews(created_at, customer, product, quantity, estimated_cost, actual_cost, variance) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (datetime.now().isoformat(timespec="seconds"), customer, product, quantity, estimated_cost, actual_cost, variance)
        )
        return cur.lastrowid

def list_cost_reviews(db_path=DB_PATH, limit=100):
    init_db(db_path)
    with sqlite3.connect(db_path) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT * FROM cost_reviews ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]
