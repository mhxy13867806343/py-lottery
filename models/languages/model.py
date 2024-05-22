from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship
from extend.db import Base,LOCSESSION,ENGIN


class Language(Base):
    __tablename__ = 'languages'
    id:int=Column(Integer,primary_key=True,autoincrement=True)
    text:str=Column(String(80),nullable=False,default="")
    href:str=Column(String(100),nullable=False,default="")
    def __repr__(self):
        return f"{self.id}-{self.text}-{self.href}"
    def save(self,languages:str="")->dict:
        pass
    def select(self,char:str="")->str:
        pass
    def delete(self,languages:str="")->dict:
        pass
    def update(self,languages:str="")->dict:
        pass
    def pop(self):
        pass