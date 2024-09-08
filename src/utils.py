from datetime import datetime

import dash_daq as daq
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
        return html.Div(
            [
                daq.LEDDisplay(
                    id="clock",
                    value=datetime.now().strftime("%H:%M:%S"),
                    color="#00cc96",
                    backgroundColor="#1e1e1e",
                    size=24,
                    style={
                        "textAlign": "left",
                        "margin": "10px",
                        "position": "absolute",
                        "top": "30px",
                        "left": "10px",
                    },
                ),
                html.Div(
                    id="date",
                    style={
                        "textAlign": "right",
                        "margin": "10px",
                        "color": "#00cc96",
                        "fontSize": "30px",
                        "position": "absolute",
                        "top": "30px",
                        "right": "10px",
                        "backgroundColor": "#1e1e1e",
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
        periods = ["1d", "1mo", "3mo", "6mo", "1y", "5y", "ytd", "max"]
        labels = {
            "1d": "1 Day",
            "1mo": "1 Month",
            "3mo": "3 Months",
            "6mo": "6 Months",
            "1y": "1 Year",
            "5y": "5 Years",
            "ytd": "Year to Date",
            "max": "Max",
        }
        return html.Div(
            style={"textAlign": "center", "margin": "20px"},
            children=[
                html.Button(
                    labels[period],
                    id=period,
                    n_clicks=0,
                    style={
                        "margin": "5px",
                        "backgroundColor": "#ffffff",
                        "color": "#000000",
                        "border": "1px solid #000000",
                    },
                )
                for period in periods
            ],
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
                            "Annual Interest Rate (%)", "annual-interest-rate", 7
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
