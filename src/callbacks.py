from datetime import datetime

import dash
import plotly.graph_objs as go
import pytz
from dash import Input, Output, State


class Callbacks:
    """
    A class to register the callbacks for the Dash app
    """

    @staticmethod
    def register_callbacks(app, data_fetcher):
        """
        Register the callbacks for the Dash app

        :param app: Dash app instance
        :param data_fetcher: DataFetcher instance
        """

        @app.callback(
            Output("stock-graph", "figure"),
            [
                Input(period, "n_clicks")
                for period in [
                    "1d",
                    "5d",
                    "1mo",
                    "3mo",
                    "6mo",
                    "1y",
                    "5y",
                    "ytd",
                    "max",
                ]
            ],
            [
                State(period, "id")
                for period in [
                    "1d",
                    "5d",
                    "1mo",
                    "3mo",
                    "6mo",
                    "1y",
                    "5y",
                    "ytd",
                    "max",
                ]
            ],
        )
        def update_graph(*args):
            ctx = dash.callback_context
            if not ctx.triggered:
                button_id = "ytd"
            else:
                button_id = ctx.triggered[0]["prop_id"].split(".")[0]

            if button_id == "ytd":
                start_date = datetime(datetime.now().year, 1, 1)
                df = data_fetcher.fetch_data(period="max")
                df = df[df.index >= start_date]
            elif button_id == "max":
                df = data_fetcher.fetch_data(period="max")
            else:
                period = button_id
                df = data_fetcher.fetch_data(period=period)

            if df is None or df.empty:
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
                title=f"S&P 500 ({button_id.upper()}) - {percentage_change_text}, {current_price_text}",
                xaxis_title="Date",
                yaxis_title="Price (DKK)",
                template="plotly_dark",
            )

            return fig

        @app.callback(
            Output("clock", "value"), Input("interval-component", "n_intervals")
        )
        def update_clock(n: int) -> str:
            """
            Update the clock display

            :param n: int, the number of intervals
            :return: str, the current time as a string
            """
            local_tz = pytz.timezone("Europe/Copenhagen")
            return datetime.now(local_tz).strftime("%H:%M:%S")

        @app.callback(
            Output("date", "children"), Input("interval-component", "n_intervals")
        )
        def update_date(n: int) -> str:
            """
            Update the date display

            :param n: int, the number of intervals
            :return: str, the current date as a string
            """
            local_tz = pytz.timezone("Europe/Copenhagen")
            return datetime.now(local_tz).strftime("%d-%m-%Y")

        @app.callback(
            Output("yearly-returns-graph", "figure"),
            Input("interval-component", "n_intervals"),
        )
        def update_yearly_returns_graph(n):
            df = data_fetcher.calculate_yearly_returns()
            if df.empty:
                return go.Figure(
                    layout=go.Layout(
                        title="No data available for Yearly Returns",
                        template="plotly_dark",
                    )
                )

            fig = go.Figure(
                data=[
                    go.Bar(
                        x=df["Year"],
                        y=df["Percentage Change"],
                        marker_color=[
                            "green" if val > 0 else "red"
                            for val in df["Percentage Change"]
                        ],
                    )
                ]
            )
            fig.update_layout(
                title="Yearly Percentage Change in Returns",
                xaxis_title="Year",
                yaxis_title="Percentage Change (%)",
                template="plotly_dark",
            )
            return fig

        @app.callback(
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
            ) = data_fetcher.calculate_investment(
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
