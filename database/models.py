from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import ForeignKey, String, BIGINT, TIMESTAMP, DateTime, BOOLEAN, FLOAT, INTEGER

class Base(DeclarativeBase):
    pass



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



class Fires(Base):
    __tablename__ = 'fires'
    fire_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    date_detect: Mapped[DateTime] = mapped_column(TIMESTAMP)
    date_terminate: Mapped[DateTime] = mapped_column(TIMESTAMP, nullable=True)
    date_actual: Mapped[DateTime] = mapped_column(TIMESTAMP)
    date_import: Mapped[DateTime] = mapped_column(TIMESTAMP)
    fire_ext_id: Mapped[str] = mapped_column(String(255))
    fire_num: Mapped[int] = mapped_column(INTEGER)
    fire_zone: Mapped[str] = mapped_column(String(255))
    map_id: Mapped[str] = mapped_column(String(255))
    region: Mapped[str] = mapped_column(String(255))
    forestry_id: Mapped[int] = mapped_column(INTEGER)
    forestry_name: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(255))
    azimuth: Mapped[int] = mapped_column(INTEGER)
    distance: Mapped[int] = mapped_column(INTEGER)
    fire_status: Mapped[str] = mapped_column(String(255))
    forces_aps: Mapped[int] = mapped_column(INTEGER)
    forces_lps: Mapped[int] = mapped_column(INTEGER)
    forces_: Mapped[int] = mapped_column(INTEGER)
    forces_rent: Mapped[int] = mapped_column(INTEGER)
    forces_mchs: Mapped[int] = mapped_column(INTEGER)
    fire_area: Mapped[float] = mapped_column(FLOAT)
    ext_log: Mapped[int] = mapped_column(INTEGER)
    email_id: Mapped[str] = mapped_column(String(255))
    
    
    
    
    
    
    
    
    
    
    
    
