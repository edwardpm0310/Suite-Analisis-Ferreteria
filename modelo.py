"""
modelo.py - Entrena y usa el modelo que pronostica la venta diaria.

Que hace:
  1. Junta las ventas por dia desde ventas.csv.
  2. Le ensena al modelo con el 80% mas antiguo del historial.
  3. Lo examina con el 20% mas reciente (datos que nunca vio) y muestra R2.
  4. Reentrena con TODO el historial y guarda modelo.pkl.
  5. Deja lista una funcion para pronosticar los proximos dias.

Como lo llama la app:
    from modelo import cargar, predecir_dias
    paquete = cargar()
    pronostico = predecir_dias(paquete, dias=7, promo=[0,1,0,0,0,0,0])
"""

import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

ARCHIVO_VENTAS = "ventas.csv"
ARCHIVO_CALENDARIO = "calendario.csv"
ARCHIVO_MODELO = "modelo.pkl"

COLUMNAS = ["dia_semana", "mes", "promo", "feriado", "lag1", "lag7", "prom7", "prom30"]


# ------------------------------------------------------------------
# 1. Preparar la tabla de entrenamiento
# ------------------------------------------------------------------
def preparar_datos(ventas, calendario):
    ventas = ventas.copy()
    ventas["fecha"] = pd.to_datetime(ventas["fecha"])
    diario = ventas.groupby("fecha")["total"].sum().asfreq("D").fillna(0)

    cal = calendario.copy()
    cal["fecha"] = pd.to_datetime(cal["fecha"])
    cal = cal.set_index("fecha")

    d = pd.DataFrame({"total": diario})
    d["lag1"] = diario.shift(1)                       # ayer
    d["lag7"] = diario.shift(7)                       # mismo dia, semana pasada
    d["prom7"] = diario.shift(1).rolling(7).mean()    # promedio ultima semana
    d["prom30"] = diario.shift(1).rolling(30).mean()  # promedio ultimo mes
    d["dia_semana"] = diario.index.day_of_week
    d["mes"] = diario.index.month
    d["promo"] = cal["promo"].reindex(diario.index).fillna(0).astype(int).values
    d["feriado"] = cal["feriado"].reindex(diario.index).fillna(0).astype(int).values
    return d.dropna()


def crear_modelo():
    return RandomForestRegressor(
        n_estimators=700,
        max_features=0.5,
        random_state=42,
        n_jobs=-1,
    )


# ------------------------------------------------------------------
# 2. Entrenar y medir
# ------------------------------------------------------------------
def entrenar(guardar=True):
    ventas = pd.read_csv(ARCHIVO_VENTAS)
    calendario = pd.read_csv(ARCHIVO_CALENDARIO)
    datos = preparar_datos(ventas, calendario)

    corte = int(len(datos) * 0.8)

    examen = crear_modelo()
    examen.fit(datos[COLUMNAS][:corte], datos["total"][:corte])
    pred = examen.predict(datos[COLUMNAS][corte:])
    real = datos["total"][corte:]

    r2 = r2_score(real, pred)
    mae = mean_absolute_error(real, pred)

    # Error si miramos la semana completa (los errores diarios se compensan)
    pred_serie = pd.Series(pred, index=datos.index[corte:])
    semana_real = real.resample("W-MON").sum().iloc[1:-1]
    semana_pred = pred_serie.resample("W-MON").sum().iloc[1:-1]
    mae_semanal = mean_absolute_error(semana_real, semana_pred)

    print("Dias de historia:", len(datos))
    print("--- EXAMEN (datos que el modelo nunca vio) ---")
    print("R2 :", round(r2, 4))
    print("MAE:", round(mae, 2), "soles por dia")
    print("MAE semanal:", round(mae_semanal, 2), "soles por semana")
    print("Venta promedio real por dia: S/", round(real.mean(), 2))
    print("Se equivoca en un", round(mae / real.mean() * 100, 1), "%")
    print("En la semana se equivoca en un",
          round(mae_semanal / semana_real.mean() * 100, 1), "%")

    # Reentrenar con todo y guardar
    final = crear_modelo()
    final.fit(datos[COLUMNAS], datos["total"])
    serie = datos["total"]

    paquete = {
        "modelo": final,
        "columnas": COLUMNAS,
        "serie": serie,
        "r2": r2,
        "mae": mae,
        "mae_semanal": mae_semanal,
        "promedio_diario": serie.iloc[-90:].mean(),
    }
    if guardar:
        joblib.dump(paquete, ARCHIVO_MODELO, compress=3)
        print("\nGuardado en", ARCHIVO_MODELO)
    return paquete


# ------------------------------------------------------------------
# 3. Pronosticar dias que aun no existen
# ------------------------------------------------------------------
def predecir_dias(paquete, dias=7, promo=None, feriado=None):
    """
    Devuelve una lista de (fecha, soles_estimados).
    Trabaja dia por dia: lo que pronostica hoy le sirve de 'ayer' manana.
    """
    modelo = paquete["modelo"]
    columnas = paquete["columnas"]
    serie = paquete["serie"].copy()

    promo = list(promo) if promo is not None else [0] * dias
    feriado = list(feriado) if feriado is not None else [0] * dias
    promo = (promo + [0] * dias)[:dias]
    feriado = (feriado + [0] * dias)[:dias]

    salida = []
    for i in range(dias):
        fecha = serie.index.max() + pd.Timedelta(days=1)
        fila = {
            "dia_semana": fecha.day_of_week,
            "mes": fecha.month,
            "promo": promo[i],
            "feriado": feriado[i],
            "lag1": serie.iloc[-1],
            "lag7": serie.iloc[-7],
            "prom7": serie.iloc[-7:].mean(),
            "prom30": serie.iloc[-30:].mean(),
        }
        valor = float(modelo.predict(pd.DataFrame([fila])[columnas])[0])
        serie.loc[fecha] = valor
        salida.append((fecha.date(), round(valor, 2)))
    return salida


def cargar():
    return joblib.load(ARCHIVO_MODELO)


# ------------------------------------------------------------------
# 4. Si se ejecuta directo: entrenar y mostrar los proximos 7 dias
# ------------------------------------------------------------------
if __name__ == "__main__":
    paquete = entrenar()

    print("\n--- PRONOSTICO PROXIMOS 7 DIAS ---")
    total = 0
    for fecha, valor in predecir_dias(paquete, dias=7):
        print(fecha, "->  S/", f"{valor:,.2f}")
        total += valor
    print("Semana estimada: S/", f"{total:,.2f}")
