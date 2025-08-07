from enum import Enum
from queue import Queue, Empty
import time
from threading import Thread

class EventType(Enum):
    MARKET = "MARKET"
    SIGNAL = "SIGNAL"
    ORDER = "ORDER"
    FILL = "FILL"
    POSITION = "POSITION"

class Event:
    """
    Event is base class, providing an interface for all subsequent 
    (inherited) events, that will trigger further events in the trading infrastructure. 
    """
    def __init__(self, event_type: EventType):
        self.event_type = event_type

class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with corresponding bars.
    """
    def __init__(self, ticker: str, price: float):
        super().__init__(EventType.MARKET)
        self.ticker = ticker
        self.price = price

class SignalEvent(Event):
    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.
    """
    def __init__(self, ticker: str, action: str, price: float):
        super().__init__(EventType.SIGNAL)
        self.ticker = ticker
        self.action = action # 'BUY' or 'SELL'
        self.price = price

class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a ticker (e.g. AAPL), a type (market or limit),
    a quantity and a direction.
    """
    def __init__(self, ticker: str, order_type: str, quantity: int, direction: str):
        super().__init__(EventType.ORDER)
        self.ticker = ticker
        self.order_type = order_type # 'MKT' or 'LMT'
        self.quantity = quantity
        self.direction = direction # 'BUY' or 'SELL'

class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned from a brokerage.
    Stores the quantity of an instrument actually filled and at what price.
    In addition, stores the commission of the trade from the brokerage.
    """
    def __init__(self, ticker: str, quantity: int, direction: str, fill_price: float, commission: float = 0.0):
        super().__init__(EventType.FILL)
        self.ticker = ticker
        self.quantity = quantity
        self.direction = direction
        self.fill_price = fill_price
        self.commission = commission

class PositionEvent(Event):
    """
    当头寸更新时触发该事件。
    """
    def __init__(self, positions: dict):
        super().__init__(EventType.POSITION)
        self.positions = positions

class EventBus:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if EventBus._initialized:
            return
        self._event_queue = Queue()
        self._handlers = {event_type: [] for event_type in EventType}
        self._running = False
        self._thread = Thread(target=self._run, daemon=True)
        EventBus._initialized = True
    
    def _run(self):
        """
        Runs the event loop.
        """
        while self._running:
            try:
                event = self._event_queue.get(block=True, timeout=1)
                if event and event.event_type in self._handlers:
                    for handler in self._handlers[event.event_type]:
                        handler(event)
            except Empty:
                continue
    
    def subscribe(self, event_type: EventType, handler):
        """
        Subscribe a handler to a specific event type.
        """
        if event_type in self._handlers:
            self._handlers[event_type].append(handler)

    def publish(self, event: Event):
        """
        Publish an event to the event bus.
        """
        self._event_queue.put(event)

    def start(self):
        """
        Starts the event bus thread.
        """
        self._running = True
        self._thread.start()
    
    def stop(self):
        """
        Stops the event bus thread.
        """
        self._running = False
        if self._thread.is_alive():
            self._thread.join()

    def is_running(self):
        """
        Returns the running state of the event bus.
        """
        return self._running