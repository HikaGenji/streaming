Stream processing with redpanda backend.

- listen to trade and quotes from coinbase websocket
- perform as of join between trade and quote using bytewax dataflow
- use risingwave to create ohlc minute bar materialized view
- plot ohlc with plotly in streamlit
