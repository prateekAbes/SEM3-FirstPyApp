
import pandas as pd
import plotly.express as px

from dash import Dash, dcc, html, Input, Output

# ---------------------------------------------------------
# 1. LOAD DATASET
# ---------------------------------------------------------

url = "https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Other/Monterrey/airbnb.csv"

df = pd.read_csv(url)

print("Dataset loaded successfully")
print("Shape:", df.shape)
print("Columns:", df.columns.tolist())


# ---------------------------------------------------------
# 2. DATA CLEANING
# ---------------------------------------------------------

required_columns = [
    'latitude',
    'longitude',
    'price',
    'minimum_nights'
]

missing = [c for c in required_columns if c not in df.columns]

if missing:
    raise ValueError(f"Missing columns in dataset: {missing}")

for col in required_columns:

    if col == 'price':
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(
                r'[^\d.]', '', regex=True
            ),
            errors='coerce'
        )

    else:
        df[col] = pd.to_numeric(
            df[col],
            errors='coerce'
        )

# Remove missing values

df = df.dropna(subset=required_columns)

# Remove invalid geographic coordinates

df = df[
    df['latitude'].between(-90, 90) &
    df['longitude'].between(-100, 100)
]

print("Clean dataset:", df.shape)
print(df.head())

if df.empty:
    raise ValueError("No valid records found in dataset.")


# ---------------------------------------------------------
# 3. CREATE DASH APPLICATION
# ---------------------------------------------------------

dash_app = Dash(__name__)


# ---------------------------------------------------------
# 4. APP LAYOUT
# ---------------------------------------------------------

dash_app.layout = html.Div([

    html.H1(
        "Airbnb Listings - Monterrey",
        style={
            'textAlign': 'center',
            'color': '#333'
        }
    ),

    html.H3("Filter by Minimum Nights"),

    dcc.Slider(
        id='night-slider',
        min=1,
        max=30,
        step=1,
        value=3,
        marks={
            i: str(i)
            for i in range(1, 31, 5)
        },
        tooltip={
            'placement': 'bottom',
            'always_visible': True
        }
    ),

    html.Br(),

    html.Div(
        id='count',
        style={
            'textAlign': 'center',
            'fontSize': '20px',
            'fontWeight': 'bold'
        }
    ),

    html.Br(),

    dcc.Graph(
        id='airbnb-app',
        style={'height': '700px'}
    )

])


# ---------------------------------------------------------
# 5. CALLBACK FUNCTION
# ---------------------------------------------------------

@dash_app.callback(
    [
        Output('airbnb-app', 'figure'),
        Output('count', 'children')
    ],
    Input('night-slider', 'value')
)
def update_graph(selected_nights):

    filtered_df = df[
        df['minimum_nights'] <= selected_nights
    ]

    count = len(filtered_df)

    fig = px.scatter_map(
        filtered_df,
        lat='latitude',
        lon='longitude',
        color='price',
        size='price',
        hover_data=[
            'price',
            'minimum_nights'
        ],
        color_continuous_scale='Viridis',
        zoom=11,
        height=700,
        title=f'Airbnb Listings - Minimum Nights <= {selected_nights}',
        map_style='open-street-map'
    )

    fig.update_layout(
        margin={
            'r': 0,
            't': 50,
            'l': 0,
            'b': 0
        }
    )

    return fig, f"Total Listings: {count}"


# ---------------------------------------------------------
# 6. VERCEL WSGI ENTRY POINT
# ---------------------------------------------------------
# Vercel WSGI entry point
app = dash_app.server

# Local execution only
if __name__ == "__main__":
    dash_app.run(debug=True)
