from utils.database import Base
from sqlalchemy import Column, Integer, String, Text

class Brand(Base):
    __tablename__ = "brand"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(25))
    description = Column(Text)