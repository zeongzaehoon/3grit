from utils.database import Base
from sqlalchemy import Column, Integer, String, DateTime

class Category(Base):
    __tablename__ = "Category"
    
    category_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(25), nullable=False)
    created_date = Column(DateTime, nullable=False)
    updated_date = Column(DateTime, nullable=False)
