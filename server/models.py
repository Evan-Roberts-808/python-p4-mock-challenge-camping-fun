from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
  "ix": "ix_%(column_0_label)s",
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)
    
    signups = db.relationship("Signup", cascade="all,delete", backref= "activity")

    serialize_only = ("id", "name", "difficulty")
    
    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'

class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)
    
    signups = db.relationship("Signup", backref= "camper")
    
    activities = association_proxy("signups", "activity")

    serialize_rules = ("-signups.camper",)
    
    @validates('name')
    def validate_name(self, key, name):
        print('Inside the name validation')
        if not name or len(name) < 1: 
            raise ValueError("Name must exist")

        return name
    
    @validates('age')
    def validate_age(self, key, age):
        print('Inside the age validation')
        if not 8 <= age <= 18: 
            print('Invalid!!')
            raise ValueError("Age must be 8 to 18")
        
        return age
    
    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'
    
class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    
    camper_id = db.Column(db.Integer, db.ForeignKey("campers.id"))
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"))
    
    serialize_rules = ("-camper.signups", "-activity.signups")
    
    @validates('time')
    def validate_time(self, key, time):
        
        if not 0 <= time <= 23:
            raise ValueError("Time must be within limits")
        return time

    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need. 