"""
ajustar-stock.py - Pone el stock de cada producto en una cantidad creible.

Antes el stock era un numero al azar entre 10 y 200, sin relacion con lo que
se vende. Ahora se calcula segun la demanda real de los ultimos 30 dias:
cada producto guarda entre 2 y 25 dias de venta, asi que unos cuantos quedan
cortos y hay que reponerlos (que es justo lo que la app debe mostrar).
"""

import numpy as np
import pandas as pd

rng = np.random.default_rng(7)

ventas = pd.read_csv("ventas.csv")
ventas["fecha"] = pd.to_datetime(ventas["fecha"])
productos = pd.read_csv("productos.csv")

corte = ventas["fecha"].max() - pd.Timedelta(days=30)
reciente = ventas[ventas["fecha"] >= corte]

unidades_30d = (reciente.groupby("id_producto")["cantidad"].sum()
                        .rename("unidades_30d").reset_index())
productos = productos.merge(unidades_30d, on="id_producto", how="left")
productos["unidades_30d"] = productos["unidades_30d"].fillna(0)

nuevo_stock = []
for u in productos["unidades_30d"]:
    diario = u / 30.0
    if diario < 0.1:
        # producto que casi no rota: se guarda poquito
        nuevo_stock.append(int(rng.integers(0, 4)))
    else:
        dias_que_guarda = rng.uniform(2, 25)     # algunos con 2 dias, otros con 25
        nuevo_stock.append(int(round(diario * dias_que_guarda)))

productos["stock"] = nuevo_stock
productos = productos.drop(columns=["unidades_30d"])
productos.to_csv("productos.csv", index=False, encoding="utf-8")

print("Productos actualizados:", len(productos))
print("Stock total en almacen:", int(productos["stock"].sum()), "unidades")
print("Productos con stock 0:", int((productos["stock"] == 0).sum()))
print("Stock promedio por producto:", round(productos["stock"].mean(), 1))
