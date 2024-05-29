from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship
from extend.db import Base,LOCSESSION,ENGIN

import time
class AccountInputs(Base): # 用户信息
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(100), nullable=False, default='')
    password = Column(String(100), nullable=False, default='')
    type = Column(Integer, nullable=False, default=0)
    create_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    last_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    email = Column(String(100), nullable=False, default='')
    name=Column(String(30),nullable=False,default='管理员')
    posts = relationship("UserPosts", back_populates="user")
    status = Column(Integer, nullable=False, default=0) # 0:正常 1:禁用
    share = relationship("Signature", backref="share")
    history = relationship("UserHistory", backref="history")
    def __repr__(self):
        return f'<AccountInputs {self.account}>'
class UserPosts(Base): # 用户动态
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
    share = relationship("ShareSignature", backref="user_posts")

    def __repr__(self):
        return f'<UserPosts {self.content[:10]}...>'  # 显示内容的前10个字符
class UserHistory(Base): # 用户浏览记录
    __tablename__ = 'user_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    url=Column(String(255),nullable=False,default='')
    isDeleted=Column(Integer,nullable=False,default=0) #是否删除 0:未删除 1:已删除
    create_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    last_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
class Signature(Base): # 用户签名
    __tablename__ ='signature'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    signature = Column(String(25), nullable=False, default='')  # 最多25个字符
    create_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    update_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    isDeleted = Column(Integer, nullable=False, default=0) # 是否删除 0:未删除 1:已删除
    user = relationship("AccountInputs", backref="signature")
    def __repr__(self):
        return f'<Signature {self.signature[:10]}...>'
class ShareSignature(Base): # 分享单条信息

    __tablename__ ='share_signature'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    type = Column(Integer, nullable=False, default=0)  # 分享类型
    share_id = Column(Integer, ForeignKey('user_posts.id'), nullable=False)  # 分享的动态id
    count = Column(Integer, nullable=False, default=0)  # 分享次数