from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Asset(Base):
    __tablename__ = 'asset'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(length=10))
    rates: Mapped[list['Rate']] = relationship(back_populates='asset')


class Rate(Base):
    __tablename__ = 'rate'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey('asset.id', ondelete='CASCADE'),
        index=True,
    )
    timestamp: Mapped[int]
    value: Mapped[float]
    asset: Mapped['Asset'] = relationship(back_populates='rates')
