import streamlit as st
import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


# ----------------------------------------------------------------------
# 1. Application Configuration
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Global and Regional Obesity Interactive Visualization",
    layout="wide")

# ----------------------------------------------------------------------
# Abstract Section
# ----------------------------------------------------------------------
st.title("Global and Regional Obesity Trends in Adults (18+ years) - WHO Data")
st.markdown(
    """
    ### Abstract
    This dashboard provides an interactive exploration of global and regional trends in adult obesity prevalence (18+ years) using data from the World Health Organization (WHO). Designed for policymakers, international organizations (e.g., WHO, UNICEF, FAO), health ministries, NGOs, and researchers, the dashboard aims to facilitate data-driven decision-making by identifying high-risk areas and analyzing gender and geographical disparities.

    Key features include:

    **Dynamic Map Visualization**: Filter and highlight countries based on obesity rates to focus on specific regions or trends.

    **Extreme Cases Analysis**: Spotlight countries with the highest and lowest obesity rates to identify outliers and prioritize intervention areas.

    **Comparative Trends**: Analyze temporal trends at global, regional, and country levels to track changes over time.

    This tool empowers stakeholders to create actionable strategies to combat obesity and promote public health initiatives worldwide.
        """
)

st.sidebar.header("Interactive Data Filters")

# ----------------------------------------------------------------------
# 2. Data Loading
# ----------------------------------------------------------------------

@st.cache_data
def load_data():
    """
    Load the necessary data for the application:
      - Obesity data (CSV)
      - Shapefile (world map) using an integrated geopandas dataset.
    """
    # Load obesity dataset
    obesity_data = pd.read_csv("BEFA58B_ALL_LATEST.csv")  # Adjust the filename to your actual CSV file
    # Load shapefile for the world map
    file_path = "ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp"
    world = gpd.read_file(file_path)
    
    return obesity_data, world

data, world = load_data()

# ----------------------------------------------------------------------
# 3. Column Adjustments for Merging
# ----------------------------------------------------------------------
if "GEO_NAME_SHORT" in data.columns:
    data.rename(columns={"GEO_NAME_SHORT": "NAME"}, inplace=True)

# Name corrections for merging datasets
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
    'Tokelau': 'Tokelau',  # No change needed
    'T³rkiye': 'Turkey',
    'United Kingdom of Great Britain and Northern Ireland': 'United Kingdom',
    'United Republic of Tanzania': 'Tanzania',
    'Venezuela (Bolivarian Republic of)': 'Venezuela',
    'Viet Nam': 'Vietnam',
    'occupied Palestinian territory, including east Jerusalem': 'Palestine'
}

data["NAME"] = data["NAME"].replace(name_corrections)

# ----------------------------------------------------------------------
# 4. Merge World Map Data with Obesity Data
# ----------------------------------------------------------------------
world = world.merge(data, on="NAME", how="inner", suffixes=(None, "_drop"))
world = GeoDataFrame(world, geometry="geometry", crs=world.crs)

# ----------------------------------------------------------------------
# 5. Sidebar Graph Selection
# ----------------------------------------------------------------------
option = st.sidebar.radio(
    "Select the graph you want to visualize:",
    ("Global Obesity Visualization", "Obesity Trends Over Time")
)
# Default values
selected_year = 2022
selected_continent = "World"

# Show filters only when "World Map" is selected
if option == "Global Obesity Visualization":
    # Year selection (DIM_TIME)
    available_years = sorted(world["DIM_TIME"].dropna().unique().astype(int))
    selected_year = st.sidebar.selectbox("Select a year:", available_years, index=available_years.index(2022))
    
    # Filter available continents
    available_continents = ['World'] + sorted(world["CONTINENT"].dropna().unique())
    selected_continent = st.sidebar.selectbox("Select a geographical area:", available_continents)

# Filter data by continent if "World" is not selected
filtered_data = world.copy()
if selected_continent != 'World' and option == "Global Obesity Visualization":
    filtered_data = filtered_data[filtered_data["CONTINENT"] == selected_continent]

# Filter data by selected year
if option == "Global Obesity Visualization":
    filtered_data = filtered_data[filtered_data["DIM_TIME"] == selected_year]

# ----------------------------------------------------------------------
# 6. World Map with Year Filter
# ----------------------------------------------------------------------

continent_ranges = {
    "World": {"lon": [-180, 180], "lat": [-90, 90]},  # Entire world
    "Europe": {"lon": [-30, 50], "lat": [30, 75]},
    "Asia": {"lon": [30, 150], "lat": [10, 70]},
    "Africa": {"lon": [-20, 55], "lat": [-35, 37]},
    "North America": {"lon": [-170, -50], "lat": [5, 80]},
    "South America": {"lon": [-85, -30], "lat": [-60, 15]},
    "Oceania": {"lon": [110, 180], "lat": [-50, 0]},
    "Seven seas (open ocean)": {"lon": [-180, 180], "lat": [-90, 90]}
}

# Get longitude and latitude ranges for the selected continent
lon_range = continent_ranges[selected_continent]["lon"]
lat_range = continent_ranges[selected_continent]["lat"]

if option == "Global Obesity Visualization":
    st.header(f"Global Obesity Visualization ({selected_year})")

    # Calcular promedios y estadísticas
    avg_obesity_rate = filtered_data["RATE_PER_100_N"].mean()
    avg_obesity_by_gender = filtered_data.groupby("DIM_SEX")["RATE_PER_100_N"].mean()
    male_avg = avg_obesity_by_gender.get("MALE", float("nan"))
    female_avg = avg_obesity_by_gender.get("FEMALE", float("nan"))

    # Identify countries with high and low rates
    max_obesity = filtered_data.loc[filtered_data["RATE_PER_100_N"].idxmax()]
    min_obesity = filtered_data.loc[filtered_data["RATE_PER_100_N"].idxmin()]
    
    # Add a slider for selecting the range of obesity rates
    min_rate, max_rate = filtered_data["RATE_PER_100_N"].min(), filtered_data["RATE_PER_100_N"].max()
    selected_range = st.sidebar.slider(
        "Select Obesity Rate Range displayed on the map:",
        0,
        100,
        (0,100)
    )

    # Filter the data based on the selected range
    filtered_data_range = filtered_data[
        (filtered_data["RATE_PER_100_N"] >= selected_range[0]) &
        (filtered_data["RATE_PER_100_N"] <= selected_range[1])
    ]

    col1, col2 = st.columns([3, 1])

    with col1:
        fig = px.choropleth(
            filtered_data_range,
            geojson=filtered_data_range.geometry,
            locations=filtered_data_range.index,
            color="RATE_PER_100_N",
            hover_name="NAME",
            hover_data={"RATE_PER_100_N": True, "DIM_TIME": False},
            title=f"{selected_continent}",
            color_continuous_scale=px.colors.sequential.Sunset,  
            labels={"RATE_PER_100_N": "Obesity Rate (%)"},
        )

        # Map
        fig.update_geos(
            projection_type="natural earth",
            showcountries=True,
            countrycolor="#D6D6D6",  # Country boundaries
            showocean=True,
            oceancolor="#EAF6FF", 
            visible=True,
            lonaxis_range=lon_range,
            lataxis_range=lat_range,
            resolution=50,
        )

        # Design and legend
        fig.update_layout(
            autosize=True,
            title={
                "text": f"{selected_continent}",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 20, "color": "#333"},  
            },
            coloraxis_colorbar={
                "title": "<b>Obesity Rate (%)</b>",
                "len": 0.75,  
                "yanchor": "middle",
                "y": 0.5,
                "thickness": 15,
                "x": 1.02,  
                "tickfont": {"size": 12, "color": "#333"},  
                "titlefont": {"size": 14, "color": "#333"},
            },
            margin={"r": 10, "t": 30, "l": 10, "b": 10},
        )

        # Show in Streamlit
        st.plotly_chart(fig, use_container_width=True)


    with col2:
        st.markdown(
            f"""
            <style>
                .stats-container {{
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    height: 100%;
                    text-align: center;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    padding: 20px;
                    background-color: #f9f9f9;
                    box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
                }}
                .stats-container h2 {{
                    font-size: 48px;
                    color: #333;
                    margin-bottom: 10px;
                }}
                .stats-container p {{
                    font-size: 16px;
                    color: #666;
                    margin: 5px 0;
                }}
                .stats-container .highlight {{
                    font-size: 18px;
                    color: #444;
                    font-weight: bold;
                }}
            </style>
            <div class="stats-container">
                <h2>{avg_obesity_rate:.2f}%</h2>
                <p class="highlight">Average Obesity Rate</p>
                <p>Male: <span class="highlight">{male_avg:.2f}%</span></p>
                <p>Female: <span class="highlight">{female_avg:.2f}%</span></p>
            </div>
            """,
            unsafe_allow_html=True,
        )


    # Chart 1: Stacked Bars by Subregion
    st.subheader("Exploring Obesity Trends in Subregions")
    if "SUBREGION" in filtered_data.columns:
        subregion_data = (
            filtered_data.groupby(["SUBREGION", "DIM_SEX"])["RATE_PER_100_N"]
            .mean()
            .reset_index()
        )

        # Sort subregions by average obesity rate (average of both genders)
        subregion_order = (
            subregion_data.groupby("SUBREGION")["RATE_PER_100_N"].mean()
            .sort_values(ascending=False)
            .index
        )
        subregion_data["SUBREGION"] = pd.Categorical(
            subregion_data["SUBREGION"], categories=subregion_order, ordered=True
        )
        subregion_data_gender = subregion_data[subregion_data["DIM_SEX"].isin(["MALE", "FEMALE"])]

        # Ensure Plotly respects the categorical order
        fig1 = px.bar(
            subregion_data_gender,
            x="SUBREGION",
            y="RATE_PER_100_N",
            color="DIM_SEX",
            barmode="stack",
            labels={"RATE_PER_100_N": "Obesity Rate (%)", "SUBREGION": "Subregion"},
            color_discrete_sequence=["#FF9999", "#9999FF"],  # Different colors for genders
            title=f"Subregion-Level Gender Analysis of Obesity in {selected_continent}",
            category_orders={"SUBREGION": list(subregion_order)},  # Respect categorical order
        )

        fig1.update_layout(
            xaxis_title="Subregion",
            yaxis_title="Obesity Rate (%)",
            legend_title="Gender",
            margin={"t": 50, "l": 50, "r": 50, "b": 50},
            width=800,
            height=500,
        )

        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning("No subregion data found for this continent.")


    # Chart 2: Extreme Countries
    st.subheader("Countries with Highest and Lowest Obesity Rates")

    # Explanation for the chart
    st.markdown(f"""
        This bar chart highlights the five countries with the highest and lowest obesity rates in {selected_continent}.
        Data is categorized by gender to emphasize disparities.
    """)

    # Group by country and calculate the average rate for males and females
    country_avg_data = (
        filtered_data.groupby("NAME")["RATE_PER_100_N"]
        .mean()
        .reset_index()
        .sort_values("RATE_PER_100_N", ascending=False)
    )
    # Select the 5 countries with the highest and lowest rates
    top_countries = country_avg_data.nlargest(5, "RATE_PER_100_N")
    bottom_countries = country_avg_data.nsmallest(5, "RATE_PER_100_N")
    extreme_countries = pd.concat([top_countries, bottom_countries])

    # Filter the original data to include only these countries
    extreme_gender_data = filtered_data[filtered_data["NAME"].isin(extreme_countries["NAME"])]

    # Filter only males and females
    extreme_gender_data = extreme_gender_data[extreme_gender_data["DIM_SEX"].isin(["MALE", "FEMALE"])]
    extreme_gender_data = extreme_gender_data[["NAME", "DIM_SEX", "RATE_PER_100_N"]]

    # Create a new column to differentiate between "Top 5" and "Bottom 5"
    extreme_gender_data["Category"] = extreme_gender_data["NAME"].apply(
        lambda x: "Top 5" if x in top_countries["NAME"].values else "Bottom 5"
    )

    # Sort data to ensure "Top 5" appear first and within each group sort by obesity rate
    extreme_gender_data = extreme_gender_data.sort_values("RATE_PER_100_N", ascending=False).reset_index(drop=True)


    # Calculate the average obesity rate (Male and Female) for each country
    extreme_gender_data["Average Rate"] = (
        extreme_gender_data.groupby("NAME")["RATE_PER_100_N"].transform("mean")
    )

    # Create the chart with improved aesthetics and additional hover data
    fig2 = px.bar(
        extreme_gender_data,
        x="RATE_PER_100_N",
        y="NAME",
        color="DIM_SEX",  # Color by gender
        pattern_shape="Category",  # Differentiate by Top 5/Bottom 5
        orientation="h",
        labels={
            "RATE_PER_100_N": "Obesity Rate (%)",
            "NAME": "Country",
            "DIM_SEX": "Gender",
            "Category": "Group",
            "Average Rate": "Average Obesity Rate",
        },
        hover_data={
            "Average Rate": ":.2f",  # Show the average obesity rate with two decimal places
            "RATE_PER_100_N": ":.2f",  # Show the individual rate for each gender
            "DIM_SEX": True,  # Show gender
            "Category": True,  # Show whether it is Top 5 or Bottom 5
        },
        title=f"Top 5 and Bottom 5 Countries by Obesity Prevalence from {selected_continent}",
        color_discrete_map={
            "MALE": "#FF9999",  # Pink for Male
            "FEMALE": "#9999FF",  # Blue for Female
        },
        pattern_shape_map={
            "Highest Obesity Rates": "/",  # Slashes for Top 5
            "Bottom 5": "",  # No pattern for Bottom 5
        },
    )

    # Layout for fig2
    fig2.update_layout(
        xaxis_title="Obesity Rate (%)",
        yaxis_title="Country",
        legend_title="Gender",
        margin={"t": 50, "l": 50, "r": 50, "b": 50},  # Same margins
        width=800,  # Same width
        height=500,  # Same height
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,  # Align legend to the right
        ),
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig2, use_container_width=True)



# ----------------------------------------------------------------------
# 7. Trends Graphs
# ----------------------------------------------------------------------
elif option == "Obesity Trends Over Time":
    st.header("Obesity Prevalence Trends")

    # Add an introductory description
    st.markdown(
        """
        This section visualizes the obesity prevalence trends over time, categorized by regions, countries, or continents.
        Data source: World Health Organization (WHO), Open Data Repository.
        """
    )

    # Selector for grouping level
    view_option = st.sidebar.radio(
        "Show trends by:",
        ("Regions", "Countries", "Continents")
    )

    # Dynamic selection of grouping level based on the chosen option
    if view_option == "Regions":
        group_by_column = "SUBREGION"
        group_title = "Region/Subregion"
    elif view_option == "Continents":
        group_by_column = "CONTINENT"
        group_title = "Continent"
    else:
        group_by_column = "NAME"
        group_title = "Country"

    # Selection of available categories for the grouping level
    available_groups = sorted(world[group_by_column].dropna().unique())
    selected_groups = st.multiselect(f"Select {group_title.lower()}:", available_groups)

    # Button to include/exclude the global trend
    include_global_trend = st.sidebar.checkbox("Include global trend", value=False)

    if not selected_groups:
        st.warning(f"Select at least one {group_title.lower()} to display trends.")
    else:
        # Filter data by the selected grouping level (region, country, or continent)
        filtered_data = world[world[group_by_column].isin(selected_groups)]

        # Calculate global obesity trend (optional)
        global_trend = (
            world.groupby("DIM_TIME")["RATE_PER_100_N"]
            .mean()
            .reset_index()
            .rename(columns={"RATE_PER_100_N": "Global Average"})
        )

        # Check for required columns
        if "DIM_TIME" in filtered_data.columns and "RATE_PER_100_N" in filtered_data.columns:
            # Group data by the selected level and year
            trend_data = (
                filtered_data.groupby([group_by_column, "DIM_TIME"])["RATE_PER_100_N"]
                .mean()
                .reset_index()
            )
            # Determine if only one category is selected
            if len(selected_groups) == 1:
                line_color = ["#FF5733"]  # Streamlit's orange for a single line
                markers = False  # Disable markers for single-line aesthetics
            else:
                line_color = px.colors.qualitative.Set2
                markers = False

            # Create the plot using Plotly
            fig = px.line(
                trend_data,
                x="DIM_TIME",
                y="RATE_PER_100_N",
                color=group_by_column,
                labels={
                    "DIM_TIME": "Year",
                    "RATE_PER_100_N": "Obesity Rate (%)",
                    group_by_column: group_title,
                },
                title=f"Obesity Prevalence Trends by {group_title}",
                markers=markers,
                color_discrete_sequence=line_color,
            )

            # Add the global trend if selected
            if include_global_trend:
                # Smoothing the global trend for better interpretation
                fig.add_scatter(
                    x=global_trend["DIM_TIME"],
                    y=global_trend['Global Average'],
                    mode="lines",
                    name="Global Trend Average",
                    line=dict(color="black"),
                )

            # Customize the layout
            fig.update_layout(
                xaxis_title="Year",
                yaxis_title="Obesity Rate (%)",
                legend_title=group_title,
                margin={"t": 50, "l": 50, "r": 50, "b": 50},
                width=900,
                height=600,
                legend=dict(
                    orientation="v",  # Vertical alignment
                    yanchor="top",
                    y=1.0,
                    xanchor="left",
                    x=1.02,
                ),
            )

            # Display the graph in Streamlit
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("The required columns for creating the graph were not found.")


# ----------------------------------------------------------------------
# Footer with Data Source
# ----------------------------------------------------------------------
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: white;
        text-align: center;
        padding: 10px 0;
        font-size: 14px;
        color: gray;
        box-shadow: 0px -2px 5px rgba(0, 0, 0, 0.1);
        z-index: 1000;
    }
    </style>
    <div class="footer">
        Data source: <a href="https://www.who.int/" target="_blank" style="color: blue;">World Health Organization (WHO)</a>, Open Data Repository.<br>
        This dashboard was created as part of an academic project to analyze global and regional trends in adult obesity prevalence.
    </div>
    """,
    unsafe_allow_html=True
)