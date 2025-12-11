from sqlalchemy import Column, Integer, String, Float, Date
from .db import Base

class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    trade_date = Column(Date, index=True)
    close = Column(Float)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    volume = Column(Float)