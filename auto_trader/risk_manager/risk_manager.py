from auto_trader.common.event import EventBus, EventType, MarketEvent, PositionEvent

class RiskManager:
    """
    风险管理器，监控投资组合的风险。
    """
    def __init__(self, event_bus: EventBus, equity_limit: float = 1_000_000.0):
        self.event_bus = event_bus
        self.equity_limit = equity_limit
        self.latest_prices = {}
        self.positions = {}
        self.event_bus.subscribe(EventType.MARKET, self.on_market_event)
        self.event_bus.subscribe(EventType.POSITION, self.on_position_event)

    def on_market_event(self, event: MarketEvent):
        """
        处理市场事件，更新最新价格。
        """
        self.latest_prices[event.ticker] = event.price

    def on_position_event(self, event: PositionEvent):
        """
        处理头寸事件，在每次头寸更新后重新计算风险。
        """
        self.positions = event.positions
        # 在成交后，需要确保最新价格可用，如果还没有市场数据，则不进行计算
        if not self.latest_prices:
            return
            
        total_equity = self.calculate_total_equity()
        if total_equity > self.equity_limit:
            print(f"[RiskManager] 警告: 投资组合总市值 {total_equity:.2f} 已超过风险限额 {self.equity_limit:.2f}!")

    def calculate_total_equity(self) -> float:
        """
        计算投资组合的总市值。
        """
        total_equity = 0.0
        for ticker, position in self.positions.items():
            if ticker in self.latest_prices:
                total_equity += position * self.latest_prices[ticker]
        return total_equity