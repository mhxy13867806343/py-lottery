from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR,BINARY

import uuid
from extend.db import Base,LOCSESSION,ENGIN
from tool.classDb import UUIDType


class User(Base):
    __tablename__ = 'user'
    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    name = Column(String(30), nullable=False, default='')
    phone = Column(String(11), nullable=False, default='')
    count=Column(Integer,nullable=False,default=2)
    create_time=Column(Integer,nullable=False,default=lambda: int(time.time()))
    last_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    lottery_records = relationship("LotteryRecord", backref="user")
    paymentAccount=relationship("PaymentAccount",backref="user")
    def __repr__(self):
        return f'<User {self.name}>'
class PaymentAccount(Base):
    __tablename__ = 'payment_account'
    id = Column(CHAR(36), primary_key=True)
    user_id = Column(CHAR(36), ForeignKey('user.id'))
    account = Column(String(30), nullable=False, default='')
    create_time = Column(Integer, nullable=False)
    timestamp = Column(Integer, nullable=False)

class LotteryRecord(Base):
    __tablename__ = 'lottery_records'
    id = Column(CHAR(36), primary_key=True)
    l_name=Column(String(30),nullable=False,default='')
    user_id = Column(CHAR(36), ForeignKey('user.id'))
    create_time = Column(Integer, nullable=False)
    timestamp = Column(Integer, nullable=False)