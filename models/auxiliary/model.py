from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship
from extend.db import Base,LOCSESSION,ENGIN

import time
class Email(Base):
    __tablename__ = 'email'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(21), nullable=False, default='')
    email = Column(String(50), nullable=False, default='')
    content = Column(String(420), nullable=False, default='')
    create_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    last_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    email_id = Column(String(36), nullable=False, default="")
    status = Column(Integer, nullable=False, default=0)  # 0:正常 1:禁用
    copies = relationship("CopyEmail", backref="origin")

class CopyEmail(Base):
    __tablename__ = 'copy_email'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(21), nullable=False, default='')
    email = Column(String(50), nullable=False, default='')
    content = Column(String(420), nullable=False, default='')
    create_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    last_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    email_id = Column(Integer, ForeignKey('email.id'), nullable=False)
    status = Column(Integer, nullable=False, default=0)  # 0:正常 1:禁用
