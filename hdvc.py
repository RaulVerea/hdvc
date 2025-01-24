import streamlit as st
import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt
import seaborn as sns
# ----------------------------------------------------------------------
# 1. Configuración de la Aplicación
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Visualización de la Prevalencia de Obesidad",
    layout="wide"
)
st.title("Visualización Interactiva: Prevalencia de Obesidad Mundial y Regional")
st.sidebar.header("Filtros de Visualización")
# ----------------------------------------------------------------------
# 2. Carga de datos
# ----------------------------------------------------------------------
# Si no vas a usar el archivo Excel "data.xlsx", puedes comentarlo o quitarlo.
# file_path = 'data.xlsx'
# excel_data = pd.ExcelFile(file_path)
# df = pd.read_excel(excel_data, sheet_name='Sheet1')

@st.cache_data
def load_data():
    """
    Carga los datos necesarios para la aplicación:
      - Datos de obesidad (CSV)
      - Shapefile (mapa mundial) usando un dataset integrado de geopandas.
    """
    # Cargar dataset de obesidad
    obesity_data = pd.read_csv("BEFA58B_ALL_LATEST.csv")  # Ajusta el nombre a tu archivo CSV real
    # Cargar shapefile del mapa mundial
    file_path = "ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp"
    world = gpd.read_file(file_path)
    europe_countries = world[world['CONTINENT'] == 'Europe']
    
    return obesity_data, europe_countries

# ----------------------------------------------------------------------
# Cargar datos
# ----------------------------------------------------------------------
data, world = load_data()



# 3. Ajuste de columnas (si fuese necesario) para hacer el merge
#    Asegúrate de que 'GEO_NAME_SHORT' sea la columna que corresponde
#    a los nombres de país en tu dataset.
#    Si tu dataset ya está en la columna 'name', puedes omitir el rename.
# ----------------------------------------------------------------------
if "GEO_NAME_SHORT" in data.columns:
    data.rename(columns={"GEO_NAME_SHORT": "NAME"}, inplace=True)

# Corrección de nombres para unir datos
name_corrections = {
    'Antigua and Barbuda': 'Antigua and Barb.',
    'Bolivia (Plurinational State of)': 'Bolivia',
    'Bosnia and Herzegovina': 'Bosnia and Herz.',
    # Agrega todas las equivalencias necesarias
}

data["NAME"] = data["NAME"].replace(name_corrections)
# ----------------------------------------------------------------------
# 4. Unir datos del mapa con los datos de obesidad
# ----------------------------------------------------------------------
world = world.merge(data, on="NAME", how="inner", suffixes=(None, "_drop"))
world = GeoDataFrame(world, geometry="geometry", crs=world.crs)
# Selección del año (DIM_TIME)
available_years = sorted(world["DIM_TIME"].dropna().unique())
selected_year = st.sidebar.selectbox("Selecciona un año:", available_years)

# Filtrar los datos por el año seleccionado
filtered_data = world[world["DIM_TIME"] == selected_year]
filtered_data = filtered_data.set_geometry("geometry", crs=world.crs)  # Asegurar geometría tras el filtrado

# Eliminar la columna 'NAME' duplicada de world_merged
#world.drop(columns=["NAME"], inplace=True)
# ----------------------------------------------------------------------
# 5. Selección del gráfico en la barra lateral
# ----------------------------------------------------------------------
option = st.sidebar.radio(
    "Selecciona el gráfico que deseas visualizar:",
    ("Mapa Mundial", "Gráficas de Tendencias")
)

# ----------------------------------------------------------------------
# 6. Mapa Mundial con filtro por año
# ----------------------------------------------------------------------
# Mapa Mundial: Prevalencia de Obesidad por País
if option == "Mapa Mundial":
    st.header("Mapa Mundial: Prevalencia de Obesidad por País")


    # Pintar los países con la tasa de obesidad
    # Crear la figura y los ejes
    fig, ax = plt.subplots(figsize=(15, 10))

    # Dibujar los bordes de los países
    #world.boundary.plot(ax=ax, linewidth=0.5, color='black')

    # Pintar los países con la tasa de obesidad
    filtered_data.plot(
        column="RATE_PER_100_N",
        ax=ax,
        cmap="RdYlGn_r",  # Escala de colores intuitiva: verde a rojo
        legend=True,
        missing_kwds={"color": "lightgrey", "label": "Sin datos"},
        legend_kwds={
            'label': "Prevalencia de Obesidad (%)",
            'orientation': "horizontal"
        }
    )

    # Ajustar el zoom al mapa (ejemplo: Europa)
    ax.set_xlim([-30, 50])  # Longitud: de -30° a 50° (aproximadamente Europa)
    ax.set_ylim([30, 75])   # Latitud: de 30° a 75° (aproximadamente Europa)

    # Títulos y formato
    ax.set_title(f"Mapa Mundial: Prevalencia de Obesidad ({selected_year})", fontsize=18)
    ax.set_axis_off()  # Ocultar los ejes

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)


# ----------------------------------------------------------------------
# 7. Gráficas de Tendencias
# ----------------------------------------------------------------------
elif option == "Gráficas de Tendencias":
    st.header("Evolución de la Prevalencia de Obesidad por Región")
        
    # Selección de regiones
    regions = st.multiselect("Selecciona regiones:", world["NAME"].dropna().unique())
    
    if not regions:
        st.warning("Selecciona al menos una región para mostrar las tendencias.")
    else:
        filtered_data = world[world["NAME"].isin(regions)]
        
        # Verificamos la columna 'DIM_TIME' y 'RATE_PER_100_N' para la gráfica
        if "DIM_TIME" in filtered_data.columns and "RATE_PER_100_N" in filtered_data.columns:
            fig, ax = plt.subplots(figsize=(12, 8))
            sns.lineplot(
                data=filtered_data,
                x="DIM_TIME",
                y="RATE_PER_100_N",
                hue="NAME",
                marker="o",
                ax=ax
            )
            ax.set_title("Evolución de la Prevalencia de Obesidad por Región", fontsize=16)
            ax.set_xlabel("Año", fontsize=12)
            ax.set_ylabel("Tasa de Obesidad (%)", fontsize=12)
            plt.legend(title="Región", fontsize=10)
            plt.grid(alpha=0.3)
            st.pyplot(fig)
        else:
            st.warning("No se encontraron las columnas 'DIM_TIME' o 'RATE_PER_100_N' en los datos.")

# Verificar que las columnas necesarias existan (ejemplo: 'GENDER', 'RATE_PER_100_N', 'NAME')
if all(col in filtered_data.columns for col in ["DIM_SEX", "RATE_PER_100_N", "NAME"]):
    # Filtrar solo hombres y mujeres
    gender_data = filtered_data[filtered_data["DIM_SEX"].isin(["MALE", "FEMALE"])]

    # Crear el gráfico de barras agrupadas
    plt.figure(figsize=(15, 8))
    sns.barplot(
        data=gender_data,
        x="NAME",  # País o región
        y="RATE_PER_100_N",  # Tasa de obesidad
        hue="DIM_SEX",  # Agrupación por género
        palette="RdYlGn_r"  # Paleta de colores intuitiva
    )

    # Personalizar el gráfico
    plt.title(f"Tasas de Obesidad por Género ({selected_year})", fontsize=16)
    plt.xlabel("País o Región", fontsize=14)
    plt.ylabel("Prevalencia de Obesidad (%)", fontsize=14)
    plt.xticks(rotation=90, fontsize=10)  # Rotar nombres de países para mayor legibilidad
    plt.legend(title="Género")
    plt.tight_layout()

    # Mostrar el gráfico en Streamlit
    st.pyplot(plt)
else:
    st.warning("Las columnas necesarias ('GENDER', 'RATE_PER_100_N', 'NAME') no están disponibles en el dataset.")


