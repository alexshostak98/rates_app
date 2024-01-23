import asyncio

from rates_app.constants import RequiredAssets
from rates_app.database.engine import async_session
from rates_app.database.models import Asset


async def fill_asset_database():
    async with async_session() as session:
        assets = [Asset(name=asset) for asset in RequiredAssets]
        session.add_all(assets)
        await session.commit()


if __name__ == '__main__':
    asyncio.run(fill_asset_database())
