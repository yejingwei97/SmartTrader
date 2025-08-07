import pandas as pd
from threading import Thread
import time
from auto_trader.common.event import MarketEvent
from auto_trader.data_handler.data_handler import DataHandler

class HistoricCSVDataHandler(DataHandler):
    """
    HistoricCSVDataHandler is designed to read CSV files for each requested
    symbol from disk and provide an interface to obtain the "latest" bar in a
    manner identical to a live trading interface.
    """

    def __init__(self, event_bus, csv_files: list, tickers: list):
        self.event_bus = event_bus
        self.csv_files = csv_files
        self.tickers = tickers
        self.ticker_data = {}
        self.latest_ticker_data = {}
        self.iterators = {}
        self._running = False
        self._thread = None

        self._open_convert_csv_files()

    def _open_convert_csv_files(self):
        """
        Opens the CSV files from the data directory, converting
        them into pandas DataFrames stored in a dictionary.
        """
        comb = zip(self.csv_files, self.tickers)
        for path, ticker in comb:
            df = pd.read_csv(
                path, header=0, index_col=0, parse_dates=True
            )
            self.ticker_data[ticker] = df
            self.iterators[ticker] = self.ticker_data[ticker].iterrows()
            self.latest_ticker_data[ticker] = []

    def get_latest_bars_values(self, ticker, val_type, n=1):
        """
        返回最新的 N 条数据
        """
        if ticker in self.latest_ticker_data:
            return [bar[val_type] for bar in self.latest_ticker_data[ticker][-n:]]
        else:
            print(f"Ticker {ticker} is not available in the data.")
            return []

    def _get_new_bar(self):
        """
        Returns the latest bar from the data feed as a tuple of
        (sybmbol, datetime, open, high, low, close, volume).
        """
        all_stopped = True
        for ticker in self.tickers:
            try:
                row = next(self.iterators[ticker])
                self.latest_ticker_data[ticker].append(row[1])
                yield MarketEvent(ticker, row[1]['close'])
                all_stopped = False
            except StopIteration:
                # End of the data feed for this symbol
                continue
        if all_stopped:
            self._running = False

    def start(self):
        """
        Starts the data handler thread.
        """
        self._running = True
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """
        Stops the data handler thread.
        """
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join()

    def _run(self):
        """
        Main loop of the data handler.
        """
        while self._running:
            for event in self._get_new_bar():
                self.event_bus.publish(event)
            time.sleep(0.1) # Simulate time passing