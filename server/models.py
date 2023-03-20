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

    serialize_rules = ('-scientist.missions', '-planet.missions')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)
    
    def __repr__(self):
        return f'<Name: {self.name} Scientist ID: {self.scientist_id}, Planet: {self.planet_id}>'
    

class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    serialize_rules = ('-missions.scientist',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    field_of_study = db.Column(db.String, nullable=False)
    avatar = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    missions = db.relationship('Mission', backref='scientist')
    planets = association_proxy('missions', 'planet', creator=lambda pl: Mission(planet=pl))

    @validates('name')
    def validate_name(self, key, name):
        scientists = [scientist.name for scientist in Scientist.query.all()]
        
        if not name or len(name) == 0:
            raise ValueError("Scientist must have a name.")
        elif name in scientists:
            raise ValueError("Scientist already exists in database.")
        
        return name
    
    @validates('field_of_study')
    def validate_name(self, key, field):
        if not field or len(field) == 0:
            raise ValueError("Scientist must have a field of study.")
        return field
    
    def __repr__(self):
        return f'<Name: {self.name}, Field of Study: {self.field_of_study}>'


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    serialize_rules = ('-missions.planet',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.String)
    nearest_star = db.Column(db.String)
    image = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    missions = db.relationship('Mission', backref='planet')
    scientists = association_proxy('missions', 'scientist', creator=lambda sc: Mission(scientist=sc))

    def __repr__(self):
        return f'<Name: {self.name}, Distance from Earth: {self.distance_from_earth}, Nearest Star: {self.nearest_star}>'