"""
ajustar-precios.py - Pone precios creibles a cada producto segun su nombre.

Un taladro no cuesta 20 soles ni un tarugo 150. Se busca una palabra clave
en el nombre y se le asigna un rango de precio de ferreteria real.
"""

import numpy as np
import pandas as pd

rng = np.random.default_rng(21)

# (palabra clave en el nombre, precio minimo, precio maximo)
REGLAS = [
    # --- Pinturas ---
    ("4 Galones", 200, 380),
    ("1 Galón", 55, 110),
    ("1/4 Galón", 25, 45),
    ("1 Litro", 12, 22),

    # --- Herramientas electricas ---
    ("Sierra de Banco", 900, 1600),
    ("Hidrolavadora", 500, 900),
    ("Compresor", 500, 900),
    ("Sierra Circular", 350, 700),
    ("Aspiradora Industrial", 400, 800),
    ("Pulidora", 300, 600),
    ("Rotomartillo", 250, 600),
    ("Esmeril Angular", 200, 450),
    ("Amoladora", 180, 380),
    ("Taladro Percutor", 180, 450),
    ("Lijadora", 200, 400),
    ("Caladora", 180, 350),
    ("Atornillador", 150, 400),
    ("Pistola de Calor", 120, 250),

    # --- Materiales electricos ---
    ("Cable Mellizo", 180, 280),
    ("Cable Vulcanizado", 90, 160),
    ("Cable THW", 130, 220),
    ("Tablero Eléctrico", 90, 180),
    ("Breaker", 18, 45),
    ("Tubo Conduit", 12, 22),
    ("Curva Conduit", 3, 6),
    ("Caja Octogonal", 2, 5),
    ("Caja Rectangular", 2, 5),
    ("Tomacorriente", 8, 18),
    ("Interruptor", 7, 15),
    ("Cinta Aislante", 4, 8),
    ("Foco LED", 7, 18),
    ("Portalámpara", 6, 12),

    # --- Plomeria ---
    ("Tubo Desagüe", 25, 60),
    ("Tubo PVC SAP", 12, 35),
    ("Llave Esférica", 15, 45),
    ("Llave de Paso", 18, 40),
    ("Válvula Check", 20, 55),
    ("Unión Universal", 12, 30),
    ("Pegamento PVC", 12, 60),
    ("Teflón", 3, 7),
    ("Inodoro", 250, 450),
    ("Lavadero", 280, 550),
    ("Grifería", 120, 280),
    ("Ducha", 60, 140),
    ("Sifón", 12, 25),
    ("Trampa P", 15, 30),
    ("Flotador", 12, 25),
    ("Codo PVC", 2, 6),
    ("Tee PVC", 3, 8),

    # --- Tornilleria ---
    ("Caja x 500", 28, 45),
    ("Caja x 200", 14, 26),
    ("Caja x 100", 8, 18),
    ("Caja x 50", 10, 20),
    ("x 100 unid", 5, 12),
    ("x 50 unid", 5, 12),
    ("1 kg", 8, 14),
    ("Perno de Anclaje", 4, 10),
    ("Tirafondo", 12, 22),
    ("Remache", 10, 18),
    ("Abrazadera", 10, 20),
    ("Grapa", 8, 15),

    # --- Herramientas manuales ---
    ("Combo", 60, 120),
    ("Juego de Llaves", 80, 180),
    ("Juego de Desarmadores", 45, 90),
    ("Llave Inglesa", 25, 70),
    ("Martillo", 25, 60),
    ("Alicate", 18, 55),
    ("Serrucho", 25, 60),
    ("Nivel", 25, 60),
    ("Formón", 20, 45),
    ("Desarmador", 10, 25),
    ("Wincha", 15, 35),
    ("Flexómetro", 12, 30),
    ("Escuadra", 12, 30),
    ("Cincel", 12, 30),
    ("Lima", 10, 25),
    ("Cuchilla", 8, 18),
]

# Si nada coincide, se usa el rango de la categoria
POR_CATEGORIA = {
    "Pinturas": (30, 120),
    "Eléctricas": (150, 500),
    "Electricidad": (8, 80),
    "Plomería": (8, 80),
    "Tornillería": (5, 30),
    "Herramientas manuales": (12, 60),
}


def precio_para(nombre, categoria):
    for clave, minimo, maximo in REGLAS:
        if clave in nombre:
            return round(float(rng.uniform(minimo, maximo)), 2)
    minimo, maximo = POR_CATEGORIA.get(categoria, (10, 100))
    return round(float(rng.uniform(minimo, maximo)), 2)


productos = pd.read_csv("productos.csv")
productos["precio"] = [precio_para(n, c)
                       for n, c in zip(productos["nombre"], productos["categoria"])]
productos.to_csv("productos.csv", index=False, encoding="utf-8")

print("Precios asignados:", len(productos))
print("Precio minimo: S/", productos["precio"].min())
print("Precio maximo: S/", productos["precio"].max())
print("Precio promedio: S/", round(productos["precio"].mean(), 2))
print("\nLos 5 mas caros:")
print(productos.nlargest(5, "precio")[["nombre", "precio"]].to_string(index=False))
