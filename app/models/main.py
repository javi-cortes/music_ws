from app.extensions import mongo


class Channel(mongo.Document):
    name = mongo.StringField()

    meta = {
        'indexes': ['name']
    }


class Performer(mongo.Document):
    name = mongo.StringField()

    meta = {
        'indexes': ['name']
    }


class Song(mongo.Document):
    title     = mongo.StringField()
    performer = mongo.StringField()

    meta = {
        'indexes': ['title', 'performer']
    }


class Play(mongo.Document):
    title     = mongo.StringField()
    channel   = mongo.StringField()
    performer = mongo.StringField()
    start     = mongo.DateTimeField()
    end       = mongo.DateTimeField()

    meta = {
        'indexes': ['title', 'channel']
    }

