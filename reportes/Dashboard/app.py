import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import json
from tensorflow.keras.models import load_model

# Cargar los datos y el GeoJSON
dataIcfes = pd.read_csv('clean_saber11.csv')  # Asegúrate de que este archivo contiene datos válidos
with open("HuilaCompleto.geojson", "r") as f:
    huila_geojson = json.load(f)

# Asegúrate de que los nombres de municipios coincidan entre dataIcfes y huila_geojson
dataIcfes["cole_mcpio_ubicacion"] = dataIcfes["cole_mcpio_ubicacion"].str.upper()

# Extraer el año de la columna 'periodo'
dataIcfes["anio"] = dataIcfes["periodo"].astype(str).str[:4]  # Toma solo los primeros 4 dígitos

# Diccionario para mapear columnas a nombres amigables
score_columns_mapping = {
    "punt_ingles": "Puntaje Inglés",
    "punt_matematicas": "Puntaje Matemáticas",
    "punt_sociales_ciudadanas": "Puntaje Sociales Ciudadanas",
    "punt_c_naturales": "Puntaje Ciencias Naturales",
    "punt_lectura_critica": "Puntaje Lectura Crítica",
    "punt_global": "Puntaje Global",
}

# Opciones para seleccionar el puntaje
score_options = [
    {"label": label, "value": column} for column, label in score_columns_mapping.items()
]

# Cargar el modelo
modelo = load_model("my_model.keras")

# Crear la aplicación
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Crear un gráfico Choropleth con Plotly
def create_choropleth(selected_column):
    fig = px.choropleth_mapbox(
        dataIcfes,
        geojson=huila_geojson,
        locations="cole_mcpio_ubicacion",  # Columna de municipios en el dataset
        featureidkey="properties.nombre_mpi",  # Clave de los municipios en el GeoJSON
        color=selected_column,
        color_continuous_scale="Viridis",
        range_color=(dataIcfes[selected_column].min(), dataIcfes[selected_column].max()),
        mapbox_style="carto-positron",
        zoom=7,
        center={"lat": 2.5, "lon": -75.5},
        opacity=0.7,
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig

# Callback para actualizar el mapa y las estadísticas
@app.callback(
    [
        Output("map_graph", "figure"),
        Output("minimo-municipio", "children"),
        Output("minimo-puntaje", "children"),
        Output("maximo-municipio", "children"),
        Output("maximo-puntaje", "children"),
        Output("media-puntaje", "children"),
        Output("desviacion-puntaje", "children"),
    ],
    [Input("score_selector", "value")],
)
def update_map(selected_column):
    fig = create_choropleth(selected_column)
    min_row = dataIcfes.loc[dataIcfes[selected_column].idxmin()]
    max_row = dataIcfes.loc[dataIcfes[selected_column].idxmax()]
    mean = dataIcfes[selected_column].mean()
    std = dataIcfes[selected_column].std()
    return (
        fig,
        f"Municipio: {min_row['cole_mcpio_ubicacion']}",
        f"Puntaje: {min_row[selected_column]:.2f}",
        f"Municipio: {max_row['cole_mcpio_ubicacion']}",
        f"Puntaje: {max_row[selected_column]:.2f}",
        f"Media: {mean:.2f}",
        f"Desviación estándar: {std:.2f}",
    )

# Callback para actualizar el gráfico de evolución por colegio
@app.callback(
    [
        Output("grafico-evolucion", "figure"),
        Output("info-colegio", "children"),
    ],
    [Input("colegio-dropdown", "value")],
)
def update_evolucion(colegio_seleccionado):
    datos_filtrados = dataIcfes[dataIcfes["cole_nombre_establecimiento"] == colegio_seleccionado]
    promedio_anual = datos_filtrados.groupby("anio")["punt_global"].mean().reset_index()
    fig = px.line(
        promedio_anual,
        x="anio",
        y="punt_global",
        title=f"Promedio del Puntaje Global por Año - {colegio_seleccionado}",
        labels={"anio": "Año", "punt_global": "Promedio del Puntaje Global"},
    )
    municipio = datos_filtrados["cole_mcpio_ubicacion"].iloc[0]
    info = f"Municipio: {municipio}"
    return fig, info

@app.callback(
    Output("grafico-correlacion", "figure"),
    [Input("anio-dropdown", "value")],
)
def update_correlacion(anio_seleccionado):
    # Filtrar los datos por el año seleccionado
    datos_filtrados = dataIcfes[dataIcfes["anio"] == anio_seleccionado]
    
    # Calcular el promedio del puntaje global por estrato
    promedio_por_estrato = (
        datos_filtrados.groupby("fami_estratovivienda")["punt_global"]
        .mean()
        .reset_index()
    )
    
    # Crear el gráfico de barras
    fig = px.bar(
        promedio_por_estrato,
        x="fami_estratovivienda",
        y="punt_global",
        title=f"Promedio del Puntaje Global por Estrato - Año {anio_seleccionado}",
        labels={"fami_estratovivienda": "Estrato Económico", "punt_global": "Promedio del Puntaje Global"},
    )
    fig.update_layout(title_x=0.5)  # Centrar el título
    return fig

# Layout de la aplicación
app.layout = html.Div(
    [
        # Encabezado
        dbc.Row(
            [
                dbc.Col(
                    html.Img(
                        src="/assets/logo.jpg",
                        style={"height": "100px", "width": "auto"},
                    ),
                    width=2,
                ),
                dbc.Col(
                    [
                        html.H1(
                            "Estadísticas del ICFES",
                            style={"font-weight": "bold"},
                        ),
                        html.H5(
                            "Análisis de puntajes del ICFES en los municipios del departamento del Huila",
                            style={"font-style": "italic"},
                        ),
                    ],
                    width=10,
                ),
            ],
            align="center",
            className="mb-4",
        ),
        # Fila principal
        dbc.Row(
            [
                # Contenedor izquierda
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5(
                                    "Seleccione una materia:",
                                    className="card-title",
                                ),
                                dcc.RadioItems(
                                    id="score_selector",
                                    options=score_options,
                                    value="punt_global",
                                    labelStyle={"display": "block", "text-align": "left"},
                                ),
                            ]
                        ),
                        style={
                            "box-shadow": "0px 4px 6px rgba(0,0,0,0.1)",
                            "border-radius": "10px",
                        },
                    ),
                    width=4,
                ),
                # Contenedores de estadísticas (Mínimo, Máximo, Media)
                dbc.Col(
                    [
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Mínimo", className="card-title"),
                                    html.P(id="minimo-municipio", className="card-text"),
                                    html.P(id="minimo-puntaje", className="card-text"),
                                ]
                            ),
                            style={
                                "box-shadow": "0px 4px 6px rgba(0,0,0,0.1)",
                                "border-radius": "10px",
                            },
                        ),
                    ],
                    width=2,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Máximo", className="card-title"),
                                    html.P(id="maximo-municipio", className="card-text"),
                                    html.P(id="maximo-puntaje", className="card-text"),
                                ]
                            ),
                            style={
                                "box-shadow": "0px 4px 6px rgba(0,0,0,0.1)",
                                "border-radius": "10px",
                            },
                        ),
                    ],
                    width=2,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Media y Desviación", className="card-title"),
                                    html.P(id="media-puntaje", className="card-text"),
                                    html.P(id="desviacion-puntaje", className="card-text"),
                                ]
                            ),
                            style={
                                "box-shadow": "0px 4px 6px rgba(0,0,0,0.1)",
                                "border-radius": "10px",
                            },
                        ),
                    ],
                    width=2,
                ),
            ],
            className="mb-4",
        ),
        # Mapa del Huila con choropleth
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                id="map_graph",
                                config={"displayModeBar": False},
                                style={"height": "500px"},
                            )
                        ),
                        style={
                            "box-shadow": "0px 4px 6px rgba(0,0,0,0.1)",
                            "border-radius": "10px",
                        },
                    ),
                    width=12,
                ),
            ]
        ),
        # Gráfico de evolución del puntaje promedio por colegio
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Seleccione un Colegio:", className="card-title"),
                                dcc.Dropdown(
                                    id="colegio-dropdown",
                                    options=[{"label": colegio, "value": colegio} for colegio in dataIcfes["cole_nombre_establecimiento"].unique()],
                                    value=dataIcfes["cole_nombre_establecimiento"].iloc[0],
                                    placeholder="Seleccione un colegio",
                                ),
                                dcc.Graph(
                                    id="grafico-evolucion",
                                    config={"displayModeBar": False},
                                    style={"height": "400px"},
                                ),
                                html.Div(id="info-colegio", style={"marginTop": "10px"}),
                            ]
                        ),
                        style={
                            "box-shadow": "0px 4px 6px rgba(0,0,0,0.1)",
                            "border-radius": "10px",
                        },
                    ),
                    width=12,
                )
            ]
        ),
        # Gráfico de correlación entre puntaje global y estrato económico
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Seleccione el Año para el Gráfico de Relación Estrato vs Puntaje Global Promedio:", className="card-title"),
                                dcc.Dropdown(
                                    id="anio-dropdown",
                                    options=[{"label": str(anio), "value": str(anio)} for anio in sorted(dataIcfes["anio"].unique())],
                                    value=str(dataIcfes["anio"].iloc[0]),
                                    placeholder="Seleccione un año",
                                ),
                                dcc.Graph(
                                    id="grafico-correlacion",
                                    config={"displayModeBar": False},
                                    style={"height": "400px"},
                                ),
                            ]
                        ),
                        style={
                            "box-shadow": "0px 4px 6px rgba(0,0,0,0.1)",
                            "border-radius": "10px",
                        },
                    ),
                    width=12,
                )
            ]
        ),
    ],
    style={"padding": "20px"},
)

if __name__ == "__main__":
    app.run_server(debug=True)