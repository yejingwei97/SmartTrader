import unittest
from unittest.mock import MagicMock
import time
from queue import Queue, Empty
from auto_trader.data_handler.data_handler import DataHandler
from auto_trader.common.event import EventBus, MarketEvent, EventType

class TestDataHandler(unittest.TestCase):
    def setUp(self):
        self.event_bus = EventBus()
        # Reset handlers for each test to ensure isolation
        self.event_bus._handlers = {event_type: [] for event_type in EventType}
        self.event_bus._event_queue = Queue()
        self.data_handler = DataHandler(self.event_bus, ticker="AAPL")

    def tearDown(self):
        if self.event_bus.is_running():
            self.event_bus.stop()
        if self.data_handler._running:
            self.data_handler.stop()

    def test_start_and_stop(self):
        self.data_handler.start()
        self.assertTrue(self.data_handler._running)
        self.assertTrue(self.data_handler._thread.is_alive())
        self.data_handler.stop()
        self.assertFalse(self.data_handler._running)
        self.data_handler._thread.join(timeout=2)
        self.assertFalse(self.data_handler._thread.is_alive())

    def test_publish_market_event(self):
        # Use a mock handler to verify that the event is published correctly
        mock_handler = MagicMock()
        self.event_bus.subscribe(EventType.MARKET, mock_handler)
        
        self.event_bus.start()
        self.data_handler.start()
        
        time.sleep(1.5)  # Wait for at least one event to be generated
        
        self.data_handler.stop()
        self.event_bus.stop()

        # Verify that the handler was called
        self.assertTrue(mock_handler.called)
        
        # Verify the content of the received event
        event_args = mock_handler.call_args[0]
        self.assertEqual(len(event_args), 1)
        received_event = event_args[0]
        self.assertIsInstance(received_event, MarketEvent)
        self.assertEqual(received_event.event_type, EventType.MARKET)
        self.assertEqual(received_event.ticker, "AAPL")

if __name__ == '__main__':
    unittest.main()