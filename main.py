import logging
import warnings

import dash
from dash import dcc

from src.callbacks import register_callbacks
from src.data_fetcher import DataFetcher
from src.layout import create_layout


class StockDashboard:
    """
    A class to represent the stock dashboard application

    app: Dash, the Dash application instance
    server: Flask, the Flask server instance used by Dash
    data_fetcher: DataFetcher, an instance of the DataFetcher class to fetch stock data
    """

    def __init__(self):
        logging.basicConfig(level=logging.WARNING)
        warnings.simplefilter(action="ignore", category=FutureWarning)

        self.app = dash.Dash(__name__)
        self.server = self.app.server
        self.data_fetcher = DataFetcher()
        self.app.layout = create_layout()
        self.app.layout.children.append(
            dcc.Interval(id="interval-component", interval=1 * 1000, n_intervals=0)
        )
        register_callbacks(self.app, self.data_fetcher)


if __name__ == "__main__":
    dashboard = StockDashboard()
    dashboard.app.run_server(debug=True)
