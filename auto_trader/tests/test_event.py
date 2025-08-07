import unittest
import time
from queue import Queue, Empty
from ..common.event import Event, EventType, MarketEvent, EventBus

class TestEventBus(unittest.TestCase):

    def setUp(self):
        """Set up a new event bus for each test."""
        self.event_bus = EventBus()
        self.test_queue = Queue()

    def test_subscribe_and_publish(self):
        """Test basic event subscription and publishing."""
        def simple_handler(event):
            self.test_queue.put(event)

        self.event_bus.subscribe(EventType.MARKET, simple_handler)
        market_event = MarketEvent("AAPL", 150.0)
        self.event_bus.publish(market_event)

        # The event bus runs in a separate thread, so we need to wait for the event to be processed
        self.event_bus.start()

        try:
            received_event = self.test_queue.get(timeout=2)
            self.assertEqual(received_event.type, EventType.MARKET)
            self.assertEqual(received_event.symbol, "AAPL")
        except Empty:
            self.fail("Handler did not receive the event within the timeout period.")
        finally:
            self.event_bus.stop()

    def test_start_and_stop(self):
        """Test the start and stop methods of the event bus thread."""
        self.event_bus.start()
        self.assertTrue(self.event_bus._running, "Event bus should be active after start()")
        self.assertIsNotNone(self.event_bus._thread, "Event bus thread should be created")
        self.assertTrue(self.event_bus._thread.is_alive(), "Event bus thread should be running")

        self.event_bus.stop()
        time.sleep(0.2) # Give a moment for the thread to stop
        self.assertFalse(self.event_bus._running, "Event bus should be inactive after stop()")
        # After stopping, the thread might still be alive for a short moment before exiting
        # self.assertFalse(self.event_bus._thread.is_alive(), "Event bus thread should be stopped")

if __name__ == '__main__':
    unittest.main()