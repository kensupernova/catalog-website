from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Base, Category, User, Item, get_engine, get_DBSession

session = get_DBSession()

## clear out the database
session.query(User).delete()
session.query(Category).delete()
session.query(Item).delete()

# Create dummy user
User1 = User(name="ZGH", email="ZGH@udacity.com")
session.add(User1)
session.commit()

# Create a cagetory
###############
cate1 = Category(user_id=User1.id, name="NHL", description="National Hockey Leagure",)

session.add(cate1)
session.commit()


item1 = Item(user_id=User1.id, name="Boston Bruins", description="Atlantic",
                     category=cate1)
session.add(item1)
session.commit()

item2 = Item(user_id=User1.id, name="Anaheim Ducks", description="Pacific",
                     category=cate1)
session.add(item2)
session.commit()

item3 = Item(user_id=User1.id, name="Chicago Blackhawks", description="Central",
                     category=cate1)
session.add(item3)
session.commit()


###############
cate2 = Category(user_id=User1.id, name="NBA", description="National Basketball Association       ")
session.add(cate2)
session.commit()

item1 = Item(user_id=User1.id, name="Boston Celtics", description="Atlantic",
                     category=cate2)
session.add(item1)
session.commit()

item2 = Item(user_id=User1.id, name="Golden State Warriors", description="Pacific",
                     category=cate2)
session.add(item2)
session.commit()

item3 = Item(user_id=User1.id, name="Chicago Bulls", description="Central",
                     category=cate2)
session.add(item3)
session.commit()

########################
cate3 = Category(user_id=User1.id, name="NFL", description="National Football League")
session.add(cate3)
session.commit()

item1 = Item(user_id=User1.id, name="Buffalo Bills", description="East",
                     category=cate3)
session.add(item1)
session.commit()

item2 = Item(user_id=User1.id, name="Baltimore Ravens", description="North",
                     category=cate3)
session.add(item2)
session.commit()

item3 = Item(user_id=User1.id, name="Houston Texans", description="South",
                     category=cate3)
session.add(item3)
session.commit()

item4 = Item(user_id=User1.id, name="Denver Broncos", description="West",
                     category=cate3)
session.add(item4)
session.commit()

print "category and item are initialized with some data!"

items = session.query(Item).all()

for item in items:
    print item.created
