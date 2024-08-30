from peewee import *

db = SqliteDatabase("arxiv_posts.db")

class BaseModel(Model):
    class Meta:
        database = db

class ArxivUpdate(BaseModel):
    date  = DateField()
    topic = TextField()
    title = TextField()
    authors = TextField()
    abstract = TextField()
    link  = TextField()

class User(BaseModel):
    telegram_user_id = IntegerField(unique=True)

