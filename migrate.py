"""
Run this once to create all database tables.
Usage: python migrate.py
"""
from data.connection import get_connection

def migrate():
    with get_connection() as conn:

        # ── Products ──────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                name     TEXT NOT NULL,
                sku      TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                price    REAL NOT NULL DEFAULT 0.0
            )
        """)

        # ── Customers ─────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT NOT NULL,
                email   TEXT,
                phone   TEXT,
                address TEXT
            )
        """)

        # ── Sales Orders ──────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sales_orders (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL REFERENCES customers(id),
                subtotal    REAL NOT NULL DEFAULT 0,
                tax         REAL NOT NULL DEFAULT 0,
                total       REAL NOT NULL DEFAULT 0,
                created_at  TEXT NOT NULL
            )
        """)

        # ── Sales Order Lines ─────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sales_order_lines (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id     INTEGER NOT NULL REFERENCES sales_orders(id),
                product_id   INTEGER NOT NULL REFERENCES products(id),
                product_name TEXT NOT NULL,
                price        REAL NOT NULL,
                quantity     INTEGER NOT NULL DEFAULT 1,
                line_total   REAL NOT NULL
            )
        """)

        # ── Seed sample customers if empty ────────────────────────────────────
        count = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO customers (name, email, phone, address) VALUES (?, ?, ?, ?)",
                [
                    ("Acme Corp",    "orders@acme.com",     "555-0101", "1 Acme Rd, Springfield"),
                    ("Globex Inc",   "buy@globex.com",      "555-0102", "2 Globex Ave, Shelbyville"),
                    ("Initech",      "po@initech.com",      "555-0103", "3 Initech Blvd, Austin"),
                    ("Umbrella Ltd", "supply@umbrella.com", "555-0104", "4 Umbrella St, Raccoon City"),
                ]
            )
            print("Seeded sample customers.")

        print("Migration complete.")


if __name__ == "__main__":
    migrate()
