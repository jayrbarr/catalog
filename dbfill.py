#!/usr/bin/env python
# coding: utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, User, Item

engine = create_engine('postgresql://catalog:catalog@127.0.0.1/catalog')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

cat1 = Category(name="Soccer")
session.add(cat1)
session.commit()

cat2 = Category(name="Basketball")
session.add(cat2)
session.commit()

cat3 = Category(name="Baseball")
session.add(cat3)
session.commit()

cat4 = Category(name="Frisbee")
session.add(cat4)
session.commit()

cat5 = Category(name="Snowboarding")
session.add(cat5)
session.commit()

cat6 = Category(name="Rock Climbing")
session.add(cat6)
session.commit()

cat7 = Category(name="Foosball")
session.add(cat7)
session.commit()

cat8 = Category(name="Skating")
session.add(cat8)
session.commit()

cat9 = Category(name="Hockey")
session.add(cat9)
session.commit()

print "added categories!"

user1 = User(name="Admin", email="admin@example.com")
session.add(user1)
session.commit()

user2 = User(name="Jack", email="jack@example.com")
session.add(user2)
session.commit()

user3 = User(name="Jill", email="jill@example.com")
session.add(user3)
session.commit()

print "added users!"

item1 = Item(name="Stick", description="Long handled, two-handed stick with flattened, curved end for controlling puck. Usually made from wood, fiberglass or composite materials.", category_id=9, user_id=1)
session.add(item1)
session.commit()

item2 = Item(name="Goggles", description="Worn on the eyes to protect from elements and help with vision.", category_id=5, user_id=2)
session.add(item2)
session.commit()

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
