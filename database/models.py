from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import ForeignKey, String, BIGINT, TIMESTAMP, DateTime, BOOLEAN

class Base(DeclarativeBase):
    pass


class Fires(Base):
    __tablename__ = 'fires'
    fire_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)

class Messages(Base):
    __tablename__ = 'messages'
    message_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('users.user_id'))
    email_id: Mapped[str] = mapped_column(String(225))
    date_send: Mapped[DateTime] = mapped_column(TIMESTAMP)
    message_text: Mapped[str] = mapped_column(String)
    
    #user = relationship("Users", back_populates="messages")
    
class Municipalities(Base):
    __tablename__ = 'municipalities'
    municipality_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    map_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    municipality_name: Mapped[str] = mapped_column(String(225))
    
    #subscriptions = relationship("Subscriptions", back_populates="map") 

class Subscriptions(Base):
    __tablename__ = 'subscriptions'
    subscription_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('users.user_id'))
    municipality_id: Mapped[str] = mapped_column(BIGINT, ForeignKey('municipalities.municipality_id'))
    date_subscribed: Mapped[DateTime] = mapped_column(TIMESTAMP)
    
    #user = relationship("Users", back_populates="subscriptions")
    #map = relationship("Municipalities", back_populates="subscriptions")

class Users(Base):
    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(255))
    joined_at: Mapped[DateTime] = mapped_column(TIMESTAMP)
    is_admin: Mapped[bool] = mapped_column(BOOLEAN)
    msg_type: Mapped[int] = mapped_column(BIGINT)


