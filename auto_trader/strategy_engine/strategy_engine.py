from ..common.event import EventType, MarketEvent, SignalEvent, EventBus
from .strategy import Strategy

class StrategyEngine:
    """
    策略引擎，负责管理和执行所有策略。
    """
    def __init__(self, strategies: list[Strategy]):
        """
        初始化策略引擎。

        Args:
            strategies (list[Strategy]): 要管理的策略列表。
        """
        self._strategies = strategies
        self._event_bus = EventBus()
        self._subscribe_to_market_data()

    def _subscribe_to_market_data(self):
        """
        订阅市场数据事件。
        """
        self._event_bus.subscribe(EventType.MARKET, self.on_market_event)

    def on_market_event(self, event: MarketEvent):
        """
        处理市场数据事件，将其传递给所有策略。

        Args:
            event (MarketEvent): 市场数据事件。
        """
        for strategy in self._strategies:
            signal_event = strategy.calculate_signals(event)
            if signal_event:
                self._event_bus.publish(signal_event)