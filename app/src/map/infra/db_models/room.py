from utils.database import Base
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

class Room(Base):
    __tablename__ = "room"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    genre = Column(String(50))
    difficulty = Column(Integer)
    fear_degree = Column(Integer)
    activity = Column(String(50))
    recommended_numb = Column(Integer)
    time_duration = Column(Integer)
    image_url = Column(String(1000))
    branch_id = Column(Integer, ForeignKey("branch.id"))
    
    # branch = relationship("Branch", back_populates="room")