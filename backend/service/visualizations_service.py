import json

import plotly
from sqlalchemy import Integer
import plotly.graph_objs as go
import pandas as pd

from repository import product_repository


def create_visualization_for_product(product_id: Integer):
    past_prices = product_repository.get_past_prices_for_product_by_id(product_id)
    current_price = product_repository.get_current_price_for_product_by_id(product_id)
    df = _create_prices_df(past_prices, current_price)
    html_visualization = _create_price_visualization(df)
    return html_visualization


def _create_prices_df(past_prices, current_price):
    rows = list()
    for past_price in past_prices:
        row = dict()
        row['Date'] = past_price.date
        row['Price'] = past_price.price
        rows.append(row)
    row = dict()
    row['Date'] = current_price.date
    row['Price'] = current_price.price
    rows.append(row)
    df = pd.DataFrame(rows)
    df['Date'] = pd.to_datetime(df['Date'])
    return df


def _create_price_visualization(df):
    fig = go.Figure()

    # Assuming your DataFrame columns are named 'date' and 'price'
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Price'], mode='lines+markers', name='Price', hovertemplate=f'%{{y}} MKD<br>Date: %{{x}}<br><extra></extra>',
))

    fig.update_layout(
        title='Prices and Predictions over Time',
        xaxis_title='Dates',
        yaxis_title='Price (МКД)',
        template='plotly',
        dragmode=False
        # yaxis=dict(
        #     tick0=0,
        #     dtick=500,
        #     tickformat='d'
        # )
    )
    fig.update_xaxes(
        tickvals=df['Date'],
        tickformat="%d %b %Y",
    )
    fig.update_yaxes(
        tickvals=df['Price'],
        tickformat='d'
    )
    graphJSON = json.loads(plotly.io.to_json(fig, pretty=True))
    graphJSON['config'] = {'displayModeBar': False, 'responsive': True}
    return graphJSON
