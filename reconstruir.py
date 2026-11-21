"""
reconstruir.py - Regenera TODO el proyecto en el orden correcto.

Un solo comando:
    python reconstruir.py

Hace, en este orden:
  1. catalogo.py           : catalogo de 100 productos de ferreteria
  2. ajustar-precios.py    : precios creibles
  3. generar-ventas.py     : 30 mil ventas con patrones + calendario.csv
  4. ajustar-stock.py      : stock segun la demanda real
  5. modelo.py             : entrena y guarda modelo.pkl
  6. sincronizar-db.py     : copia todo a ferreteria.db

Todos los pasos usan semilla fija, asi que da siempre el mismo resultado.
"""

import runpy
import sys

PASOS = [
    ("1/6 Catálogo de productos", "catalogo.py", []),
    ("2/6 Precios realistas", "ajustar-precios.py", []),
    ("3/6 Generar ventas", "generar-ventas.py", ["60000"]),
    ("4/6 Ajustar stock", "ajustar-stock.py", []),
    ("5/6 Entrenar modelo", "modelo.py", []),
    ("6/6 Sincronizar base de datos", "sincronizar-db.py", []),
]

for titulo, archivo, argumentos in PASOS:
    print("\n" + "=" * 60)
    print(titulo, "->", archivo)
    print("=" * 60)
    sys.argv = [archivo] + argumentos
    runpy.run_path(archivo, run_name="__main__")

print("\n" + "=" * 60)
print("LISTO. Proyecto reconstruido completo.")
print("=" * 60)
