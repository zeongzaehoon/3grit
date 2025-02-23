from utils.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

class SecondaryCategory(Base):
    __tablename__ = "SecondaryCategory"
    
    subcategory_id = Column(Integer, primary_key=True, nullable=False)
    category_id = Column(Integer, ForeignKey("Category.category_id"), nullable=False)
    name = Column(String(25), nullable=False)
    created_date = Column(DateTime, nullable=False)
    updated_date = Column(DateTime, nullable=False)
    
    category = relationship("Category", backref="subcategories")