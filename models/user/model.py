from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship
from extend.db import Base,LOCSESSION,ENGIN

import time
class AccountInputs(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(100), nullable=False, default='')
    password = Column(String(100), nullable=False, default='')
    type = Column(Integer, nullable=False, default=0)
    create_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    last_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    name=Column(String(30),nullable=False,default='管理员')
    posts = relationship("UserPosts", back_populates="user")
    status = Column(Integer, nullable=False, default=0) # 0:正常 1:禁用
    def __repr__(self):
        return f'<AccountInputs {self.account}>'
class UserPosts(Base):
    __tablename__ = 'user_posts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    isDisabledTitle=Column(Integer,nullable=False,default=0) #标题不能进行修改创建完了就不能修改 0:不可以修改 1:不可以修改
    title = Column(String(100), nullable=False, default='') # 最多100个字符
    content = Column(String(255), nullable=False, default='')  # 最多255个字符
    create_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    update_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    status = Column(Integer, nullable=False, default=0)
    isDeleted=Column(Integer,nullable=False,default=0) #是否删除 0:未删除 1:已删除
    isTop=Column(Integer,nullable=False,default=0) #是否置顶 0:不置顶 1:置顶
    # 创建与AccountInputs的反向引用，建立一对多关系
    user = relationship("AccountInputs", back_populates="posts")
    def __repr__(self):
        return f'<UserPosts {self.content[:10]}...>'  # 显示内容的前10个字符
