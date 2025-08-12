import logging
import warnings

import dash
from dash import dcc

from src.callbacks import Callbacks
from src.extractor import Extractor
from src.layout import Layout


class StockDashboard:
    """
    A class to represent the stock dashboard application

    app: Dash, the Dash application instance
    server: Flask, the Flask server instance used by Dash
    extractor: Extractor, an instance of the Extractor class to extract stock data
    """

    def __init__(self):
        logging.basicConfig(level=logging.WARNING)
        warnings.simplefilter(action="ignore", category=FutureWarning)

        self.app = dash.Dash(__name__)
        self.server = self.app.server
        self.data_fetcher = Extractor()
        self.app.layout = Layout.create_layout()
        self.app.layout.children.append(
            dcc.Interval(id="interval-component", interval=1 * 1000, n_intervals=0)
        )
        Callbacks.register_callbacks(self.app, self.data_fetcher)


dashboard = StockDashboard()
server = dashboard.server

if __name__ == "__main__":
    dashboard.app.run(debug=True)
