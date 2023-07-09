import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import create_engine

engine = create_engine("risingwave://root:@risingwave:4566/dev")

st.set_page_config(layout="wide")
st.title(f"ETH/USD OHLC data every {5} seconds")

def getData():
    return pd.read_sql_query('select * from ohlcv where product_id=\'BTC-USD\' order by minute asc', con=engine)

# here we store the data our Stream processing outputs
df = pd.DataFrame()

placeholder = st.empty()

while True:
    with placeholder.container():
        data = getData()
        fig = go.Figure(data=go.Ohlc(x=data['minute'],
                             open=data['open'],
                             high=data['high'],
                             low=data['low'],
                             close=data['close']))
        st.plotly_chart(fig, use_container_width=True)
