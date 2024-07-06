import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import plotly_express as px
import datetime

# Titulo de proyecto
st.header("Proyecto de Restaurantes para analisis de sus ventas")

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


st.title("Analisis Exploratorio para Datos de un Restaurante")

st.write(df_rest.head(10))

st.write("Vamos a observar la distribución de sus ventas totales a lo largo del mes")

# Crear grafico para la distribución de los días
fig = px.histogram(df_rest, x="dia", y="venta_total", nbins=50)
st.plotly_chart(fig, use_container_width=True)


# Crear histograma para la distribución de ventas durante todo el día
st.write("Histograma para las ventas durante el día.")
fig4 = px.histogram(df_rest, x="hora", y="venta_total",
                    nbins=24, color=df_rest["tipo_x"])
st.plotly_chart(fig4, use_container_width=True)


st.write("Ahora vamos a ver los meseros como se comportan con las cuentas")

# Grafico para los meseros, vamos a identificar como se comportan con diferentes graficas

hist_button = st.button("Construir un Histograma")
scatter_button = st.button("Construir un grafico de dispersión")
box_button = st.button("Construir diagrama de caja")
bar_button = st.button("Construir grafico de barras para las propinas")

venta_meseros = df_rest.groupby(["atendió", "dia"])[
    "venta_total"].sum().reset_index()

venta_ordenes = df_rest.groupby(["orden", "atendió", "dia"])[
    "precio"].sum().reset_index()

propinas = df_rest.groupby(["atendió", "tipo_de_cliente"])[
    "propina"].mean().reset_index()

if hist_button:
    st.write("Histograma para la ditribución de meseros por ventas totales")
    fig1 = px.histogram(df_rest, x="atendió", y="venta_total")
    st.plotly_chart(fig1, use_container_width=True)

if box_button:
    st.write("Diagrama de caja para meseros, de sus ventas por día")
    fig3 = px.box(venta_meseros, x="atendió", y="venta_total")
    st.plotly_chart(fig3)

if scatter_button:
    st.write("Diagrama de dispersión para los meseros")
    fig2 = px.scatter(venta_ordenes, x="orden", y="precio")
    st.plotly_chart(fig2, use_container_width=True)

if bar_button:
    st.write(
        "Grafica de barras para ver las propinas promedios que reciben los meseros")
    fig8 = px.bar(propinas, x="atendió", y="propina",
                  color=propinas["tipo_de_cliente"])
    st.plotly_chart(fig8, use_container_width=True)


st.header(
    "Ahora vamos a evaluar cuales son las categorias, alimentos y más que se venden")

categorias = df_rest.groupby(["categoria", "tipo_x", "tipo_y", "atendió"])[
    "tipo_de_cliente"].size().reset_index()

meseros = df_rest["atendió"].unique()

fig5 = px.bar(categorias, x="categoria", y="tipo_de_cliente",
              title="Categorias más vendidas")
st.plotly_chart(fig5, use_container_width=True)

meseros_categoria = df_rest.groupby(["atendió", "categoria"])[
    "tipo_de_cliente"].size().reset_index()


fig6 = px.bar(meseros_categoria, x="atendió", y="tipo_de_cliente",
              color=meseros_categoria["categoria"])
st.plotly_chart(fig6)

venta_categorias = df_rest.groupby([
    "categoria", "tipo_de_cliente"])["venta_total"].sum().reset_index().sort_values(by="venta_total", ascending=False)

fig7 = px.funnel(venta_categorias, x="venta_total",
                 y="categoria", color=venta_categorias["tipo_de_cliente"])
st.plotly_chart(fig7)

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
