from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship
from extend.db import Base,LOCSESSION,ENGIN
class DictTypes(Base):
    __tablename__ = 'dict'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False, default='')
    key = Column(String(30), nullable=False, default='')
    value = Column(String(30), nullable=False, default='')
    create_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    status = Column(Integer, nullable=False, default=0)
    children = relationship("DictTypesChild", backref="dict")
    def __repr__(self):
        return f'<DictTypes {self.children}>'
class DictTypesChild(Base):
    __tablename__ = 'dict_child'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False, default='')
    key = Column(String(30), nullable=False, default='')
    value = Column(String(30), nullable=False, default='')
    create_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    parent_id = Column(Integer, ForeignKey('dict.id'))
    status = Column(Integer, nullable=False, default=0)
    def __repr__(self):
        return f'<DictTypesChild {self.parent_id}>'