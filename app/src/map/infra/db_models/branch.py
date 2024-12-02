from utils.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Branch(Base):
    __tablename__ = "branch"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    city = Column(String)
    district = Column(String(50))
    address = Column(String(200))
    booking_link = Column(String(2000))
    brand_id = Column(Integer, ForeignKey("brand.id"))
    
    brand = relationship("Brand", back_populates="branch")