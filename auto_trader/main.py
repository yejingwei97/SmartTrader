import time
from queue import Queue, Empty
from auto_trader.common.event import EventBus, EventType, MarketEvent, SignalEvent, OrderEvent, FillEvent
from auto_trader.data_handler.historic_csv_data_handler import HistoricCSVDataHandler
from auto_trader.strategy_engine.strategy_engine import StrategyEngine
from auto_trader.strategy_engine.buy_and_hold_strategy import MovingAverageCrossoverStrategy
from auto_trader.execution_handler.execution_handler import ExecutionHandler
from auto_trader.position_manager.position_manager import PositionManager
from auto_trader.risk_manager.risk_manager import RiskManager


def handle_order_event(event: OrderEvent):
    """测试用的事件处理器，打印订单事件"""
    print(f"接收到订单事件: {event.ticker} - {event.direction} {event.quantity} shares at {event.order_type} price")


def handle_fill_event(event: FillEvent):
    """测试用的事件处理器，打印成交事件"""
    print(f"接收到成交事件: {event.ticker} - {event.direction} {event.quantity} shares at {event.fill_price} price, commission: {event.commission}")


def main():
    """主函数，启动所有组件"""
    # 1. 初始化核心组件
    event_bus = EventBus()
    data_handler = HistoricCSVDataHandler(event_bus, ['auto_trader/data/AAPL.csv'], ['AAPL'])
    # 创建策略实例
    strategy = MovingAverageCrossoverStrategy(data_handler, short_window=5, long_window=10)
    # 创建策略引擎并传入策略列表
    strategy_engine = StrategyEngine([strategy])
    # risk_manager 需要在 position_manager 之后创建，因为它依赖后者的工作流
    position_manager = PositionManager(event_bus)
    execution_handler = ExecutionHandler(event_bus)
    # 创建风险管理器，并设置一个较低的风险限额以便测试
    risk_manager = RiskManager(event_bus, equity_limit=10000.0)

    # 2. 注册事件处理器
    # StrategyEngine 会自动订阅 MARKET 事件，所以下面这行可以移除
    # event_bus.subscribe(EventType.MARKET, strategy_engine.on_market_event)
    event_bus.subscribe(EventType.SIGNAL, execution_handler.on_signal)
    event_bus.subscribe(EventType.ORDER, handle_order_event)
    event_bus.subscribe(EventType.FILL, handle_fill_event)

    # 3. 启动事件总线
    print("系统启动...")
    event_bus.start()
    print("事件总线已启动")

    # 4. 启动其他模块的线程
    data_handler.start()

    # 保持主线程运行
    try:
        while event_bus.is_running() and data_handler._thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("接收到退出信号，正在关闭系统...")
    finally:
        event_bus.stop()
        data_handler.stop()
        print("系统已关闭。")

if __name__ == "__main__":
    main()