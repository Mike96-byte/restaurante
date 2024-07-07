import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import plotly_express as px
import datetime

# Titulo de proyecto
st.header(
    "*_Proyecto de Restaurantes para analisis de sus ventas_* :fork_and_knife: :wine_glass:", divider="violet")


def stream_data():
    """Nos ayudara a poner los textos para cada sección"""
    for word in texto.split(" "):
        yield word + " "
        time.sleep(0.02)


# Primero vamos a leer los archivos y combinarlos.

# Leer los archivos
restaurants = pd.read_excel("datos_restaurante.xlsx", sheet_name="Datos")
precios = pd.read_csv("precios_restaurant.csv")

# Combinar los archivos
df_rest = pd.merge(restaurants, precios, on="Producto", how="outer")

# cambiar a minusculas las letras y cambiar los espacios por guines bajos.
new_names = []
for column in df_rest.columns:
    columns_lower = column.lower()
    columns_espacios = columns_lower.replace(" ", "_")
    new_names.append(columns_espacios)
df_rest.columns = new_names

# Cambio de signo de pesos y de tipo de datos
df_rest["precio"] = df_rest["precio"].str.replace("$", "")
df_rest["costo"] = df_rest["costo"].str.replace("$", "")

# Cambio de tipos a float
df_rest["precio"] = df_rest["precio"].astype("float")
df_rest["costo"] = df_rest["costo"].astype("float")

# Cambiamos los tipos de datos para el tiempo


def convert(value):
    """Convierte las fechas si existen en time"""
    if isinstance(value, pd.Timestamp):
        return value.time()
    elif isinstance(value, datetime.datetime):
        return value.time()
    else:
        return value


df_rest["hora_de_cobro"] = df_rest["hora_de_cobro"].apply(convert)

# Obtener nuevas columnas como el mes, venta total, ganancia y más
df_rest["venta_total"] = (
    (df_rest["precio"]*df_rest["propina"]).round(2)) + df_rest["precio"]
df_rest["ganancia"] = df_rest["precio"]-df_rest["costo"]
df_rest["mes"] = df_rest["fecha"].dt.month
df_rest["dia"] = df_rest["fecha"].dt.day
df_rest["hora"] = df_rest["hora_de_cobro"].apply(
    lambda x: x.hour if isinstance(x, datetime.time) else None)
df_rest["propina_total"] = df_rest["propina"]*df_rest["precio"]
df_rest["dia_semana"] = df_rest["fecha"].dt.weekday
# Termina analisis de datos

# Empezamos con el analisis de los datos

texto = """En esta ocasión vamos a hacer un primer analisis exploratorio para un local de restaurante, vamos a analizar sus ventas por día, por hora,
sus propinas, cuales son los productos que más se venden, las categorias y las horas con más ventas. Todo esto con ayuda de los graficos."""

# Boton para poner el texto.
if st.button("Objetivo"):
    st.write_stream(stream_data)

# Titulo principal para el analisis
st.header("Analisis Exploratorio para Datos de un Restaurante", divider="blue")

# Obtenemos las primeras lineas del datafream
st.write(df_rest.head(10))

# Titulo para primer grafica de la distribución de ventas a lo largo del mes (del 1 al 31)
st.subheader(
    "Vamos a observar la distribución de sus ventas totales a lo largo del mes", divider="blue")

# Crear grafico para la distribución de los días
fig = px.histogram(df_rest, x="dia", y="venta_total",
                   nbins=50, color="tipo_x", title="Histograma para distribución de ventas del mes", marginal="box", opacity=0.8)
st.plotly_chart(fig, use_container_width=True)


# Crear histograma para la distribución de ventas durante todo el día
st.subheader("Histograma para las ventas durante el día.", divider="rainbow")
fig4 = px.histogram(df_rest, x="hora", y="venta_total",
                    nbins=24, color="tipo_x", opacity=0.7)
st.plotly_chart(fig4, use_container_width=True)

# Titulo
st.subheader(
    "Ahora vamos a ver los meseros como se comportan con las cuentas", divider="rainbow")

# Grafico para los meseros, vamos a identificar como se comportan con diferentes graficas

# hist_checkbox = st.checkbox("Construir un Histograma")
# scatter_checkbox = st.checkbox("Construir un grafico de dispersión")
# box_checkbox = st.checkbox("Construir diagrama de caja")
# bar_checkbox = st.checkbox("Construir grafico de barras para las propinas")

graficos = st.radio("Seleccionar el grafico que deseas ver", [
    ":rainbow[Histograma]", ":rainbow[Scatter]", ":rainbow[Boxplot]", ":rainbow[Barplot]"], captions=["Construye un Histograma",
                                                                                                      "Construye una grafica de dispersion",
                                                                                                      "Construye un diagrama de caja",
                                                                                                      "Construye una grafica de barras"])

venta_meseros = df_rest.groupby(["atendió", "dia"])[
    "venta_total"].sum().reset_index()

venta_ordenes = df_rest.groupby(["orden", "atendió", "dia"])[
    "precio"].sum().reset_index()

propinas = df_rest.groupby(["atendió", "tipo_de_cliente"])[
    "propina"].mean().reset_index()


if graficos == ":rainbow[Barplot]":
    st.write(
        "Grafica de barras para ver las propinas promedios que reciben los meseros")
    fig8 = px.bar(propinas, x="atendió", y="propina",
                  color=propinas["tipo_de_cliente"])
    st.plotly_chart(fig8, use_container_width=True)

elif graficos == ":rainbow[Histograma]":
    st.write("Histograma para la ditribución de meseros por ventas totales")
    fig1 = px.histogram(df_rest, x="atendió",
                        y="venta_total", color="categoria")
    st.plotly_chart(fig1, use_container_width=True)

elif graficos == ":rainbow[Boxplot]":
    st.write("Diagrama de caja para meseros, de sus ventas por día")
    fig3 = px.box(venta_meseros, x="atendió", y="venta_total")
    st.plotly_chart(fig3)

else:
    st.write("Diagrama de dispersión para los meseros")
    fig2 = px.scatter(venta_ordenes, x="orden", y="precio", color="atendió")
    st.plotly_chart(fig2, use_container_width=True)


st.subheader(
    "Ahora vamos a evaluar cuales son las categorias, alimentos y más que se venden", divider="rainbow")

categorias = df_rest.groupby(["categoria", "tipo_x", "tipo_y", "atendió"])[
    "tipo_de_cliente"].size().reset_index()

meseros = df_rest["atendió"].unique()

fig5 = px.bar(categorias, x="tipo_y", y="tipo_de_cliente",
              title="Categorias más vendidas", color="categoria")
st.plotly_chart(fig5, use_container_width=True)

meseros_categoria = df_rest.groupby(["atendió", "categoria", "tipo_x"])[
    "venta_total"].sum().reset_index()


fig6 = px.bar(meseros_categoria, x="atendió", y="venta_total",
              color="tipo_x")
st.plotly_chart(fig6)

venta_categorias = df_rest.groupby([
    "categoria", "tipo_de_cliente"])["venta_total"].sum().reset_index().sort_values(by="venta_total", ascending=False)

fig7 = px.funnel(venta_categorias, x="venta_total",
                 y="categoria", color=venta_categorias["tipo_de_cliente"])
st.plotly_chart(fig7)


fig17 = px.pie(df_rest, "tipo_x", values="venta_total",
               facet_col="tipo_de_cliente")
st.plotly_chart(fig17)


st.title("Vamos a hacer otro analisis exploratorio con graficas de barras")

# Grafico de barras para venta de productos
st.title("Venta por producto para los mejores 20 productos")
venta_producto = df_rest.groupby(
    "producto")["venta_total"].sum().nlargest(20).reset_index()
fig10 = plt.figure(figsize=(10, 6))

plt.bar(venta_producto["producto"], venta_producto["venta_total"])
labels = venta_producto["producto"].unique()
plt.xticks(venta_producto["producto"], labels, rotation="vertical")
st.pyplot(fig10)

# Venta por tipo de alimentos
st.title("Grafica de barras para ventas por tipo")

# Agrupación de datos de ventas por tipo_y
venta_tipo = df_rest.groupby("tipo_y")["venta_total"].sum(
).reset_index().sort_values(by="venta_total", ascending=False)

# Grafica de barras
fig11 = plt.figure(figsize=(10, 8))
plt.bar(venta_tipo["tipo_y"], venta_tipo["venta_total"])
label11 = venta_tipo["tipo_y"]
plt.xticks(venta_tipo["tipo_y"], label11, rotation="vertical")
st.pyplot(fig11)

# Agrupación de datos por ventas por días
ventas_tiempo = df_rest.groupby("fecha")["venta_total"].sum().reset_index()

# grafica de dispersión
st.title("Grafica de dispersión para las ventas por fechas")
fig12 = plt.figure(figsize=(10, 6))
plt.plot_date(ventas_tiempo["fecha"], ventas_tiempo["venta_total"])
plt.title("Grafica de dispersión de ventas con el tiempo")
plt.xlabel("Fechas")
plt.ylabel("Venta total del día")
st.pyplot(fig12)

# Grafica de lineas
st.title("Grafica de linea para tendencia de las ventas")
fig13 = plt.figure(figsize=(10, 6))
plt.plot(ventas_tiempo["fecha"], ventas_tiempo["venta_total"])
plt.title("Grafica de linea para ver tendencias de ventas")
plt.xlabel("Fechas")
plt.ylabel("Venta total del día")
st.pyplot(fig13)

# Agrupar datos para las propinas a traves del tiempo
propinas_tiempo = df_rest.groupby("fecha")["propina_total"].sum().reset_index()

# Grafica de lineas para las propinas
st.title("Propinas a lo largo del tiempo")
fig14 = plt.figure(figsize=(10, 6))
plt.plot(propinas_tiempo["fecha"], propinas_tiempo["propina_total"])
plt.title("Propinas a lo largo del tiempo")
plt.xlabel("Fechas")
plt.ylabel("Propina total por día")
st.pyplot(fig14)

st.title("Headmap para venta por hora")

venta_dia = df_rest.groupby(["hora", "categoria"])[
    "venta_total"].mean().reset_index()

fig15 = px.density_heatmap(venta_dia, x="hora", y="categoria",
                           text_auto=True, z="venta_total", color_continuous_scale="RdBu", color_continuous_midpoint=1000)
st.plotly_chart(fig15)

# Diagrama de cajas para el ticket promedio por día de la semana.

venta_dia_semana = df_rest.groupby(["dia_semana", "orden"])[
    "venta_total"].sum().reset_index()

fig16 = px.box(data_frame=venta_dia_semana, x="dia_semana",
               y="venta_total")
st.plotly_chart(fig16, use_container_width=True)
