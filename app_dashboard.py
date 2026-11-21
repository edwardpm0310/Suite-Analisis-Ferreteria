"""
app_dashboard.py - Suite de Análisis de Ferretería
Tres secciones:
  1. Análisis    : subes un CSV y salen los gráficos solos
  2. Predicción  : cuánto se estima vender los próximos días
  3. Stock       : qué reponer, cuánto comprar y en cuántos días se acaba
"""

import math
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Dashboard Ferretería", layout="wide", page_icon="🔧")

DIAS_ES = {
    0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
    4: "Viernes", 5: "Sábado", 6: "Domingo",
}
DIAS_FUERTES = {5: "Sábado: el día de más venta", 4: "Viernes: movimiento alto",
                6: "Domingo: casi no se vende"}


# ------------------------------------------------------------------
# Carga de datos y modelo
# ------------------------------------------------------------------
@st.cache_data(ttl=300)
def cargar_datos():
    ventas = pd.read_csv("ventas.csv")
    ventas["fecha"] = pd.to_datetime(ventas["fecha"])
    productos = pd.read_csv("productos.csv")
    return ventas, productos


@st.cache_resource
def cargar_modelo():
    import modelo
    return modelo.cargar()


def falla_modelo(mensaje):
    st.error("No se pudo cargar el modelo: " + mensaje)
    st.info("Ejecuta `python modelo.py` una vez para generarlo.")


# ------------------------------------------------------------------
# Barra lateral
# ------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063822.png", width=80)
    st.title("Menú de Control")
    seccion = st.radio("Ir a:", ["📊 Análisis", "🔮 Predicción", "📦 Stock", "👥 Clientes"])

    with st.expander("❓ ¿Qué hace cada sección?"):
        st.markdown(
            "- **Análisis**: subes un archivo y la app dibuja los gráficos según "
            "las columnas que traiga.\n"
            "- **Predicción**: la app ya tiene el historial guardado y estima "
            "cuánto se venderá los próximos días.\n"
            "- **Stock**: dice qué productos reponer, cuántas unidades comprar y "
            "en cuántos días se acaba cada uno.\n"
            "- **Clientes**: agrupa a los clientes en VIP, Frecuentes y "
            "Ocasionales según cómo compran."
        )

    st.markdown("---")
    st.write("Desarrollado por: Edwardpm0310")
    st.write("Prácticas SENATI")

st.title("📊 Suite de Análisis de Datos - Ferretería")


# ==================================================================
# SECCIÓN 1 : ANÁLISIS
# ==================================================================
if seccion == "📊 Análisis":
    st.subheader("Analiza tus datos")
    st.caption("La app lee las columnas del archivo y decide qué gráfico dibujar. "
               "No necesitas configurar nada.")

    with st.expander("📌 ¿Qué gráfico saca con cada archivo?"):
        st.markdown(
            "- Si el archivo tiene **categoria** y **precio** → barras de precios "
            "por categoría (`productos.csv`).\n"
            "- Si tiene **fecha** y **total** → línea de evolución mensual "
            "(`ventas.csv`).\n"
            "- Si tiene **categoria** y **total** → barras de ingresos por "
            "categoría.\n"
            "- Si no tiene ninguna de esas columnas → solo muestra la tabla "
            "(`clientes.csv`)."
        )

    col_a, col_b = st.columns([2, 1])
    with col_a:
        archivo_subido = st.file_uploader("Sube tu archivo Excel o CSV",
                                          type=["csv", "xlsx"])
    with col_b:
        st.write("")
        st.write("")
        usar_proyecto = st.checkbox("Usar los datos del proyecto",
                                    help="Analiza ventas.csv sin subir nada.")

    df = None
    if archivo_subido is not None:
        try:
            if archivo_subido.name.endswith(".csv"):
                df = pd.read_csv(archivo_subido)
            else:
                df = pd.read_excel(archivo_subido)
            st.success(f"¡Archivo cargado! **{archivo_subido.name}**")
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
    elif usar_proyecto:
        df = pd.read_csv("ventas.csv")
        st.success("Cargados los datos del proyecto: **ventas.csv**")

    if df is not None:
        st.markdown("#### 🔎 Filtros")
        f1, f2 = st.columns(2)
        if "fecha" in df.columns:
            fechas_df = pd.to_datetime(df["fecha"], errors="coerce")
            minimo, maximo = fechas_df.min(), fechas_df.max()
            rango = f1.date_input("Rango de fechas", (minimo, maximo),
                                  help="Muestra solo los datos de ese periodo.")
            if isinstance(rango, tuple) and len(rango) == 2:
                df = df[(fechas_df >= pd.Timestamp(rango[0]))
                        & (fechas_df <= pd.Timestamp(rango[1]))]
        if "categoria" in df.columns:
            categorias_df = sorted(df["categoria"].dropna().unique())
            elegidas_df = f2.multiselect("Categorías", categorias_df, categorias_df,
                                         help="Quita las que no quieras ver.")
            if elegidas_df:
                df = df[df["categoria"].isin(elegidas_df)]
        st.caption(f"Mostrando **{len(df):,}** filas después de filtrar.")

        k1, k2, k3 = st.columns(3)
        k1.metric("Filas", f"{len(df):,}", help="Cada fila es un registro.")
        k2.metric("Columnas", len(df.columns), help=", ".join(df.columns[:6]))
        if "total" in df.columns:
            k3.metric("Suma de la columna total", f"S/ {df['total'].sum():,.0f}",
                      help="Suma de todos los montos del archivo.")
        else:
            k3.metric("Columnas con texto", int((df.dtypes == "object").sum()))

        with st.expander("👀 Ver los datos originales"):
            st.dataframe(df, use_container_width=True)

        st.markdown("### 📈 Visualizaciones Automáticas")
        col1, col2 = st.columns(2)
        dibujo = False

        if "categoria" in df.columns and "total" in df.columns:
            with col1:
                st.subheader("Ventas por Categoría")
                st.caption("Cuánto dinero entró por cada rubro.")
                fig = px.bar(df, x="categoria", y="total", color="categoria",
                             title="Ingresos por Categoría")
                st.plotly_chart(fig, use_container_width=True)
            dibujo = True
        elif "categoria" in df.columns and "precio" in df.columns:
            with col1:
                st.subheader("Precio Promedio por Categoría")
                st.caption("Cuánto cuesta, en promedio, cada rubro.")
                fig = px.bar(df, x="categoria", y="precio", color="categoria",
                             title="Precios")
                st.plotly_chart(fig, use_container_width=True)
            dibujo = True

        if "fecha" in df.columns and "total" in df.columns:
            with col2:
                st.subheader("Tendencia de Ventas")
                st.caption("Cómo se movió la venta mes a mes en todo el historial.")
                df["fecha"] = pd.to_datetime(df["fecha"])
                df_mes = (df.groupby(df["fecha"].dt.to_period("M"))["total"]
                            .sum().reset_index())
                df_mes["fecha"] = df_mes["fecha"].astype(str)
                fig = px.line(df_mes, x="fecha", y="total", title="Evolución Mensual")
                st.plotly_chart(fig, use_container_width=True)
            dibujo = True

        if not dibujo:
            st.warning("Este archivo no tiene las columnas necesarias "
                       "(categoria, precio, fecha o total), así que no hay "
                       "gráfico para mostrar. Arriba ves la tabla.")
    else:
        st.info("👈 Sube un archivo o marca **Usar los datos del proyecto**.")


# ==================================================================
# SECCIÓN 2 : PREDICCIÓN
# ==================================================================
elif seccion == "🔮 Predicción":
    st.subheader("¿Cuánto se va a vender?")
    st.caption("El modelo aprendió del historial: días de la semana, promociones "
               "y feriados.")

    try:
        paquete = cargar_modelo()
    except Exception as e:
        falla_modelo(str(e))
        st.stop()

    c1, c2, c3 = st.columns(3)
    c1.metric("Precisión del modelo (R²)", f"{paquete['r2']:.2f}",
              help="Va de 0 a 1. Indica qué parte de las subidas y bajadas de la "
                   "venta logra explicar el modelo. 0.62 es un buen valor para "
                   "ventas diarias.")
    c2.metric("Error promedio por día", f"S/ {paquete['mae']:,.0f}",
              help="Cuánto suele desviarse el pronóstico de la venta real. "
                   "En la semana baja a S/ " + f"{paquete['mae_semanal']:,.0f}" +
                   " porque los errores de cada día se compensan.")
    c3.metric("Venta diaria típica", f"S/ {paquete['promedio_diario']:,.0f}",
              help="Promedio de los últimos 90 días. Es el nivel normal del negocio.")

    with st.expander("⚙️ Ajustar los próximos días"):
        st.caption("Marca **Promoción** o **Feriado** en el día que corresponda y "
                   "el estimado cambia al instante.")
        dias = st.slider("Días a pronosticar", 1, 14, 7)
        promos, feriados = [], []
        cols = st.columns(min(dias, 7))
        for i in range(min(dias, 7)):
            with cols[i]:
                st.markdown(f"**Día {i + 1}**")
                promos.append(1 if st.checkbox("Promoción", key=f"p{i}") else 0)
                feriados.append(1 if st.checkbox("Feriado", key=f"f{i}") else 0)
        promos += [0] * (dias - len(promos))
        feriados += [0] * (dias - len(feriados))

    import modelo as mod
    pronostico = mod.predecir_dias(paquete, dias=dias, promo=promos, feriado=feriados)

    manana, valor_manana = pronostico[0]
    total_periodo = sum(v for _, v in pronostico)

    m1, m2 = st.columns(2)
    m1.metric(f"Estimado para el {manana}", f"S/ {valor_manana:,.0f}",
              delta=f"± S/ {paquete['mae']:,.0f} de margen",
              help="Margen de error de un solo día.")
    m2.metric(f"Estimado en {dias} días", f"S/ {total_periodo:,.0f}",
              delta=(f"± S/ {paquete['mae_semanal']:,.0f} de margen"
                     if dias >= 7 else None),
              help="Al sumar varios días el error relativo baja mucho: los días "
                   "en que se vende más compensan los días flojos.")

    historial = paquete["serie"].tail(60)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=historial.index, y=historial.values,
                             name="Ventas reales", mode="lines",
                             line=dict(color="#1f77b4")))
    fig.add_trace(go.Scatter(x=[f for f, _ in pronostico], y=[v for _, v in pronostico],
                             name="Pronóstico", mode="lines+markers",
                             line=dict(color="#ff7f0e", dash="dash")))
    fig.update_layout(title="Últimos 60 días y lo que viene",
                      xaxis_title="Fecha", yaxis_title="Soles por día",
                      hovermode="x unified", height=420)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📖 Cómo leer este gráfico"):
        st.markdown(
            "- La línea **azul** son los últimos 60 días reales.\n"
            "- La línea **naranja punteada** es el pronóstico; empieza donde "
            "termina la azul.\n"
            "- Los **huecos hondos** son domingos o feriados.\n"
            "- El **± margen** significa que la venta real puede caer dentro de "
            "ese rango, arriba o abajo.\n"
            "- No esperes que la naranja copie cada pico: lo que importa es el "
            "**nivel** y el **ritmo** semanal."
        )

    filas = []
    for (fecha, valor), p, f in zip(pronostico, promos, feriados):
        dia_semana = pd.Timestamp(fecha).dayofweek
        if f:
            nota = "🔴 Feriado: baja la venta"
        elif p:
            nota = "🟡 Promoción: sube la venta"
        else:
            nota = DIAS_FUERTES.get(dia_semana, "Día normal")
        filas.append({
            "Fecha": fecha,
            "Día": DIAS_ES[dia_semana],
            "Estimado": f"S/ {valor:,.2f}",
            "Rango probable": f"S/ {max(valor - paquete['mae'], 0):,.0f} – "
                              f"S/ {valor + paquete['mae']:,.0f}",
            "Observación": nota,
        })
    tabla = pd.DataFrame(filas)
    st.dataframe(tabla, use_container_width=True, hide_index=True)

    st.download_button("⬇️ Descargar pronóstico (CSV)",
                       tabla.to_csv(index=False).encode("utf-8-sig"),
                       file_name="pronostico.csv", mime="text/csv")


# ==================================================================
# SECCIÓN 3 : STOCK
# ==================================================================
elif seccion == "📦 Stock":
    st.subheader("¿Qué reponer y cuánto comprar?")
    st.caption("Cruza el pronóstico de venta con el stock que tienes hoy en almacén.")

    try:
        paquete = cargar_modelo()
        ventas, productos = cargar_datos()
    except Exception as e:
        falla_modelo(str(e))
        st.stop()

    with st.expander("⚙️ Ajustes"):
        dias_cobertura = st.slider("Días que quieres cubrir con el stock", 3, 30, 7,
                                   help="Cuántos días de venta quieres tener "
                                        "guardados en almacén.")
        categorias = sorted(productos["categoria"].unique())
        elegidas = st.multiselect("Filtrar por categoría", categorias, categorias,
                                  help="Deja vacío para ver todas.")
        buscar = st.text_input("Buscar producto", "",
                               help="Escribe parte del nombre, por ejemplo: clavo.")
        solo_urgentes = st.checkbox("Mostrar solo los que se acaban antes de "
                                    f"{dias_cobertura} días", value=True)

    import modelo as mod
    pronostico = mod.predecir_dias(paquete, dias=dias_cobertura)
    venta_estimada = sum(v for _, v in pronostico)

    # Peso de cada producto en los últimos 90 días
    corte = ventas["fecha"].max() - pd.Timedelta(days=90)
    reciente = ventas[ventas["fecha"] >= corte]
    por_producto = (reciente.groupby("id_producto")["total"].sum()
                           .rename("soles_90d").reset_index())
    total_90d = por_producto["soles_90d"].sum()

    tabla = productos.merge(por_producto, on="id_producto", how="left").fillna({"soles_90d": 0})
    tabla["participacion"] = tabla["soles_90d"] / total_90d if total_90d else 0
    tabla["venta_diaria"] = (tabla["participacion"] * venta_estimada) / dias_cobertura
    tabla["unidades_diarias"] = tabla["venta_diaria"] / tabla["precio"]
    tabla["soles_estimados"] = tabla["participacion"] * venta_estimada
    tabla["unidades_estimadas"] = tabla["soles_estimados"] / tabla["precio"]
    tabla["comprar"] = (tabla["unidades_estimadas"].apply(math.ceil)
                        - tabla["stock"]).clip(lower=0)

    # En cuántos días se acaba el stock actual
    def dias_que_dura(fila):
        if fila["unidades_diarias"] <= 0:
            return 999
        return fila["stock"] / fila["unidades_diarias"]

    tabla["se_acaba_en"] = tabla.apply(dias_que_dura, axis=1)
    tabla["se_acaba"] = tabla["se_acaba_en"].map(
        lambda d: "más de 90 días" if d >= 90 else f"{d:.0f} días")
    tabla["estado"] = tabla.apply(
        lambda f: "🔴 comprar ya" if f["comprar"] > 0 else "🟢 alcanza", axis=1)

    k1, k2, k3 = st.columns(3)
    k1.metric("Venta estimada", f"S/ {venta_estimada:,.0f}", f"en {dias_cobertura} días",
              help="Lo que el modelo espera vender en el periodo que elegiste.")
    k2.metric("Productos a reponer", int((tabla["comprar"] > 0).sum()),
              help="Productos cuyo stock no alcanza para cubrir el periodo.")
    k3.metric("Unidades a comprar", int(tabla["comprar"].sum()),
              help="Suma de todas las unidades que faltan.")

    vista = tabla.copy()
    if elegidas:
        vista = vista[vista["categoria"].isin(elegidas)]
    if buscar:
        vista = vista[vista["nombre"].str.contains(buscar, case=False, na=False)]
    if solo_urgentes:
        vista = vista[vista["se_acaba_en"] < dias_cobertura]

    orden = vista.sort_values(["comprar", "se_acaba_en"], ascending=[False, True])

    st.markdown("#### Productos que necesitan atención")
    if orden.empty:
        st.success("Con esos filtros no hay productos en riesgo. "
                   "Baja el filtro o sube los días a cubrir.")
    else:
        st.dataframe(
            orden[["nombre", "categoria", "precio", "stock", "se_acaba",
                   "unidades_estimadas", "comprar", "estado"]]
            .rename(columns={"nombre": "Producto", "categoria": "Categoría",
                             "precio": "Precio", "stock": "Stock actual",
                             "se_acaba": "Se acaba en",
                             "unidades_estimadas": "Unidades necesarias",
                             "comprar": "Comprar", "estado": "Estado"})
            .round(2),
            use_container_width=True, hide_index=True,
        )

        fig = px.bar(orden[orden["comprar"] > 0].head(15), x="nombre", y="comprar",
                     color="categoria", title="Top 15: unidades a comprar")
        fig.update_layout(xaxis_tickangle=-45, height=430)
        st.plotly_chart(fig, use_container_width=True)

        st.download_button("⬇️ Descargar lista de compras (CSV)",
                           orden[["nombre", "categoria", "stock", "se_acaba",
                                  "unidades_estimadas", "comprar"]]
                           .to_csv(index=False).encode("utf-8-sig"),
                           file_name="lista_de_compras.csv", mime="text/csv")

    with st.expander("🧮 ¿Cómo se calcula todo esto?"):
        st.markdown(
            f"1. El modelo estima que en **{dias_cobertura} días** se venderán "
            f"**S/ {venta_estimada:,.0f}**.\n"
            "2. Esa venta se reparte según cuánto pesa cada producto en los "
            "**últimos 90 días**.\n"
            "3. Se divide entre el precio y salen las **unidades necesarias**.\n"
            "4. Se resta el **stock actual**: lo que falta es lo que hay que "
            "comprar.\n"
            "5. **Se acaba en** = stock actual ÷ unidades que se venden por día."
        )

    with st.expander(f"Ver los {len(productos)} productos"):
        st.dataframe(
            tabla.sort_values("se_acaba_en")[["nombre", "categoria", "precio",
                                              "stock", "se_acaba_en", "comprar"]]
            .rename(columns={"nombre": "Producto", "categoria": "Categoría",
                             "precio": "Precio", "stock": "Stock actual",
                             "se_acaba_en": "Días que dura",
                             "comprar": "Comprar"})
            .round(1),
            use_container_width=True, hide_index=True,
        )


# ==================================================================
# SECCIÓN 4 : CLIENTES
# ==================================================================
elif seccion == "👥 Clientes":
    st.subheader("¿Quiénes son tus clientes?")
    st.caption("La app los agrupa sola con K-Means (aprendizaje no supervisado), "
               "según cuántas veces compran y cuánto gastan.")

    with st.expander("⚙️ Ajustes"):
        grupos = st.slider("Cantidad de grupos", 2, 5, 3,
                           help="Más grupos = segmentos más finos, con menos "
                                "clientes cada uno.")
        buscar_cli = st.text_input("Buscar cliente", "",
                                   help="Escribe parte del nombre.")

    from clientes import segmentar
    tabla_cli, resumen_cli, puntos = segmentar(n_grupos=grupos)

    mejor = resumen_cli.sort_values("participacion", ascending=False).iloc[0]

    k1, k2, k3 = st.columns(3)
    k1.metric("Clientes analizados", len(tabla_cli),
              help="Todos los clientes que registran al menos una compra.")
    k2.metric(f"El más rentable: {mejor['segmento']}",
              f"{mejor['participacion']:.1f}% de la venta",
              help="Porción del dinero total que aporta ese segmento.")
    k3.metric("Ticket promedio", f"S/ {tabla_cli['ticket'].mean():,.2f}",
              help="Gasto promedio por compra, sumando todos los clientes.")

    col1, col2 = st.columns([3, 2])
    with col1:
        visibles = puntos[puntos["gasto"] > 0]
        fig = px.scatter(visibles, x="compras", y="gasto", color="segmento",
                         title="Cada punto es un cliente",
                         labels={"compras": "Número de compras",
                                 "gasto": "Gasto total (S/)",
                                 "segmento": "Segmento"},
                         log_y=True)
        fig.update_layout(height=430)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("#### Resumen por segmento")
        st.dataframe(
            resumen_cli[["segmento", "clientes", "compras_promedio",
                         "gasto_promedio", "participacion"]]
            .rename(columns={"segmento": "Segmento", "clientes": "Clientes",
                             "compras_promedio": "Compras prom.",
                             "gasto_promedio": "Gasto prom. (S/)",
                             "participacion": "% de la venta"})
            .round(1),
            use_container_width=True, hide_index=True)

    with st.expander("📊 Qué significa cada segmento"):
        st.markdown(
            "- **VIP**: compran todo el tiempo y sostienen buena parte de la "
            "venta. Conviene darles crédito, precio por volumen y trato "
            "preferente.\n"
            "- **Frecuentes**: vienen seguido y son el corazón del negocio. "
            "Se mantienen con buen stock y atención rápida.\n"
            "- **Ocasionales**: aparecen de vez en cuando. Se activan con "
            "promociones y recordatorios."
        )

    vista = tabla_cli.copy()
    if buscar_cli:
        vista = vista[vista["nombre"].str.contains(buscar_cli, case=False, na=False)]
    vista = vista.sort_values("gasto", ascending=False)

    st.markdown("#### Detalle por cliente")
    st.dataframe(
        vista[["nombre", "tipo_cliente", "compras", "gasto", "ticket",
               "dias_sin_comprar", "segmento"]]
        .rename(columns={"nombre": "Cliente", "tipo_cliente": "Tipo",
                         "compras": "Compras", "gasto": "Gasto total",
                         "ticket": "Ticket prom.",
                         "dias_sin_comprar": "Días sin venir",
                         "segmento": "Segmento"})
        .round(2),
        use_container_width=True, hide_index=True)

    st.download_button("⬇️ Descargar la segmentación (CSV)",
                       vista[["id_cliente", "nombre", "tipo_cliente", "compras",
                              "gasto", "ticket", "segmento"]]
                       .to_csv(index=False).encode("utf-8-sig"),
                       file_name="segmentacion_clientes.csv", mime="text/csv")

    with st.expander("🧮 ¿Cómo se agrupan?"):
        st.markdown(
            "1. Para cada cliente se calcula: **número de compras**, **gasto "
            "total**, **ticket promedio** y **días sin venir**.\n"
            "2. Esas cuatro medidas se normalizan con *StandardScaler* para que "
            "ninguna pese más que otra.\n"
            "3. K-Means agrupa a los clientes que se parecen entre sí.\n"
            "4. Al grupo que más gasta se le llama **VIP**, y así hacia abajo."
        )
