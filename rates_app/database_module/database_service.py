from datetime import datetime, timedelta

from sqlalchemy import select

from rates_app.database_module.engine import async_session
from rates_app.database_module.models import Asset as AssetORM
from rates_app.database_module.models import Rate as RateORM
from rates_app.utils import get_unix_timestamp
from rates_app.websocket_module.websocket_types import Asset as AssetModel
from rates_app.websocket_module.websocket_types import Rate as RateModel


class DBService:
    cached_assets = None

    @classmethod
    async def get_assets(cls) -> list[AssetModel]:
        if cls.cached_assets:
            return cls.cached_assets
        assets_q = select(AssetORM)
        async with async_session() as session:
            raw_result = await session.execute(assets_q)
            orm_result = raw_result.scalars().all()
        result = [AssetModel.model_validate(asset) for asset in orm_result]
        cls.cached_assets = result
        return result

    async def get_rates_history_by_asset_id_for_time_range(
        self,
        asset_id: int,
        time_range: timedelta,
    ) -> list[RateModel]:
        unix_timestamp = get_unix_timestamp(datetime.utcnow() - time_range)
        rates_history_q = (
            select(
                RateORM.asset_id,
                RateORM.timestamp,
                RateORM.value,
                AssetORM.name.label('asset'),
            )
            .join(AssetORM, AssetORM.id == RateORM.asset_id)
            .where(RateORM.asset_id == asset_id)
            .where(RateORM.timestamp > unix_timestamp)
        )
        async with async_session() as session:
            raw_result = await session.execute(rates_history_q)
            orm_result = raw_result.mappings().all()
        return [RateModel.model_validate(rate) for rate in orm_result]

    async def create_rates_point(self, rates_point: list[RateModel]) -> None:
        async with async_session() as session:
            rates = [
                RateORM(**rate.model_dump(exclude={'asset'}))
                for rate in rates_point
            ]
            session.add_all(rates)
            await session.commit()
