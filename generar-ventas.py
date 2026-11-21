"""
generar-ventas.py - Genera ventas con patrones de una ferreteria real.

Sigue siendo data simulada (es una practica), pero ahora tiene logica:
  * viernes y sabado se vende mas, domingo casi nada
  * diciembre y mayo son temporada alta
  * el negocio crece poco a poco
  * hay dias de PROMOCION que suben las ventas
  * los FERIADOS bajan las ventas (medio local cerrado)
  * unos pocos productos son los que mas rotan

Ademas crea calendario.csv, que dice que dia hubo promo y que dia fue feriado.
El modelo necesita ese archivo para aprender.

Uso:  python generar-ventas.py 12000
"""

import sys
import numpy as np
import pandas as pd

SEMILLA = 42
rng = np.random.default_rng(SEMILLA)

OBJETIVO = int(sys.argv[1]) if len(sys.argv) > 1 else 45000

# ------------------------------------------------------------------
# Productos y precios que ya existen
# ------------------------------------------------------------------
productos = pd.read_csv("productos.csv")
ids = productos["id_producto"].to_numpy()
precios = productos["precio"].to_numpy()

# ------------------------------------------------------------------
# Calendario
# ------------------------------------------------------------------
fechas = pd.date_range("2024-01-01", "2026-10-30", freq="D")
n_dias = len(fechas)

# --- Promociones: dias sueltos donde se anuncia oferta ---
promo = (rng.random(n_dias) < 0.12).astype(int)
# los sabados suelen haber promo mas seguido
promo[(fechas.day_of_week == 5) & (rng.random(n_dias) < 0.20)] = 1

# --- Feriados del Peru en ese periodo ---
feriados_fijos = [(1, 1), (5, 1), (6, 29), (7, 28), (7, 29),
                  (8, 30), (10, 8), (11, 1), (12, 8), (12, 25)]
feriado = np.array([1 if (f.month, f.day) in feriados_fijos else 0 for f in fechas])

calendario = pd.DataFrame({"fecha": fechas, "promo": promo, "feriado": feriado})
calendario["fecha"] = calendario["fecha"].dt.strftime("%Y-%m-%d")
calendario.to_csv("calendario.csv", index=False)
print("calendario.csv creado:", len(calendario), "dias")

# ------------------------------------------------------------------
# Factores que mueven la demanda
# ------------------------------------------------------------------
factor_dia = np.array([0.75, 0.70, 0.85, 1.00, 1.20, 1.50, 0.35])   # lunes..domingo
factor_mes = np.array([1.05, 0.92, 1.00, 1.02, 1.10, 1.00,
                       0.95, 0.90, 1.00, 1.06, 1.16, 1.30])
crecimiento = np.linspace(0.86, 1.16, n_dias)

# Rachas suaves de semanas buenas y malas
racha = np.zeros(n_dias)
for i in range(1, n_dias):
    racha[i] = 0.7 * racha[i - 1] + rng.normal(0, 1)
rachas = np.exp(0.05 * racha)

base = np.zeros(n_dias)
for i, f in enumerate(fechas):
    base[i] = factor_dia[f.day_of_week] * factor_mes[f.month - 1] * crecimiento[i]

base = base * rachas
base = base * np.where(promo == 1, 1.65, 1.0)     # promo sube 65%
base = base * np.where(feriado == 1, 0.45, 1.0)   # feriado baja 55%
base = base / base.mean()

# ------------------------------------------------------------------
# Cuantos tickets caen cada dia
# ------------------------------------------------------------------
media_tickets = OBJETIVO / n_dias
tickets = rng.poisson(media_tickets * base)

# ------------------------------------------------------------------
# Popularidad de productos (pocos venden mucho)
# ------------------------------------------------------------------
pesos = (1.0 / precios) ** 0.6
pesos = pesos / pesos.sum()

# ------------------------------------------------------------------
# Armar las ventas
# ------------------------------------------------------------------
# Clientes: no todos compran igual
# Un contratista compra todo el tiempo; el publico general, de vez en cuando.
# ------------------------------------------------------------------
clientes = pd.read_csv("clientes.csv")
peso_tipo = {"Contratista": 3.0, "Maestro de obra": 1.8, "Público general": 0.8}
pesos_cliente = clientes["tipo_cliente"].map(peso_tipo).fillna(1.0).to_numpy()
pesos_cliente = pesos_cliente * rng.lognormal(0, 0.6, len(pesos_cliente))
pesos_cliente = pesos_cliente / pesos_cliente.sum()
ids_cliente = clientes["id_cliente"].to_numpy()

# ------------------------------------------------------------------
registros = []
fecha_de_cada_ticket = np.repeat(fechas.values, tickets)
for fecha in fecha_de_cada_ticket:
    pos = rng.choice(len(ids), p=pesos)
    cantidad = int(rng.integers(1, 4))
    if rng.random() < 0.08:
        cantidad = int(rng.integers(4, 9))
    total = round(cantidad * precios[pos], 2)
    cliente = int(rng.choice(ids_cliente, p=pesos_cliente))
    registros.append((fecha, cliente, ids[pos], cantidad, total))

ventas = pd.DataFrame(registros, columns=["fecha", "id_cliente", "id_producto",
                                          "cantidad", "total"])
ventas.insert(0, "id_venta", range(1, len(ventas) + 1))
ventas["fecha"] = pd.to_datetime(ventas["fecha"]).dt.strftime("%Y-%m-%d")
ventas.to_csv("ventas.csv", index=False, encoding="utf-8")

# ------------------------------------------------------------------
# Reporte
# ------------------------------------------------------------------
diario = ventas.groupby("fecha")["total"].sum()
print("Ventas generadas:", len(ventas))
print("Venta promedio por dia: S/", round(diario.mean(), 2))
print("Dias con promo:", int(promo.sum()), "| Dias feriados:", int(feriado.sum()))
print("\nventas.csv actualizado")
