import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import create_engine

engine = create_engine("risingwave://root:@host.docker.internal:4566/dev")

st.set_page_config(layout="wide")
st.title(f"ETH/USD OHLC data every {5} seconds")

def getData():
    return pd.read_sql_query('select * from ohlcv', con=engine)

# here we store the data our Stream processing outputs
df = pd.DataFrame()

placeholder = st.empty()

while True:
    with placeholder.container():
        data = getData()
        fig = go.Figure(data=go.Ohlc(x=data['time'],
                             open=data['open'],
                             high=data['high'],
                             low=data['low'],
                             close=data['close']))
        fig.show()
