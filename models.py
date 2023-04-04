from peewee import *
from peewee import VirtualField
import datetime
from flask_login import UserMixin
import re

db = PostgresqlDatabase(
    'youtube',
    host = 'localhost',
    port = 5433,
    user = 'youtube_user',
    password = 'qwe123'
)
db.connect()



class BaseModel(Model):
    class Meta:
        database = db



class MyUser(UserMixin, BaseModel):
    email = CharField (max_length=225, null = False, unique = True)
    username = CharField(max_length=225, null = False)
    password = CharField(max_length=225, null = False)
    age = IntegerField()



    
        

    def __repr__ (self):
        return self.email


class Post(BaseModel):
    author = ForeignKeyField (MyUser, on_delete='CASCADE')
    title = CharField(max_length=225, null = False)
    # video_url = CharField(max_length=225, null=False)
    video = BlobField()
    filename = CharField(max_length=225)
    description = TextField()
    date = DateTimeField(default = datetime.datetime.now)

class Favorite(BaseModel):
    user_id = ForeignKeyField (MyUser, on_delete='CASCADE')
    post_id = ForeignKeyField (Post, on_delete='CASCADE')

class Subscribes(BaseModel):
    user_id = ForeignKeyField (MyUser, on_delete='CASCADE')
    author_id = ForeignKeyField (Post, on_delete='CASCADE')





    





    def __repr__ (self):
        return self.title

db.create_tables([Subscribes])
