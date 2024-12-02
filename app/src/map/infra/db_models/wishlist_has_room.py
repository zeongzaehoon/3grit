from utils.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# class WishListHasRoom(Base):
#     __tablename__ = "wishlist_has_room"
    
#     id = Column(Integer, primary_key=True)
#     wishlist_id = Column(Integer, ForeignKey("wishlist.id"))
#     room_id = Column(Integer, ForeignKey("room.id"))
    
#     wishlist = relationship("Wishlist", back_populates="wishlist_has_room")
#     room = relationship("Room", back_populates="wishlist_has_room")