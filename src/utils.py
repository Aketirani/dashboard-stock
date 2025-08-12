from datetime import datetime

from dash import dcc, html


class Utils:
    """
    A class containing utility functions for the Dash app
    """

    @staticmethod
    def create_clock_and_date() -> html.Div:
        """
        Create the clock and date display

        :return: html.Div, the clock and date display
        """
        common_style = {
            "color": "#00cc96",
            "fontSize": "30px",
            "backgroundColor": "#1e1e1e",
            "margin": "10px",
            "position": "absolute",
            "padding": "5px 10px",
            "borderRadius": "5px",
        }

        return html.Div(
            [
                html.Div(
                    id="clock",
                    children=datetime.now().strftime("%H:%M:%S"),
                    style={
                        **common_style,
                        "top": "30px",
                        "left": "10px",
                        "textAlign": "left",
                    },
                ),
                html.Div(
                    id="date",
                    children=datetime.now().strftime("%Y-%m-%d"),
                    style={
                        **common_style,
                        "top": "30px",
                        "right": "10px",
                        "textAlign": "right",
                    },
                ),
            ]
        )

    @staticmethod
    def create_period_buttons() -> html.Div:
        """
        Create buttons for selecting different time periods for stock data

        :return: html.Div, the period selection buttons
        """
        button_style = {"margin": "5px"}
        return html.Div(
            children=[
                html.Button("1 Day", id="1d", style=button_style),
                html.Button("5 Days", id="5d", style=button_style),
                html.Button("1 Month", id="1mo", style=button_style),
                html.Button("3 Months", id="3mo", style=button_style),
                html.Button("6 Months", id="6mo", style=button_style),
                html.Button("1 Year", id="1y", style=button_style),
                html.Button("5 Years", id="5y", style=button_style),
                html.Button("Year To Date", id="ytd", style=button_style),
                html.Button("Max Date", id="max", style=button_style),
            ],
            style={"textAlign": "center", "margin": "20px 0"},
        )

    @staticmethod
    def create_investment_prediction_section() -> html.Div:
        """
        Create the investment prediction section

        :return: html.Div, the investment prediction section
        """
        return html.Div(
            [
                html.H2("Investment Prediction"),
                html.Div(
                    [
                        Utils.create_input_field(
                            "Initial Investment (DKK)", "initial-investment", 100000
                        ),
                        Utils.create_input_field(
                            "Monthly Investment (DKK)", "monthly-investment", 5000
                        ),
                        Utils.create_input_field("Number of Years", "num-years", 20),
                        Utils.create_input_field(
                            "Annual Interest Rate (%)", "annual-interest-rate", 10
                        ),
                        Utils.create_input_field(
                            "Ongoing Charges Rate (%)", "ongoing-charges-rate", 0.07
                        ),
                    ],
                    style={"textAlign": "center"},
                ),
                html.Button(
                    "Predict", id="predict-button", n_clicks=0, style={"margin": "20px"}
                ),
                dcc.Graph(id="prediction-graph"),
            ],
            style={"textAlign": "center", "margin": "20px auto"},
        )

    @staticmethod
    def create_input_field(label: str, id: str, value: float) -> html.Div:
        """
        Create an input field for the investment prediction section

        :param label: str, the label for the input field
        :param id: str, the ID for the input field
        :param value: float, the default value for the input field
        :return: html.Div, the input field
        """
        return html.Div(
            [
                html.Label(label),
                dcc.Input(
                    id=id,
                    type="number",
                    value=value,
                    style={"margin": "10px", "width": "80px"},
                ),
            ],
            style={"display": "inline-block", "margin": "10px"},
        )
