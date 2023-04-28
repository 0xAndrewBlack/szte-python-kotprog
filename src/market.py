import logging

from prisma import Prisma
from datetime import datetime

logger = logging.getLogger(str(__name__).upper())


class Market:
    @staticmethod
    async def get_item(item_id):
        prisma = Prisma()
        await prisma.connect()

        item = await prisma.marketplace.find_unique(where={"id": item_id})

        logger.info(f"Item queried: {item.id}")

        return item

    @staticmethod
    async def paginate_items(page=1, limit=10):
        prisma = Prisma()
        await prisma.connect()

        items = await prisma.marketplace.find_many(skip=(page - 1) * limit, take=limit, where={
            "status": "available"
        })

        logger.info(f"Items queried: {len(items)}")

        return items

    @staticmethod
    async def add_item(item, description, seller_id, action, price, currency, message_id):
        prisma = Prisma()
        await prisma.connect()

        item = await prisma.marketplace.create(
            data={
                "actor": str(seller_id),
                "name": item,
                "description": description,
                "price": price,
                "listing": str(action).upper(),
                "currency": currency,
                "message_id": str(message_id),
            }
        )

        logger.info(f"Item added {item.id}")

        return item

    @staticmethod
    async def update_item(item_id, item, status, description, seller_id, action, price, currency):
        prisma = Prisma()
        await prisma.connect()

        query = await prisma.marketplace.find_unique(where={"id": item_id})

        if query.actor != str(seller_id):
            return None

        item = await prisma.marketplace.update(
            where={
                "id": int(item_id),
            },
            data={
                "name": item,
                "description": description,
                "price": price,
                "listing": str(action).upper(),
                "currency": currency,
                "status": str(status).lower(),
            }
        )

        logger.info(f"Item updated: {item.id}")

        return item

    @staticmethod
    async def delete_item(item_id, seller_id):
        prisma = Prisma()
        await prisma.connect()

        query = await prisma.marketplace.find_unique(where={"id": item_id})
        
        if query.actor != str(seller_id):
            return None

        item = await prisma.marketplace.update(
            where={
                "id": int(item_id),
            },
            data={
                "status": "sold",
                "deleted_at": datetime.now(),
            }
        )

        logger.info(f"Item deleted: {item.id}")

        return item
