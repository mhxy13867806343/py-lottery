from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship
from extend.db import Base,LOCSESSION,ENGIN

import time
class Email(Base): # 用户信息
    __tablename__ = 'email'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(21), nullable=False,default='')
    email = Column(String(50), nullable=False, default='')
    content = Column(String(420), nullable=False, default='')
    create_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    last_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
