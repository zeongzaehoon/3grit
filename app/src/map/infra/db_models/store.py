from utils.database import Base
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship



class Store(Base):
    __tablename__ = "Store"
    
    store_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    category_id = Column(Integer, ForeignKey("Category.category_id"), nullable=True)
    subcategory_id = Column(Integer, ForeignKey("SecondaryCategory.subcategory_id"), nullable=True)
    name = Column(String(100), nullable=False)
    mapx = Column(Float, nullable=False)
    mapy = Column(Float, nullable=False)
    address_name = Column(String(100), nullable=False)
    created_date = Column(DateTime(timezone=True), nullable=False)
    updated_date = Column(DateTime(timezone=True), nullable=False)
    kakao_map_id = Column(Integer, nullable=False)

    category = relationship("Category", backref="store")
    subcategory = relationship("SecondaryCategory", backref="store")