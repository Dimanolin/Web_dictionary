from sqlalchemy import Column, Integer, String
from .database import Base

class DictionaryWord(Base):
    __tablename__ = "dictionary"

    id = Column(Integer, primary_key = True, index = True)
    word = Column(String, index = True)
    definition = Column(String)