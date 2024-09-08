from dash import dcc, html

from .utils import (
    create_clock_and_date,
    create_investment_prediction_section,
    create_period_buttons,
)


def create_layout() -> html.Div:
    """
    Create the layout for the Dash app.

    :return: html.Div, the layout of the Dash app
    """
    return html.Div(
        style={"backgroundColor": "#1e1e1e", "color": "#ffffff"},
        children=[
            html.H1("Stock Dashboard", style={"textAlign": "center"}),
            dcc.Markdown(
                """
                This dashboard provides real-time data and visualizations for the S&P 500 index.  
                You can view stock performance over various time periods and predict future investment values.
                """,
                style={
                    "textAlign": "center",
                    "margin": "20px auto",
                    "maxWidth": "800px",
                },
            ),
            create_clock_and_date(),
            html.H2("S&P 500 History", style={"textAlign": "center"}),
            dcc.Graph(id="stock-graph"),
            create_period_buttons(),
            create_investment_prediction_section(),
        ],
    )
