import json

# pip install websocket-client
# pip install confluent-kafka
from websocket import create_connection

from bytewax.connectors.stdio import StdOutput
from bytewax.connectors.kafka import KafkaOutput
from bytewax.dataflow import Dataflow
from bytewax.inputs import PartitionedInput, StatefulSource
from bytewax.testing import run_main


class CoinbaseSource(StatefulSource):
    def __init__(self, product_id):
        self.product_id = product_id
        self.ws = create_connection("wss://ws-feed.exchange.coinbase.com")
        self.ws.send(
            json.dumps(
                {
                    "type": "subscribe",
                    "product_ids": [product_id],
                    "channels": ["level2"],
                }

            )
        )
        self.ws.send(
            json.dumps(
                {
                    "type": "subscribe",
                    "product_ids": [product_id],
                    "channels": ["ticker"]
                }

            )
        )

    def next(self):
        return self.ws.recv()

    def snapshot(self):
        return None

    def close(self):
        self.ws.close()


class CoinbaseFeedInput(PartitionedInput):
    def __init__(self, product_ids):
        self.product_ids = product_ids

    def list_parts(self):
        return set(self.product_ids)

    def build_part(self, for_key, resume_state):
        assert resume_state is None
        return CoinbaseSource(for_key)


def key_on_product(data):
    return (data["product_id"], data)


class OrderBook:
    def __init__(self):
        # if using Python < 3.7 need to use OrderedDict here
        self.product_id=None
        self.type=None
        self.time=None
        self.last_size=None
        self.trade_id=None
        self.price=None
        self.trade_id=None
        self.bids = {}
        self.asks = {}
        self.bid_price = None
        self.ask_price = None

    def update(self, data):
        self.product_id=data['product_id']
        self.time=data['time']
        self.type=data['type']
        if data['type'] == "ticker":
            self.price=float(data['price'])
            self.last_size=float(data['last_size'])
            self.trade_id=data['trade_id']
        else:
            if self.bids == {}:
                self.bids = {float(price): float(size) for price, size in data["bids"]}
                # The bid_price is the highest priced buy limit order.
                # since the bids are in order, the first item of our newly constructed bids
                # will have our bid price, so we can track the best bid
                self.bid_price = next(iter(self.bids))
            if self.asks == {}:
                self.asks = {float(price): float(size) for price, size in data["asks"]}
                # The ask price is the lowest priced sell limit order.
                # since the asks are in order, the first item of our newly constructed
                # asks will be our ask price, so we can track the best ask
                self.ask_price = next(iter(self.asks))
            else:
                # We receive a list of lists here, normally it is only one change,
                # but could be more than one.
                for update in data["changes"]:
                    price = float(update[1])
                    size = float(update[2])
                if update[0] == "sell":
                    # first check if the size is zero and needs to be removed
                    if size == 0.0:
                        try:
                            del self.asks[price]
                            # if it was the ask price removed,
                            # update with new ask price
                            if price <= self.ask_price:
                                self.ask_price = min(self.asks.keys())
                        except KeyError:
                            # don't need to add price with size zero
                            pass
                    else:
                        self.asks[price] = size
                        if price < self.ask_price:
                            self.ask_price = price
                if update[0] == "buy":
                    # first check if the size is zero and needs to be removed
                    if size == 0.0:
                        try:
                            del self.bids[price]
                            # if it was the bid price removed,
                            # update with new bid price
                            if price >= self.bid_price:
                                self.bid_price = max(self.bids.keys())
                        except KeyError:
                            # don't need to add price with size zero
                            pass
                    else:
                        self.bids[price] = size
                        if price > self.bid_price:
                            self.bid_price = price
        return self, {
            "product_id": self.product_id,
            "type": self.type,
            "time": self.time,
            "price": self.price,
            "last_size": self.last_size,
            "trade_id": self.trade_id,
            "bid": self.bid_price,
            "bid_size": self.bids[self.bid_price],
            "ask": self.ask_price,
            "ask_size": self.asks[self.ask_price],
            "spread": self.ask_price - self.bid_price,
        }


flow = Dataflow()
flow.input("input", CoinbaseFeedInput(["BTC-USD", "ETH-USD", "BTC-EUR", "ETH-EUR"]))
flow.map(json.loads)
# {
#     'type': 'l2update',
#     'product_id': 'BTC-USD',
#     'changes': [['buy', '36905.39', '0.00334873']],
#     'time': '2022-05-05T17:25:09.072519Z',
# }
flow.filter(lambda x: not x['type'] =='subscriptions')
flow.map(key_on_product)
# ('BTC-USD', {
#     'type': 'l2update',
#     'product_id': 'BTC-USD',
#     'changes': [['buy', '36905.39', '0.00334873']],
#     'time': '2022-05-05T17:25:09.072519Z',
# })
flow.stateful_map("order_book", lambda: OrderBook(), OrderBook.update)
# ('BTC-USD', (36905.39, 0.00334873, 36905.4, 1.6e-05, 0.010000000002037268))

flow.filter(lambda x: x[1]['type'] == 'ticker')
flow.output("out", StdOutput())
flow.map(lambda x: (x[0], json.dumps(x[1]).encode()))
flow.output("out", KafkaOutput(["redpanda:9092"], "trade"))

def main():
    run_main(flow)

if __name__=="__main__":
    main()