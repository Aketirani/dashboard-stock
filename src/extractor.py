import logging
import os
import sys
from contextlib import contextmanager
from typing import List, Optional, Tuple

import pandas as pd
import yfinance as yf


class Extractor:
    """
    A class to extract stock data, and calculate investment values over time

    data_cache: dict, a cache to store fetched data
    """

    def __init__(self):
        """
        Initialize the Extractor class
        """
        self.data_cache = {}

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
        Fetch stock data for a given period and cache it

        :param period: str, the period for which to fetch data
        :return: Optional[pd.DataFrame], the fetched data as a DataFrame, or None if an error occurs
        """
        if period in self.data_cache:
            logging.info(f"Using cached data for period {period}")
            return self.data_cache[period]
        try:
            with self.suppress_stdout():
                if period == "1d":
                    df = yf.download("SXR8.DE", period=period, interval="1m")
                elif period == "5d":
                    df = yf.download("SXR8.DE", period=period, interval="1h")
                else:
                    df = yf.download("SXR8.DE", period=period)
            if df.empty:
                raise ValueError("No data found for the given period")
            logging.info(f"Fetched data for period {period}: {df.head()}")
            self.data_cache[period] = df
            return df
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            return None

    def calculate_yearly_returns(self) -> pd.DataFrame:
        """
        Calculate the yearly percentage change in stock prices based on the maximum available data period.

        :return: pd.DataFrame, containing the annual percentage change in the stock price
        """
        df = self.fetch_data(period="max")
        if df is not None and "Close" in df.columns:
            df["Year"] = df.index.year
            yearly_prices = df.groupby("Year")["Close"].last()
            yearly_returns = yearly_prices.pct_change() * 100
            yearly_returns_df = yearly_returns.reset_index()
            yearly_returns_df.columns = ["Year", "Percentage Change"]
            return yearly_returns_df
        return pd.DataFrame(columns=["Year", "Percentage Change"])

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
        threshold_tax = 80000
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
