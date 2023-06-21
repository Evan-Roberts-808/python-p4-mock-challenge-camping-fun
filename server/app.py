#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def home():
    return ''


class Campers(Resource):

    def get(self):
        campers = [camper.to_dict(only=('id', 'name', 'age'))
                   for camper in Camper.query.all()]
        return campers, 200

    def post(self):
        try:
            data = request.get_json()
            new_camper = Camper(
                name=data.get('name'),
                age=data.get('age')
            )
            db.session.add(new_camper)
            db.session.commit()
            return new_camper.to_dict(), 201
        except:
            return {"error": "validation error"}, 400


api.add_resource(Campers, '/campers')


class CampersById(Resource):

    def get(self, id):
        try:
            campers = Camper.query.filter_by(id=id).first().to_dict()
            return campers, 200
        except:
            return {"error": "Camper not found"}, 404

    def patch(self, id):
        data = request.get_json()
        try:
            camper = Camper.query.filter_by(id=id).first()
        except:
            return {"error": "404: Camper not found"}
        try:
            for attr in data:
                setattr(camper, attr, data[attr])
            db.session.add(camper)
            db.session.commit()
            return camper.to_dict(), 202
        except:
            return {"error": "validation error"}, 400


api.add_resource(CampersById, '/campers/<int:id>')


class Activities(Resource):

    def get(self):
        activities = [activity.to_dict() for activity in Activity.query.all()]
        return activities, 200


api.add_resource(Activities, '/activities')


class ActivitiesById(Resource):

    def delete(self, id):
        try:
            Activity.query.filter_by(id=id).first().delete()
            db.session.commit()
            return ({}, 204)
        except:
            return {"error": "Activity not found"}, 404


api.add_resource(ActivitiesById, '/activities/<int:id>')


class Signups(Resource):
    def post(self):
        try:
            signup = Signup(
                time=request.json["time"],
                camper_id=request.json["camper_id"],
                activity_id=request.json["activity_id"]
            )

            db.session.add(signup)
            db.session.commit()

            return signup.activity.to_dict(), 201

        except:
            return {
                "error": "400: Validation error"
            }, 400


api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
