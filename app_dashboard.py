import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página web
st.set_page_config(page_title="Dashboard Ferretería", layout="wide", page_icon="🔧")

# 2. Barra lateral (Menú)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063822.png", width=80) # Ícono de ferretería
    st.title("Menú de Control")
    archivo_subido = st.file_uploader("Sube tu archivo Excel o CSV", type=["csv", "xlsx"])
    st.markdown("---")
    st.write("Desarrollado por: Edwardpm0310")
    st.write("Prácticas SENATI")

# 3. Título principal
st.title("📊 Suite de Análisis de Datos - Ferretería")
st.markdown("Bienvenido al sistema interactivo. Sube tu archivo para generar los gráficos automáticamente.")

# 4. Lógica principal de la App
if archivo_subido is not None:
    try:
        # Leer el archivo dependiendo del formato
        if archivo_subido.name.endswith('.csv'):
            df = pd.read_csv(archivo_subido)
        else:
            df = pd.read_excel(archivo_subido)
        
        st.success("¡Archivo cargado exitosamente!")
        
        # Mostrar los datos crudos
        with st.expander("👀 Ver los datos originales"):
            st.dataframe(df)
            
        # --- GRÁFICOS DINÁMICOS ---
        st.markdown("### 📈 Visualizaciones Automáticas")
        
        # Creamos dos columnas para los gráficos
        col1, col2 = st.columns(2)
        
        # Si el archivo tiene columnas de categoría y total (como el de productos/ventas)
        if 'categoria' in df.columns and 'total' in df.columns:
            with col1:
                st.subheader("Ventas por Categoría")
                fig_bar = px.bar(df, x='categoria', y='total', color='categoria', title="Ingresos por Categoría")
                st.plotly_chart(fig_bar, use_container_width=True)
        elif 'categoria' in df.columns and 'precio' in df.columns:
             with col1:
                st.subheader("Precio Promedio por Categoría")
                fig_bar = px.bar(df, x='categoria', y='precio', color='categoria', title="Precios")
                st.plotly_chart(fig_bar, use_container_width=True)
                
        # Si el archivo tiene columna de fecha (como el de ventas)
        if 'fecha' in df.columns and 'total' in df.columns:
            with col2:
                st.subheader("Tendencia de Ventas")
                # Convertir a fecha
                df['fecha'] = pd.to_datetime(df['fecha'])
                df_mes = df.groupby(df['fecha'].dt.to_period('M'))['total'].sum().reset_index()
                df_mes['fecha'] = df_mes['fecha'].astype(str)
                fig_line = px.line(df_mes, x='fecha', y='total', title="Evolución Mensual")
                st.plotly_chart(fig_line, use_container_width=True)

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    # Mensaje que se ve antes de subir el archivo
    st.info("👈 Por favor, sube un archivo en el menú de la izquierda para comenzar.")