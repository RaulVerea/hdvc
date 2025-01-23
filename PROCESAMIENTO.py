import pandas as pd
import geopandas as gpd

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

# ----------------------------------------------------------------------
# 3. Ajuste de columnas (si fuese necesario) para hacer el merge
#    Asegúrate de que 'GEO_NAME_SHORT' sea la columna que corresponde
#    a los nombres de país en tu dataset.
#    Si tu dataset ya está en la columna 'name', puedes omitir el rename.
# ----------------------------------------------------------------------
if "GEO_NAME_SHORT" in data.columns:
    data.rename(columns={"GEO_NAME_SHORT": "NAME"}, inplace=True)

name_corrections = {
    'Antigua and Barbuda': 'Antigua and Barb.',
    'Bolivia (Plurinational State of)': 'Bolivia',
    'Bosnia and Herzegovina': 'Bosnia and Herz.',
    'Brunei Darussalam': 'Brunei',
    'Central African Republic': 'Central African Rep.',
    "Democratic People's Republic of Korea": 'North Korea',
    'Democratic Republic of the Congo': 'Dem. Rep. Congo',
    'Dominican Republic': 'Dominican Rep.',
    'Eswatini': 'eSwatini',
    'Iran (Islamic Republic of)': 'Iran',
    "Lao People's Democratic Republic": 'Laos',
    'Marshall Islands': 'Marshall Is.',
    'Micronesia (Federated States of)': 'Micronesia',
    'Netherlands (Kingdom of the)': 'Netherlands',
    'Republic of Korea': 'South Korea',
    'Republic of Moldova': 'Moldova',
    'Russian Federation': 'Russia',
    'Saint Kitts and Nevis': 'St. Kitts and Nevis',
    'Saint Vincent and the Grenadines': 'St. Vin. and Gren.',
    'Sao Tome and Principe': 'SÒo TomÚ and Principe',
    'Solomon Islands': 'Solomon Is.',
    'South Sudan': 'S. Sudan',
    'Syrian Arab Republic': 'Syria',
    'Tokelau': 'Tokelau',  # No cambio necesario
    'T³rkiye': 'Turkey',
    'United Kingdom of Great Britain and Northern Ireland': 'United Kingdom',
    'United Republic of Tanzania': 'Tanzania',
    'Venezuela (Bolivarian Republic of)': 'Venezuela',
    'Viet Nam': 'Vietnam',
    'occupied Palestinian territory, including east Jerusalem': 'Palestine'
}

# Reemplazar nombres en el dataset `data` utilizando las equivalencias
data["NAME"] = data["NAME"].replace(name_corrections)

world = world.merge(data, on="NAME", how="inner")

print(world["NAME"].unique())