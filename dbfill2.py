#!/usr/bin/env python
# coding: utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, User, Item

engine = create_engine('postgresql://catalog:catalog@127.0.0.1/catalog')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

item3 = Item(name="Snowboard", description="Best for any terrain and conditions. All-mountain snowboards perform anywhere on mountain-groomed runs, backcountry, even park and pipe.", category_id=5, user_id=3)
session.add(item3)
session.commit()

item4 = Item(name="Shinguards", description="Protect a player's front lower legs from injury when kicking or, more commonly, when kicked by other players.", category_id=1, user_id=1)
session.add(item4)
session.commit()

item5 = Item(name="Frisbee", description="Flying disc, generally made of plastic with aerodynamic curved edges to create air pocket for greater lift.", category_id=4, user_id=2)
session.add(item5)
session.commit()

item6 = Item(name="Bat", description="For elite composite performance in the Junior Big Barrel category, look no further than the 2017 Easton MAKO BEAST Junior Big Barrel Baseball Bat", category_id=3, user_id=3)
session.add(item6)
session.commit()

item7 = Item(name="Jersey", description="Fit for the field in energetic colors, this men's soccer jersey features sweat-wicking climalite fabric to keep you dry and comfortable.", category_id=1, user_id=1)
session.add(item7)
session.commit()

item8 = Item(name="Soccer Cleats", description="Two color dimpled synthetic upper. Strong and durable. Anti stretch lining. Two-color rubber outsole. Stitched at the front to the upper.", category_id=1, user_id=2)
session.add(item8)
session.commit()

print "added items!"
