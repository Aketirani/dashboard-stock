import logging
import os
import sys
import warnings
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional, Tuple

import dash
import dash_daq as daq
import pandas as pd
import plotly.graph_objs as go
import yfinance as yf
from dash import Input, Output, State, dcc, html


class StockDashboard:
    def __init__(self):
        """
        Initialize the StockDashboard class
        """
        logging.basicConfig(level=logging.WARNING)
        warnings.simplefilter(action="ignore", category=FutureWarning)

        self.app = dash.Dash(__name__)
        self.server = self.app.server
        self.data_cache = {}
        self.app.layout = self.create_layout()
        self.app.layout.children.append(
            dcc.Interval(id="interval-component", interval=1 * 1000, n_intervals=0)
        )
        self.register_callbacks()

    @contextmanager
    def suppress_stdout(self):
        """
        Context manager to suppress standard output

        :yield: None
        """
        with open(os.devnull, "w") as devnull:
            old_stdout = sys.stdout
            sys.stdout = devnull
            try:
                yield
            finally:
                sys.stdout = old_stdout

    def fetch_data(self, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Fetch stock data for a given period

        :param period: str, the period for which to fetch data
        :return: Optional[pd.DataFrame], the fetched data as a DataFrame, or None if an error occurs
        """
        if period in self.data_cache:
            logging.info(f"Using cached data for period {period}")
            return self.data_cache[period]

        try:
            with self.suppress_stdout():
                df = yf.download("^GSPC", period=period)
            if df.empty:
                raise ValueError("No data found for the given period.")
            logging.info(f"Fetched data for period {period}: {df.head()}")
            self.data_cache[period] = df
            return df
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            return None

    def create_layout(self) -> html.Div:
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
                self.create_clock_and_date(),
                html.H2("S&P 500 History", style={"textAlign": "center"}),
                dcc.Graph(id="stock-graph"),
                self.create_period_buttons(),
                self.create_investment_prediction_section(),
            ],
        )

    def create_clock_and_date(self) -> html.Div:
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

    def create_period_buttons(self) -> html.Div:
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

    def create_investment_prediction_section(self) -> html.Div:
        """
        Create the investment prediction section

        :return: html.Div, the investment prediction section
        """
        return html.Div(
            [
                html.H2("Investment Prediction"),
                html.Div(
                    [
                        self.create_input_field(
                            "Initial Investment (DKK)", "initial-investment", 100000
                        ),
                        self.create_input_field(
                            "Monthly Investment (DKK)", "monthly-investment", 5000
                        ),
                        self.create_input_field("Number of Years", "num-years", 20),
                        self.create_input_field(
                            "Annual Interest Rate (%)", "annual-interest-rate", 7
                        ),
                        self.create_input_field(
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

    def create_input_field(self, label: str, id: str, value: float) -> html.Div:
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

    def register_callbacks(self):
        """
        Register the callbacks for the Dash app.
        """

        @self.app.callback(
            Output("stock-graph", "figure"),
            [
                Input(period, "n_clicks")
                for period in ["1d", "1mo", "3mo", "6mo", "1y", "5y", "ytd", "max"]
            ],
            [
                State(period, "id")
                for period in ["1d", "1mo", "3mo", "6mo", "1y", "5y", "ytd", "max"]
            ],
        )
        def update_graph(*args) -> go.Figure:
            """
            Update the stock graph based on the selected period

            :param args: The arguments passed by the callback
            :return: go.Figure, the updated stock graph
            """
            ctx = dash.callback_context
            if not ctx.triggered:
                button_id = "ytd"
            else:
                button_id = ctx.triggered[0]["prop_id"].split(".")[0]

            period = button_id
            df = self.fetch_data(period=period)
            if df is None:
                logging.error(f"No data available for period {period}")
                return go.Figure(
                    layout=go.Layout(
                        title="No data available for the selected period",
                        template="plotly_dark",
                    )
                )

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["Close"],
                    mode="lines",
                    name="S&P 500",
                    line=dict(color="white"),
                )
            )

            start_price = df["Close"].iloc[0]
            end_price = df["Close"].iloc[-1]
            percentage_change = ((end_price - start_price) / start_price) * 100
            sign = "+" if percentage_change > 0 else ""
            percentage_change_text = f"Change: {sign}{percentage_change:.2f}%"
            current_price_text = f"Current Price: {end_price:.2f} DKK"

            fig.update_layout(
                template="plotly_dark",
                xaxis_title="Date",
                yaxis_title="Price (DKK)",
                title=f"S&P 500 ({period.upper()}) - {percentage_change_text}, {current_price_text}",
            )

            return fig

        @self.app.callback(
            Output("clock", "value"), Input("interval-component", "n_intervals")
        )
        def update_clock(n: int) -> str:
            """
            Update the clock display

            :param n: int, the number of intervals
            :return: str, the current time as a string
            """
            return datetime.now().strftime("%H:%M:%S")

        @self.app.callback(
            Output("date", "children"), Input("interval-component", "n_intervals")
        )
        def update_date(n: int) -> str:
            """
            Update the date display

            :param n: int, the number of intervals
            :return: str, the current date as a string
            """
            return datetime.now().strftime("%d-%m-%Y")

        @self.app.callback(
            Output("prediction-graph", "figure"),
            Input("predict-button", "n_clicks"),
            [
                State("initial-investment", "value"),
                State("monthly-investment", "value"),
                State("num-years", "value"),
                State("annual-interest-rate", "value"),
                State("ongoing-charges-rate", "value"),
            ],
        )
        def predict_investment(
            n_clicks: int,
            initial_investment: float,
            monthly_investment: float,
            num_years: int,
            annual_interest_rate: float,
            ongoing_charges_rate: float,
        ) -> go.Figure:
            """
            Predict the investment value based on user inputs

            :param n_clicks: int, the number of clicks on the predict button
            :param initial_investment: float, the initial investment amount
            :param monthly_investment: float, the monthly investment amount
            :param num_years: int, the number of years for the investment
            :param annual_interest_rate: float, the annual interest rate
            :param ongoing_charges_rate: float, the ongoing charges rate
            :return: go.Figure, the investment prediction graph
            """
            if (
                not initial_investment
                or not monthly_investment
                or not num_years
                or not annual_interest_rate
                or not ongoing_charges_rate
            ):
                return go.Figure()

            annual_interest_rate /= 100
            ongoing_charges_rate /= 100

            (
                money_invested_yearly,
                investment_yearly,
                profits_yearly,
            ) = self.calculate_investment(
                initial_investment,
                monthly_investment,
                num_years,
                annual_interest_rate,
                ongoing_charges_rate,
            )

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=list(range(num_years + 1)),
                    y=money_invested_yearly,
                    mode="lines",
                    name="Money Invested (DKK)",
                    line=dict(color="blue"),
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=list(range(num_years + 1)),
                    y=investment_yearly,
                    mode="lines",
                    name="Investment Value (DKK)",
                    line=dict(color="green"),
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=list(range(num_years + 1)),
                    y=profits_yearly,
                    mode="lines",
                    name="Profit (DKK)",
                    line=dict(color="orange"),
                )
            )
            fig.update_layout(
                template="plotly_dark", xaxis_title="Years", yaxis_title="Amount (DKK)"
            )
            return fig

    def calculate_investment(
        self,
        initial_investment: float,
        monthly_investment: float,
        num_years: int,
        annual_interest_rate: float,
        ongoing_charges_rate: float,
    ) -> Tuple[List[int], List[int], List[int]]:
        """
        Calculate the investment value over time

        :param initial_investment: float, the initial investment amount
        :param monthly_investment: float, the monthly investment amount
        :param num_years: int, the number of years for the investment
        :param annual_interest_rate: float, the annual interest rate
        :param ongoing_charges_rate: float, the ongoing charges rate
        :return: Tuple[List[int], List[int], List[int]], the yearly money invested, investment value, and profits
        """
        low_tax = 0.27
        high_tax = 0.42
        threshold_tax = 61000
        months = 12
        num_months = num_years * months
        monthly_interest_rate = annual_interest_rate / months
        investment_value = initial_investment
        profit = 0
        investment = [initial_investment]
        money_invested = [initial_investment]
        profits = [0]

        for i in range(num_months):
            interest = investment_value * monthly_interest_rate
            investment_value += interest
            investment_value += monthly_investment
            profit = (
                investment_value - initial_investment - (i + 1) * monthly_investment
            )

            if (i + 1) % months == 0:
                if profit < threshold_tax:
                    tax = profit * low_tax
                else:
                    tax = threshold_tax * low_tax + (profit - threshold_tax) * high_tax
            else:
                tax = 0

            profit -= tax
            ongoing_charges = investment_value * (ongoing_charges_rate / months)
            investment_value -= ongoing_charges
            total_money = initial_investment + (i + 1) * monthly_investment
            investment.append(investment_value)
            profits.append(profit)
            money_invested.append(total_money)

        money_invested_yearly = [round(num) for num in money_invested[0::months]]
        investment_yearly = [round(num) for num in investment[0::months]]
        profits_yearly = [round(num) for num in profits[0::months]]

        return money_invested_yearly, investment_yearly, profits_yearly


dashboard = StockDashboard()
server = dashboard.server

if __name__ == "__main__":
    dashboard.app.run_server(debug=True)
