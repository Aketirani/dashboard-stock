import warnings
from datetime import datetime

import dash
import dash_daq as daq
import plotly.graph_objs as go
import yfinance as yf
from dash import Input, Output, State, dcc, html

# Suppress specific FutureWarning from yfinance
warnings.simplefilter(action="ignore", category=FutureWarning)

app = dash.Dash(__name__)

# Fetch S&P 500 data
def fetch_data(period="1y"):
    try:
        df = yf.download("^GSPC", period=period)
        if df.empty:
            raise ValueError("No data found for the given period.")
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


# Investment calculation function
def calculate_investment(
    initial_investment,
    monthly_investment,
    num_years,
    annual_interest_rate,
    ongoing_charges_rate,
):
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
        profit = investment_value - initial_investment - (i + 1) * monthly_investment

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


# Layout components
def create_layout():
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


def create_clock_and_date():
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


def create_period_buttons():
    periods = ["1d", "1wk", "1mo", "3mo", "6mo", "1y", "3y", "5y", "ytd", "max"]
    return html.Div(
        [
            html.Button(
                period.replace("ytd", "Year to Date")
                .replace("max", "Max")
                .replace("mo", " Month")
                .replace("wk", " Week")
                .replace("d", " Day")
                .replace("y", " Year"),
                id=period,
                n_clicks=0,
                style={"margin": "5px"},
            )
            for period in periods
        ],
        style={"textAlign": "center"},
    )


def create_investment_prediction_section():
    return html.Div(
        [
            html.H2("Investment Prediction"),
            html.Div(
                [
                    create_input_field(
                        "Initial Investment (DKK)", "initial-investment", 100000
                    ),
                    create_input_field(
                        "Monthly Investment (DKK)", "monthly-investment", 5000
                    ),
                    create_input_field("Number of Years", "num-years", 20),
                    create_input_field(
                        "Annual Interest Rate (%)", "annual-interest-rate", 7
                    ),
                    create_input_field(
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


def create_input_field(label, id, value):
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


# Callbacks
@app.callback(
    Output("stock-graph", "figure"),
    [
        Input(period, "n_clicks")
        for period in ["1d", "1wk", "1mo", "3mo", "6mo", "1y", "3y", "5y", "ytd", "max"]
    ],
    [
        State(period, "id")
        for period in ["1d", "1wk", "1mo", "3mo", "6mo", "1y", "3y", "5y", "ytd", "max"]
    ],
)
def update_graph(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = "ytd"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    period = button_id
    df = fetch_data(period=period)
    if df is None:
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

    # Calculate percentage change
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


@app.callback(Output("clock", "value"), Input("interval-component", "n_intervals"))
def update_clock(n):
    return datetime.now().strftime("%H:%M:%S")


@app.callback(Output("date", "children"), Input("interval-component", "n_intervals"))
def update_date(n):
    return datetime.now().strftime("%d-%m-%Y")


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
    n_clicks,
    initial_investment,
    monthly_investment,
    num_years,
    annual_interest_rate,
    ongoing_charges_rate,
):
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

    money_invested_yearly, investment_yearly, profits_yearly = calculate_investment(
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


# Update clock and date every second
app.layout = create_layout()
app.layout.children.append(
    dcc.Interval(id="interval-component", interval=1 * 1000, n_intervals=0)
)

if __name__ == "__main__":
    app.run_server(debug=True)
