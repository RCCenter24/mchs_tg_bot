from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import ForeignKey, String, BIGINT, TIMESTAMP, DateTime, func, Text

class Base(DeclarativeBase):
    pass

class Messages(Base):
    __tablename__ = 'messages'
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('users.user_id'))
    message_id: Mapped[str] = mapped_column(String(50))
    message_text: Mapped[str] = mapped_column(String(50))
    date_of_sending: Mapped[DateTime] = mapped_column(TIMESTAMP)
    
    #user = relationship("Users", back_populates="messages")
    
class Municipalities(Base):
    __tablename__ = 'municipalities'
    map_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    municipality_name: Mapped[str] = mapped_column(String(100))
    
    #subscriptions = relationship("Subscriptions", back_populates="map") 

class Subscriptions(Base):
    __tablename__ = 'subscriptions'
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('users.user_id'))
    map_id: Mapped[str] = mapped_column(String(10), ForeignKey('municipalities.map_id'))
    municipality_name: Mapped[str] = mapped_column(String(50))
    subscribed_at: Mapped[DateTime] = mapped_column(TIMESTAMP)
    
    #user = relationship("Users", back_populates="subscriptions")
    #map = relationship("Municipalities", back_populates="subscriptions")

class Users(Base):
    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_name: Mapped[str] = mapped_column(String(60))
    last_name: Mapped[str] = mapped_column(String(60))
    username: Mapped[str] = mapped_column(String(60))
    joined_at: Mapped[DateTime] = mapped_column(TIMESTAMP)
