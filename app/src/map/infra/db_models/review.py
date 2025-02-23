from utils.database import Base
from sqlalchemy import Column, Integer, ForeignKey, BigInteger, String
from sqlalchemy.orm import relationship

class Review(Base):
    __tablename__ = "review"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("Store.store_id"), nullable=False)
    rating = Column(Integer, nullable=False)
    review = Column(String(255), nullable=False)
    
    user = relationship("User", backref="review")
    store = relationship("Store", backref="review")