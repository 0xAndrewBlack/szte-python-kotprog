import pytest
from unittest.mock import Mock, patch

from src import market


@pytest.mark.asyncio
async def test_add_update_delete_item():
    item = "Test item"
    description = "Test description"
    seller_id = 1
    action = "sell"
    price = 100
    currency = "USD"
    message_id = 123

    # Mock Prisma and connect method
    prisma_mock = Mock()
    prisma_mock.connect.return_value = None

    # Patch Prisma class to return the mock object
    with patch("market.Prisma", return_value=prisma_mock):
        # Test add_item method
        prisma_mock.marketplace.create.return_value = Mock(id=1)
        added_item = await market.Market.add_item(item, description, seller_id, action, price, currency, message_id)
        assert added_item.id == 1

        # Test update_item method
        prisma_mock.marketplace.find_unique.return_value = Mock(actor=str(seller_id))
        prisma_mock.marketplace.update.return_value = Mock(id=1)
        updated_item = await market.Market.update_item(1, "Updated item", "Updated description", seller_id, action, price, currency, message_id)
        assert updated_item.id == 1

        # Test delete_item method
        prisma_mock.marketplace.find_unique.return_value = Mock(actor=str(seller_id))
        prisma_mock.marketplace.update.return_value = Mock(id=1)
        deleted_item = await market.Market.delete_item(1, seller_id)
        assert deleted_item.id == 1
        assert deleted_item.status == "sold"
        assert deleted_item.deleted_at is not None
