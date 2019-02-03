import os
import sys
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy import String, LargeBinary, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class UserInfo(Base):
    __tablename__ = 'user_info'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    email = Column(String(80), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        return {
            'name': self.name,
            'email': self.email,
            'id': self.id,
            'picture' : self.picture
        }


class Catalog(Base):
    __tablename__ = 'catalog'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_info.id'))
    user = relationship(UserInfo)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id
        }


class CatalogItem(Base):
    __tablename__ = 'catalog_item'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    catalog_id = Column(Integer, ForeignKey('catalog.id'))
    catalog = relationship(Catalog)
    user_id = Column(Integer, ForeignKey('user_info.id'))
    user = relationship(UserInfo)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'catalog_id': self.catalog_id
        }


class CatalogItemType(Base):
    __tablename__ = 'catalog_item_type'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    catalog_item_id = Column(Integer, ForeignKey('catalog_item.id'))
    catalog_item = relationship(CatalogItem)
    image = Column(LargeBinary)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'image': self.image
        }


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
