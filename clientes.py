"""
clientes.py - Segmenta a los clientes con K-Means (aprendizaje no supervisado).

Que hace:
  1. Saca de ventas.csv el comportamiento de cada cliente:
     cuantas compras hizo, cuanto gasto, su ticket promedio y hace cuanto no viene.
  2. Normaliza esas variables para que ninguna pese mas que otra.
  3. Agrupa a los clientes en 3 grupos con K-Means.
  4. Le pone nombre a cada grupo segun cuanto gasta: VIP, Frecuentes, Ocasionales.

Como lo usa la app:
    from clientes import segmentar
    tabla, resumen, puntos = segmentar()
"""

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

VARIABLES = ["compras", "gasto", "ticket", "dias_sin_comprar"]


def preparar_tabla(ventas=None, clientes=None):
    """Devuelve una fila por cliente, con sus numeros de compra."""
    if ventas is None:
        ventas = pd.read_csv("ventas.csv")
        ventas["fecha"] = pd.to_datetime(ventas["fecha"])
    if clientes is None:
        clientes = pd.read_csv("clientes.csv")

    ultima_fecha = ventas["fecha"].max()

    resumen = ventas.groupby("id_cliente").agg(
        compras=("id_venta", "count"),
        gasto=("total", "sum"),
        ultima_compra=("fecha", "max"),
    ).reset_index()

    resumen["ticket"] = resumen["gasto"] / resumen["compras"]
    resumen["dias_sin_comprar"] = (ultima_fecha - resumen["ultima_compra"]).dt.days

    tabla = clientes.merge(resumen, on="id_cliente", how="left").fillna(
        {"compras": 0, "gasto": 0.0, "ticket": 0.0, "dias_sin_comprar": 999})
    tabla["ultima_compra"] = tabla["ultima_compra"].astype(str).replace("NaT", "-")
    return tabla


def segmentar(n_grupos=3, tabla=None):
    """Agrupa a los clientes y devuelve tabla, resumen y puntos para graficar."""
    if tabla is None:
        tabla = preparar_tabla()

    escala = StandardScaler()
    X = escala.fit_transform(tabla[VARIABLES])

    modelo = KMeans(n_clusters=n_grupos, random_state=42, n_init=10)
    tabla = tabla.copy()
    tabla["grupo"] = modelo.fit_predict(X)

    # Nombre del grupo segun el gasto promedio (el que mas gasta = VIP)
    gasto_por_grupo = tabla.groupby("grupo")["gasto"].mean().sort_values(ascending=False)
    etiquetas = ["VIP", "Frecuentes", "Ocasionales", "Grupo 4", "Grupo 5"]
    nombres = {grupo: etiquetas[i] for i, grupo in enumerate(gasto_por_grupo.index)}
    tabla["segmento"] = tabla["grupo"].map(nombres)

    resumen = (tabla.groupby("segmento")
                    .agg(clientes=("id_cliente", "count"),
                         compras_promedio=("compras", "mean"),
                         gasto_total=("gasto", "sum"),
                         gasto_promedio=("gasto", "mean"),
                         ticket_promedio=("ticket", "mean"),
                         dias_sin_venir=("dias_sin_comprar", "mean"))
                    .round(1)
                    .reset_index())
    resumen["participacion"] = (resumen["gasto_total"]
                                / resumen["gasto_total"].sum() * 100).round(1)

    puntos = tabla[["compras", "gasto", "segmento"]].copy()
    return tabla, resumen, puntos


if __name__ == "__main__":
    tabla, resumen, _ = segmentar()
    print("Clientes segmentados:", len(tabla))
    print("\n--- RESUMEN POR SEGMENTO ---")
    print(resumen.to_string(index=False))
    print("\n--- EJEMPLOS VIP ---")
    print(tabla.nlargest(5, "gasto")[["nombre", "tipo_cliente", "compras",
                                      "gasto", "segmento"]].to_string(index=False))
