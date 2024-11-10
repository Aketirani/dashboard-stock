from dash import dcc, html

from src.utils import Utils


class Layout:
    """
    A class to create the layout for the Dash app
    """

    @staticmethod
    def create_layout() -> html.Div:
        """
        Create the layout for the Dash app

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
                Utils.create_clock_and_date(),
                html.H2("Index History", style={"textAlign": "center"}),
                dcc.Graph(id="stock-graph"),
                Utils.create_period_buttons(),
                html.H2("Yearly Returns", style={"textAlign": "center"}),
                dcc.Graph(id="yearly-returns-graph"),
                Utils.create_investment_prediction_section(),
            ],
        )
