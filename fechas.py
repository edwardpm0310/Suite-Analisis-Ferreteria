import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta

conn = sqlite3.connect('ferreteria.db')
cursor = conn.cursor()

# Obtener todos los IDs de ventas
cursor.execute("SELECT id_venta FROM Ventas")
ids_ventas = cursor.fetchall()

# Generar fechas desde el 1 de enero de 2024 hasta el 30 de octubre de 2026
start_date = datetime(2024, 1, 1)
end_date = datetime(2026, 10, 30)

for id_venta in ids_ventas:
    # Generar una fecha aleatoria en ese rango
    dias_totales = (end_date - start_date).days
    fecha_aleatoria = start_date + timedelta(days=random.randint(0, dias_totales))
    fecha_str = fecha_aleatoria.strftime('%Y-%m-%d')
    
    # Actualizar en la base de datos
    cursor.execute("UPDATE Ventas SET fecha = ? WHERE id_venta = ?", (fecha_str, id_venta[0]))

conn.commit()
conn.close()

print("¡Fechas actualizadas! Ahora las ventas van del 2024 al 2026.")