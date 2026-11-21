# Suite de Análisis de Datos — Ferretería

Sistema web que analiza las ventas de una ferretería, **pronostica cuánto se venderá** los próximos días, **calcula qué productos reponer** y **segmenta a los clientes** según cómo compran.

Desarrollado como proyecto de prácticas en SENATI.

---

## ¿Qué hace?

La aplicación tiene cuatro secciones:

| Sección | Qué muestra |
|---|---|
| **📊 Análisis** | Subes un archivo CSV o Excel y la app detecta las columnas para dibujar los gráficos automáticamente. Incluye filtros por rango de fechas y categoría, y tarjetas de resumen. |
| **🔮 Predicción** | Estima la venta de los próximos días con un modelo de Machine Learning. Permite marcar promociones y feriados, y muestra el margen de error del pronóstico. |
| **📦 Stock** | Indica qué productos reponer, cuántas unidades comprar, en cuántos días se acaba el stock actual y permite descargar la lista de compras. |
| **👥 Clientes** | Agrupa a los clientes en VIP, Frecuentes y Ocasionales con K-Means, y muestra cuánto aporta cada segmento a la venta. |

---

## Estructura del proyecto

```
Suite-Analisis-Ferreteria/
│
├── app_dashboard.py        # Aplicación web (Streamlit) con las 4 secciones
├── modelo.py               # Modelo de pronóstico de ventas (Random Forest)
├── clientes.py             # Segmentación de clientes (K-Means)
│
├── catalogo.py             # Crea el catálogo de 100 productos
├── ajustar-precios.py      # Asigna precios realistas por tipo de producto
├── generar-ventas.py       # Genera el historial de ventas con patrones
├── ajustar-stock.py        # Calcula el stock según la demanda
├── sincronizar-db.py       # Copia los datos a ferreteria.db
├── reconstruir.py          # Ejecuta todo el proceso en orden
│
├── ventas.csv              # Historial de ventas
├── productos.csv           # Catálogo de productos
├── clientes.csv            # Clientes de la ferretería
├── calendario.csv          # Promociones y feriados por fecha
├── modelo.pkl              # Modelo entrenado
├── ferreteria.db           # Base de datos SQLite
└── README.md
```

---

## Requisitos

- Python 3.11 o superior
- Las librerías del archivo `requirements.txt` (pandas, numpy, streamlit, plotly, scikit-learn, joblib)

## Instalación

```bash
# 1. Crear y activar el entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows

# 2. Instalar dependencias
pip install -r requirements.txt
```

## Ejecución

```bash
streamlit run app_dashboard.py
```

La aplicación se abre en `http://localhost:8501`.

---

## Regenerar los datos y el modelo

Todo el proceso se reconstruye con un solo comando:

```bash
python reconstruir.py
```

Ese script ejecuta en orden: catálogo → precios → ventas → stock → modelo → base de datos. Usa semillas fijas, así que **siempre genera el mismo resultado**.

> Los datos son simulados, pero con patrones reales de ferretería: ventas más altas los sábados, caída en feriados, aumento en promociones, crecimiento sostenido en el tiempo y clientes que compran con distinta frecuencia.

---

## Modelos de Machine Learning

### Pronóstico de ventas — Random Forest

Predice la venta diaria usando como variables la venta de ayer, la de la semana pasada, el promedio de los últimos 7 y 30 días, el día de la semana, el mes, las promociones y los feriados.

| Métrica | Valor |
|---|---|
| R² (datos de prueba) | **0.61** |
| Error promedio por día | **± S/ 952** (26 %) |
| Error por semana | **± S/ 3.168** (12 %) |

El error baja a la mitad al medir por semana, porque los días en que se vende más compensan los días flojos.

### Segmentación de clientes — K-Means

Agrupa a los clientes con cuatro variables (número de compras, gasto total, ticket promedio y días sin venir), normalizadas con *StandardScaler*.

| Segmento | Clientes | Aporte a la venta |
|---|---|---|
| VIP | 37 | 45,8 % |
| Frecuentes | 144 | 50,6 % |
| Ocasionales | 19 | 3,6 % |

---

## Base de datos

Archivo SQLite `ferreteria.db` con las tablas:

- **Productos** — catálogo con precio y stock
- **Clientes** — datos y tipo de cliente
- **Ventas** — 59 611 registros de venta
- **Calendario** — promociones y feriados por fecha

---

## Resultados del proyecto

- 59 611 ventas procesadas (enero 2024 – octubre 2026)
- S/ 3.250.202 de venta histórica
- 100 productos y 200 clientes analizados
- Pronóstico con R² de 0.61 y 12 % de error semanal
- Reposición automática de stock por producto

---

## Autor

**Edwardpm0310** — Prácticas SENATI
