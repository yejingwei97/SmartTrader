import time
from threading import Thread
from auto_trader.common.event import MarketEvent
from abc import ABC, abstractmethod

class DataHandler(ABC):
    """
    DataHandler is an abstract base class providing an interface for all subsequent
    (inherited) data handlers (both live and historic).

    The goal of a (derived) DataHandler object is to output a generated
    MarketEvent onto the events queue.

    This sits at the top of the hierarchy, despite the fact that it will probably
    be the last class we write inheritance-wise. It is designed to track
    the "latest" data feed from a market, with a timestamp to assist with
    backtesting and live trading.
    """

    @abstractmethod
    def start(self):
        """
        Starts the data handler.
        """
        raise NotImplementedError("Should implement start()")

    @abstractmethod
    def stop(self):
        """
        Stops the data handler.
        """
        raise NotImplementedError("Should implement stop()")