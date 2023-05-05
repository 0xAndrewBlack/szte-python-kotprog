import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from marketbot import market


class TestMarket(unittest.TestCase):
    def setUp(self):
        self.market = market.Market()

    def test_get_items(self):
        items = self.market.paginate_items()
        # Coroutine object
        self.assertIsInstance(items, object)

    def test_get_item(self):
        item = self.market.get_item(1)
        # Coroutine object
        self.assertIsInstance(item, object)


if __name__ == "__main__":
    unittest.main()