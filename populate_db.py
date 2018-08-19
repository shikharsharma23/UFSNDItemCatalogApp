''' Insert data to the database created
by database_setup.py (Create Part of Crud)'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///catalogitems.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# User 1


# Create dummy users
User1 = User(name="Shikhar Sharma", email="shikharcic23@gmail.com")
session.add(User1)
session.commit()

User2 = User(name="S S", email="shikharcic2@gmail.com")
session.add(User2)
session.commit()

# Category 1
category1 = Category(name="Soccer")
session.add(category1)
session.commit()

item1 = Item(
    user=User1,
    name="Soccer Cleats",
    description='''Soccer shoes, soccer cleats,
     soccer boots – whatever the name, most of
     the time a soccer shoe is a firm ground
     soccer shoe. Firm ground is the classic
      soccer shoe with cleats/studs designed to
      provide traction and stability on most
      natural grass, outdoor soccer fields.''',
    category=category1)
session.add(item1)
session.commit()

item2 = Item(
    user=User1,
    name="Shin Guards",
    description='''protective covering,
    usually of leather or plastic and often
     padded, for the shins and sometimes
     the knees''',
    category=category1)
session.add(item2)
session.commit()

item3 = Item(
    user=User1,
    name="Ball",
    description='''A football, soccer ball, or
     association football ball is the ball
     used in the sport of association football''',
    category=category1)
session.add(item3)
session.commit()

item4 = Item(
    user=User1,
    name="Jersey",
    description="Sweat proof, high quality clothing",
    category=category1)
session.add(item4)
session.commit()


# Category 2
category2 = Category(name="Cricket")
session.add(category2)
session.commit()

item1 = Item(
    user=User2,
    name="Bat",
    description="Used to hit the ball",
    category=category2)
session.add(item1)
session.commit()

item2 = Item(
    user=User2,
    name="Cricket Ball",
    description="Red color spherical ball made of leather",
    category=category2)
session.add(item2)
session.commit()

item3 = Item(
    user=User2,
    name="Elbow Pads",
    description="To guard elbow from damage",
    category=category2)
session.add(item3)
session.commit()

item4 = Item(
    user=User2,
    name="Helmet",
    description='''To protect head from damage.
     Blue color made from high quality material.''',
    category=category2)
session.add(item4)
session.commit()

item5 = Item(
    user=User2,
    name="Stumps",
    description="Three stumps with bails",
    category=category2)
session.add(item5)
session.commit()

item6 = Item(
    user=User2,
    name="cap",
    description="To prevent damage and distraction from harmful rays",
    category=category2)
session.add(item6)
session.commit()


# Category 3
category3 = Category(name="Hokcey")
session.add(category3)
session.commit()

item1 = Item(
    user=User1,
    name="Stick",
    description="Red color hockey stick",
    category=category3)
session.add(item1)
session.commit()

item2 = Item(
    user=User1,
    name="Hockey Ball",
    description="White color hockey ball",
    category=category3)
session.add(item2)
session.commit()

item3 = Item(
    user=User1,
    name="Clothing",
    description="High quality sports clothing",
    category=category3)
session.add(item3)
session.commit()

print("added catalog items!")
