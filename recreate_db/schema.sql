-- Used to recreate the database if necessary

-- SQLite requires this command to actively enforce foreign key constraints
PRAGMA foreign_keys = ON;

-- 1. Procuts Table
CREATE TABLE products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, 
    sku TEXT, 
    category TEXT,
    quantity INTEGER,
    price REAL)

-- 2. Customers Table
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    address TEXT
);

-- 3. Sales Orders Table
CREATE TABLE sales_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    subtotal REAL NOT NULL DEFAULT 0.0,
    tax_rate REAL NOT NULL DEFAULT 0.0,
    tax REAL NOT NULL DEFAULT 0.0,
    total REAL NOT NULL DEFAULT 0.0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT
);

-- 4. Sales Order Lines Table
CREATE TABLE sales_order_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    price REAL NOT NULL DEFAULT 0.0,
    quantity INTEGER NOT NULL DEFAULT 1,
    line_total REAL NOT NULL DEFAULT 0.0,
    FOREIGN KEY (order_id) REFERENCES sales_orders(id) ON DELETE CASCADE
);

