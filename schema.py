#!/usr/bin/python

from sqlalchemy import (
    create_engine,
    Table,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    PickleType,
    MetaData,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


eng = create_engine("sqlite+pysqlite:///passes.db")
Base = declarative_base()
Base.metadata.bind = eng


class ISSPass(Base):
    __tablename__ = "isspass"
    id = Column("Id", Integer, primary_key=True)
    lat = Column("Lat", Float)
    lng = Column("Lon", Float)
    start_date = Column("StartDate", DateTime)
    path = Column("Path", PickleType)


if __name__=="__main__":
    Base.metadata.create_all()
else:
    Session = sessionmaker(bind=eng)
    db = Session()
