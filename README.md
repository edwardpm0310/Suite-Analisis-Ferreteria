# Suite de Análisis de Ferretería 🔧📊

Sistema integral de análisis de datos y Machine Learning desarrollado para el negocio de ferretería (Cerraduras Unidas EIRL). Este proyecto transforma datos crudos de ventas, inventario y clientes en información estratégica para la toma de decisiones.

## 🚀 Características Principales
*   **Procesamiento de Datos:** Limpieza y estructuración de datos con Python (Pandas).
*   **Visualización Interactiva:** Dashboards dinámicos con KPIs, gráficos de tendencia y segmentación de datos.
*   **Machine Learning:** Modelos predictivos para la proyección de ventas y algoritmos de clustering (K-Means) para la segmentación de clientes.
*   **Reportes Automatizados:** Generación automática de resúmenes ejecutivos en texto plano.

## 🛠️ Tecnologías y Herramientas
*   **Lenguaje:** Python 3.x
*   **Análisis y ML:** Pandas, Scikit-Learn, Numpy.
*   **Visualización Web:** Streamlit, Plotly.
*   **Base de Datos:** SQLite (`ferreteria.db`).
*   **Business Intelligence:** Power BI (`aqui.pbix`).
*   **Control de Versiones:** Git y GitHub.

## 📂 Estructura del Proyecto
*   `app_dashboard.py`: Archivo principal de la aplicación web en Streamlit.
*   `ferreteria.db`: Base de datos relacional SQLite con la información del negocio.
*   `ventas.csv`, `clientes.csv`, `productos.csv`: Conjuntos de datos fuente.
*   `generar-datos.py`: Script de Python para la generación y simulación de datos iniciales.
*   `aqui.pbix`: Dashboard interactivo desarrollado en Power BI.
*   `fechas.py`: Módulo auxiliar de gestión de datos temporales.

## ⚙️ Instalación y Ejecución Local
1. Clonar este repositorio:
   ```bash
   git clone https://github.com/TU_USUARIO/Suite-Analisis-Ferreteria.git
