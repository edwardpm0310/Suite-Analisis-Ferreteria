"""
sincronizar-db.py - Copia los CSV a ferreteria.db.

Asi la base de datos, los archivos CSV y Power BI muestran lo mismo.
Tambien agrega la tabla Calendario (promo y feriado por dia).
"""

import sqlite3
import pandas as pd

conn = sqlite3.connect("ferreteria.db")
cur = conn.cursor()

ventas = pd.read_csv("ventas.csv")
productos = pd.read_csv("productos.csv")
clientes = pd.read_csv("clientes.csv")
calendario = pd.read_csv("calendario.csv")

# --- Tablas de trabajo ---
cur.executescript("""
DROP TABLE IF EXISTS Ventas;
DROP TABLE IF EXISTS Productos;
DROP TABLE IF EXISTS Clientes;
DROP TABLE IF EXISTS Calendario;

CREATE TABLE Clientes (
    id_cliente INTEGER PRIMARY KEY,
    nombre TEXT,
    dni_ruc TEXT,
    tipo_cliente TEXT
);

CREATE TABLE Productos (
    id_producto INTEGER PRIMARY KEY,
    nombre TEXT,
    categoria TEXT,
    precio REAL,
    stock INTEGER
);

CREATE TABLE Ventas (
    id_venta INTEGER PRIMARY KEY,
    fecha DATE,
    id_cliente INTEGER,
    id_producto INTEGER,
    cantidad INTEGER,
    total REAL,
    FOREIGN KEY(id_cliente) REFERENCES Clientes(id_cliente),
    FOREIGN KEY(id_producto) REFERENCES Productos(id_producto)
);

CREATE TABLE Calendario (
    fecha DATE PRIMARY KEY,
    promo INTEGER,
    feriado INTEGER
);
""")

cur.executemany("INSERT INTO Clientes VALUES (?,?,?,?)",
                clientes[["id_cliente", "nombre", "dni_ruc", "tipo_cliente"]].values.tolist())
cur.executemany("INSERT INTO Productos VALUES (?,?,?,?,?)",
                productos[["id_producto", "nombre", "categoria", "precio", "stock"]].values.tolist())
cur.executemany("INSERT INTO Ventas VALUES (?,?,?,?,?,?)",
                ventas[["id_venta", "fecha", "id_cliente", "id_producto",
                        "cantidad", "total"]].values.tolist())
cur.executemany("INSERT INTO Calendario VALUES (?,?,?)",
                calendario[["fecha", "promo", "feriado"]].values.tolist())

conn.commit()

print("Filas por tabla:")
for tabla in ["Clientes", "Productos", "Ventas", "Calendario"]:
    n = cur.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
    print(f"  {tabla:<11} {n}")

venta_total = cur.execute("SELECT ROUND(SUM(total), 2) FROM Ventas").fetchone()[0]
print("Venta total historica: S/", venta_total)

conn.close()
