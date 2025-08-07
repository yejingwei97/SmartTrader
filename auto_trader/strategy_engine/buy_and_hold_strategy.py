import numpy as np
from ..common.event import SignalEvent, EventType
from .strategy import Strategy

class MovingAverageCrossoverStrategy(Strategy):
    """
    一个简单的移动平均线交叉策略。
    当短期简单移动平均线（SMA）上穿长期简单移动平均线时，生成买入信号。
    """
    def __init__(self, bars, short_window=10, long_window=30):
        """
        初始化移动平均线交叉策略。

        参数:
        bars (HistoricCSVDataHandler): 数据处理器，用于访问价格数据。
        short_window (int): 短期移动平均线的周期。
        long_window (int): 长期移动平均线的周期。
        """
        self.bars = bars
        self.short_window = short_window
        self.long_window = long_window
        self.bought = False  # 跟踪是否已经买入

    def calculate_signals(self, event):
        """
        计算信号事件。
        """
        if event.event_type == EventType.MARKET:
            ticker = event.ticker
            # 获取最新的 `long_window` 条数据
            close_prices = self.bars.get_latest_bars_values(ticker, "close", self.long_window)

            if len(close_prices) >= self.long_window and not self.bought:
                short_sma = np.mean(close_prices[-self.short_window:])
                long_sma = np.mean(close_prices)

                # 检查金叉
                if short_sma >= long_sma:
                    print(f"交叉信号：短期SMA={short_sma:.2f}, 长期SMA={long_sma:.2f}")
                    signal = SignalEvent(ticker, "BUY", 100)  # 创建买入信号
                    self.bought = True # 标记为已买入，避免重复信号
                    return signal
        return None