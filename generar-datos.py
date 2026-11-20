import sqlite3
import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker('es_ES')
random.seed(42)

# 1. Conexión a la base de datos
conn = sqlite3.connect('ferreteria.db')
cursor = conn.cursor()

# 2. Crear tablas
cursor.executescript('''
DROP TABLE IF EXISTS Ventas;
DROP TABLE IF EXISTS Productos;
DROP TABLE IF EXISTS Clientes;

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
''')

# 3. Generar 200 Clientes
clientes = []
tipos = ['Maestro de obra', 'Contratista', 'Público general']
for i in range(1, 201):
    clientes.append((i, fake.name(), fake.nif(), random.choice(tipos)))
cursor.executemany('INSERT INTO Clientes VALUES (?,?,?,?)', clientes)

# 4. Generar 100 Productos
productos = []
categorias = ['Herramientas manuales', 'Eléctricas', 'Pinturas', 'Plomería', 'Electricidad', 'Tornillería']
for i in range(1, 101):
    cat = random.choice(categorias)
    precio = round(random.uniform(5.0, 150.0), 2)
    stock = random.randint(10, 200)
    productos.append((i, f"Producto {cat[:3]} {i}", cat, precio, stock))
cursor.executemany('INSERT INTO Productos VALUES (?,?,?,?,?)', productos)

# 5. Generar 3500 Ventas (entre Agosto y Diciembre 2026)
ventas = []
start_date = datetime(2026, 8, 1)
for i in range(1, 3501):
    fecha = (start_date + timedelta(days=random.randint(0, 150))).strftime('%Y-%m-%d')
    id_cliente = random.randint(1, 200)
    id_prod = random.randint(1, 100)
    cantidad = random.randint(1, 10)
    # Buscar el precio del producto
    precio_unitario = next(p[3] for p in productos if p[0] == id_prod)
    total = round(cantidad * precio_unitario, 2)
    ventas.append((i, fecha, id_cliente, id_prod, cantidad, total))

cursor.executemany('INSERT INTO Ventas VALUES (?,?,?,?,?,?)', ventas)
conn.commit()
conn.close()

print("¡Base de datos 'ferreteria.db' creada con éxito!")
print("Clientes: 200 | Productos: 100 | Ventas: 3500")