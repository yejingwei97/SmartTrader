from abc import ABC, abstractmethod
from typing import Optional
from ..common.event import SignalEvent, MarketEvent

class Strategy(ABC):
    """
    Strategy 是一个抽象基类，提供了所有后续策略类必须实现的接口。
    """

    @abstractmethod
    def calculate_signals(self, event: MarketEvent) -> Optional[SignalEvent]:
        """
        根据市场数据计算并返回交易信号。

        Args:
            event: 市场事件对象

        Returns:
            如果生成了交易信号，则返回 SignalEvent 对象，否则返回 None。
        """
        raise NotImplementedError("应该在子类中实现 calculate_signals() 方法")