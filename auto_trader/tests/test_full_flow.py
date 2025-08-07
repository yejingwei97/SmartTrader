import unittest
from unittest.mock import MagicMock, patch
from queue import Queue
import time

from auto_trader.common.event import Event, EventBus, EventType, MarketEvent, SignalEvent, OrderEvent, FillEvent, PositionEvent
from auto_trader.data_handler.historic_csv_data_handler import HistoricCSVDataHandler
from auto_trader.strategy_engine.strategy import Strategy
from auto_trader.strategy_engine.strategy_engine import StrategyEngine
from auto_trader.execution_handler.execution_handler import ExecutionHandler
from auto_trader.position_manager.position_manager import PositionManager
from auto_trader.risk_manager.risk_manager import RiskManager


class MockStrategy(Strategy):
    """A mock strategy that always generates a BUY signal for AAPL."""
    def calculate_signals(self, event: Event) -> SignalEvent:
        if event.event_type == EventType.MARKET and event.ticker == "AAPL":
            return SignalEvent(ticker="AAPL", action="BUY", price=event.price)
        return None

class TestFullTradingFlow(unittest.TestCase):
    def setUp(self):
        self.event_bus = EventBus()
        self.mock_data_handler = MagicMock()
        self.strategy = MockStrategy()
        self.strategy_engine = StrategyEngine([self.strategy])
        self.position_manager = PositionManager(self.event_bus)
        self.execution_handler = ExecutionHandler(self.event_bus)
        self.risk_manager = RiskManager(self.event_bus, equity_limit=100000.0)

        # Subscribe handlers
        self.event_bus.subscribe(EventType.SIGNAL, self.execution_handler.on_signal)
        # PositionManager, RiskManager, and StrategyEngine subscribe to events internally

    def test_complete_flow(self):
        """Test the complete flow from market data to risk management."""
        # 1. Start the event bus
        self.event_bus.start()

        # 2. A market event occurs, which is published to the event bus
        market_event = MarketEvent(ticker="AAPL", price=150.0)
        self.event_bus.publish(market_event)

        # 3. Process events
        # Give the event bus a moment to process
        time.sleep(0.1) # allow for all events to be processed

        # 4. Check results
        # Check that the position manager has a position in AAPL
        self.assertIn("AAPL", self.position_manager.positions)
        self.assertEqual(self.position_manager.positions["AAPL"], 100) # Assuming quantity is 100

        # We can check the logs or mock the print function to verify the risk check message
        with patch('builtins.print') as mocked_print:
            # The events should have been processed, let's check the final state
            # The PositionEvent is published by the PositionManager, so we don't need to publish it manually
            time.sleep(0.1) # allow for all events to be processed

            # Check that the risk manager has calculated the total equity
            total_equity = self.risk_manager.calculate_total_equity()
            self.assertGreater(total_equity, 0)
            self.assertEqual(total_equity, 100 * 150.0)

        # 5. Stop the event bus
        self.event_bus.stop()

if __name__ == '__main__':
    unittest.main()