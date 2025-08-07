from collections import defaultdict

from ..common.event import FillEvent, EventBus, PositionEvent, EventType


class PositionManager:
    """
    头寸管理器负责跟踪和更新交易头寸。
    """
    def __init__(self, event_bus: EventBus):
        """
        初始化 PositionManager。

        :param event_bus: 事件总线实例。
        """
        self.event_bus = event_bus
        self.positions = defaultdict(float)
        self.event_bus.subscribe(EventType.FILL, self.on_fill)

    def on_fill(self, fill_event: FillEvent):
        """
        处理成交事件，更新头寸。
        """
        ticker = fill_event.ticker
        quantity = fill_event.quantity
        direction = fill_event.direction

        if direction == 'BUY':
            self.positions[ticker] += quantity
        elif direction == 'SELL':
            self.positions[ticker] -= quantity

        print(f"[Position] Updated position for {ticker}: {self.positions[ticker]} shares")
        self.event_bus.publish(PositionEvent(self.positions))