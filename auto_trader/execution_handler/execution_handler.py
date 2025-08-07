from ..common.event import SignalEvent, OrderEvent, FillEvent, EventBus

class ExecutionHandler:
    """
    The ExecutionHandler simulates a connection to a brokerage.
    It takes SignalEvents from a queue and places OrderEvents onto the event queue.
    """

    def __init__(self, event_bus: EventBus):
        """
        Initialises the ExecutionHandler.
        """
        self.event_bus = event_bus

    def on_signal(self, event: SignalEvent):
        """
        This is called by the EventBus when a SignalEvent is received.
        It takes a SignalEvent, converts it into an OrderEvent, and then
        simulates the execution of this order by creating a FillEvent.
        """
        order_event = OrderEvent(event.ticker, 'MKT', 100, event.action)
        self.event_bus.publish(order_event)

        # Simulate execution and create a FillEvent
        # In a real system, this would come from a brokerage
        fill_event = FillEvent(
            ticker=event.ticker, 
            quantity=100, 
            direction=event.action, 
            fill_price=event.price, # Use the price from the signal for simplicity
            commission=5.0 # Example commission
        )
        self.event_bus.publish(fill_event)