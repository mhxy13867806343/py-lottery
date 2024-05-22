import requests
from typing import List,Dict
from sqlalchemy.orm import Session
from extend.db import LOCSESSION,Base,ENGIN
from pyquery import PyQuery as pq
from tool.dbHeaders import outerUserAgentHeadersX64
from .model import Language
url:str="https://github.com/trending"
session=LOCSESSION()
Base.metadata.create_all(bind=ENGIN)
def writer():
    resource = requests.get(url, headers=outerUserAgentHeadersX64)
    content = resource.content
    doc = pq(content)
    languageMmenuitems = doc.find("#languages-menuitems")
    selectMenuItem = languageMmenuitems.find("a.select-menu-item")
    for item in selectMenuItem.items():
        href = item.attr('href')
        text = item.find(".select-menu-item-text").text()
        try:
            session.add(Language(text=text, href=href))
            session.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            session.rollback()

def getListAll(db:Session,q:str=""):
    if not q or len(q)==0:
        return db.query(Language).all()
    return db.query(Language).filter(Language.text.like(f"%{q}%")).all()