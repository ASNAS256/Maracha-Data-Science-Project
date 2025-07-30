from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ExtractedData(Base):
    __tablename__ = 'extracted_data'

    id = Column(Integer, primary_key=True)
    filename = Column(String(200))
    extracted_text = Column(Text)
