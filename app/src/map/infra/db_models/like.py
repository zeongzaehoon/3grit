from utils.database import Base
from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship

class LikeButton(Base):
    __tablename__ = "likeButton"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("Store.store_id"), nullable=False)
    likeButton = Column(Boolean, nullable=False)
    
    user = relationship("User", backref="likeButton")
    store = relationship("Store", backref="likeButton")