from datetime import datetime
from re import U
from sqlalchemy import DATETIME, Column, ForeignKey, Integer, String, Text, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, relationship
Base = declarative_base()

class Query(Base):
    __tablename__ = 'query'
    id = Column(Integer, primary_key=True)
    query = Column(String(255), nullable=False)
    query_results = relationship("QueryResult", cascade="all, delete", back_populates="query")

    def __init__(self, query:str):
        self.query = query

class QueryResult(Base):
    __tablename__ = 'queryresult'
    id = Column(Integer, primary_key=True)
    parent_query = Column(Integer, ForeignKey("query.id"), nullable=False)
    publisher = Column(String(255),)
    headline = Column(Text(), nullable=False)
    description = Column(Text())
    url = Column(Text())
    publish_date = Column(DateTime())
    sentiment = Column(Float)
    query = relationship("Query", back_populates="query_results")

    def __init__(self, query:str, publisher:str, headline:str, description:str, url:str, publish_date:datetime, sentiment:float):
        self.query = query
        self.publisher = publisher
        self.headline = headline
        self.description = description
        self.url = url
        self.publish_date = publish_date
        self.sentiment = sentiment