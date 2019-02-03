from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *

from database_setup import UserInfo, Catalog, CatalogItem, Base, CatalogItemType

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

metadata = MetaData()

DBSession = sessionmaker(bind=engine)

session = DBSession()

metadata.drop_all(engine)


# for x in range(100):
#     catalog1 = Catalog(name="Test_Cat"+str(x))
#     session.add(catalog1)
#     session.commit()
#     for y in range(3):
#         menuItem1 = CatalogItem(name="Test_Cat_Item"+str(x)+str(y), catalog=catalog1)
#         session.add(menuItem1)
#         session.commit()
#         for z in range(2):
#             menuItemType = CatalogItemType(name="Test_Catalog_Item_Type"+str(x)+str(y)+str(z), catalog_item=menuItem1)
#             session.add(menuItemType)
#             session.commit()

# session.commit()

# Menu for Golf
# catalog1 = Catalog(name="Tennis")

# session.add(catalog1)
# session.commit()

# menuItem2 = CatalogItem(name="Tennis Ball", description='''A Tennis Ball is a special ball designed to be used in the game of Tennis.''', catalog=catalog1)

# session.add(menuItem2)
# session.commit()

#menu type for golf balls
# menuItemType1 = CatalogItemType(name="Recreational Golf Ball", description='''Recerational balls are made of two layers, with the cover firmer than the core. Generally used by low swing speed player and who tend to loose golf balls easily.''',
#              price="$5.50" , catalog_item=menuItem2)

# session.add(menuItemType1)
# session.commit()

# menuItemType2 = CatalogItemType(name="Advanced Golf Ball", description='''Advanced balls are made of multiple layers (three or more), with a soft cover and firm core. They induce a greater amount of spin from lofted shots (wedges especially), as well as a sensation of softness in the hands in short-range shots''',
#              price="$10.50" , catalog_item=menuItem2)

# session.add(menuItemType2)
# session.commit()

# Menu for Golf
# menuItem1 = CatalogItem(name="Tennis Raqucet", description='''A Tennis Raqucet is used hit a Tennis ball. The raqucet is composed of net with a grip/handle'''
#                     , catalog=catalog1)

# session.add(menuItem1)
# session.commit()

# #menu type for golf clubs
# menuItemType11 = CatalogItemType(name="Woods", description='''Woods are used for tee-shorts or long distance fairways.''',
#              price="$15.50" , catalog_item=menuItem1)

# session.add(menuItemType11)
# session.commit()

# menuItemType12 = CatalogItemType(name="Irons", description='''Irons are ease of access and used for variety of shots''',
#              price="$10.50" , catalog_item=menuItem1)

# session.add(menuItemType12)
# session.commit()

# menuItemType13 = CatalogItemType(name="Wedges", description='''Wedges are subclass to irons and can be used for short distance, high altitude shots''',
#              price="$12.50" , catalog_item=menuItem1)

# session.add(menuItemType13)
# session.commit()

# menuItemType14 = CatalogItemType(name="Hybrid", description='''Hybrid are combination of woods and irons''',
#              price="$12.50" , catalog_item=menuItem1)

# session.add(menuItemType14)
# session.commit()

# menuItemType15 = CatalogItemType(name="Putter", description='''Putters are clubs with less than 10 degree loft, used to roll ball in the grass''',
#              price="$20.50" , catalog_item=menuItem1)

# session.add(menuItemType15)
# session.commit()

# menuItemType16 = CatalogItemType(name="Chipper", description='''Chipper is like putter with more loffted face''',
#              price="$20.50" , catalog_item=menuItem1)

# session.add(menuItemType15)
# session.commit()




print("added menu items!")