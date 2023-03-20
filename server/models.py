from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, default = db.func.now(), onupdate = db.func.now())
    
    @validates('name')
    def validates_name(self, key, value):
        if not value:
            raise ValueError("Name must be provided.")
        return value
    
    @validates('scientist_id')
    def validates_scientist_id(self, key, value):
        scientists = Scientist.query.all()
        ids = [scientist.id for scientist in scientists]
        if not value:
            raise ValueError("Scientist must be provided.")
        elif not value in ids:
            raise ValueError("Scientist does not exist.")
        return value
    
    @validates('planet_id')
    def validates_scientist_id(self, key, value):
        planets = Planet.query.all()
        ids = [planet.id for planet in planets]
        if not value:
            raise ValueError("Planet must be provided.")
        elif not value in ids:
            raise ValueError("Planet does not exist.")
        return value
    
    def __repr__(self):
        return f'<Name: {self.name}, Scientist ID: {self.scientist_id}, Planet ID: {self.planet_id}'
    
class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    field_of_study = db.Column(db.String, nullable=False)
    avatar = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, default = db.func.now(), onupdate = db.func.now())

    missions = db.relationship('Mission', backref='scientist')
    planets = association_proxy('missions', 'planet')

    @validates('name')
    def validates_name(self, key, value):
        scientists = Scientist.query.all()
        names = [scientist.name for scientist in scientists]
        if not value:
            raise ValueError("Name must be provided.")
        elif value in names:
            raise ValueError("Scientist already exists in database.")
        return value
    
    @validates('field_of_study')
    def validates_field_of_study(self, key, value):
        if not value:
            raise ValueError("Field of study must be provided.")
        return value

class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.String)
    nearest_star = db.Column(db.String)
    image = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, default = db.func.now(), onupdate = db.func.now())

    missions = db.relationship('Mission', backref='planet')
    scientists = association_proxy('missions', 'scientist')
    