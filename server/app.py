from flask import Flask, request, make_response, jsonify, abort
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource
from sqlalchemy import exc

from models import db, Scientist, Planet, Mission

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)


db.init_app(app)
api = Api(app)

class Scientists(Resource):

    def get(self):
        scientists = [scientist.to_dict() for scientist in Scientist.query.all()]
        response = make_response(
            scientists,
            200
        )
        return response
    
    def post(self):
        new_info = request.get_json()
        try:

            new_scientist = Scientist(
                name = new_info['name'],
                field_of_study = new_info['field_of_study'],
                avatar = new_info['avatar']
            )
        except ValueError as e:
            abort(422, e.args)
        except exc.IntegrityError as e:
            abort(422, e.args[0])

        db.session.add(new_scientist)
        db.session.commit()

        response = make_response(
            new_scientist.to_dict(),
            201
        )
        return response

class ScientistsByID(Resource):
    def get(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        
        if not scientist: 
            abort(404, description="Scientist not found.")
        
        response = make_response(
            scientist.to_dict(),
            200
        )
        return response
    
    def patch(self, id):
        updates = request.get_json()
        scientist = Scientist.query.filter(Scientist.id == id).first()

        if not scientist:
            abort(404, description="Scientist not found.")

        for key in updates:
            setattr(scientist, key, updates[key])

        db.session.add(scientist)
        db.session.commit()

        response = make_response(
            scientist.to_dict(),
            202
        )
        return response
    
    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()

        if not scientist:
            abort(404, description="Scientist not found.")

        for mission in scientist.missions:
            db.session.delete(mission)
            db.session.commit()

        db.session.delete(scientist)
        db.session.commit()

        response_body = ""

        response = make_response(
            response_body, 
            204
        )
        
        return response

class Planets(Resource):
    def get(self):
        planets = [planet.to_dict() for planet in Planet.query.all()]
        response = make_response(
            planets,
            200
        )
        return response

class Missions(Resource):
    def get(self):
        missions = [mission.to_dict() for mission in Mission.query.all()]
        response = make_response(
            missions,
            200
        )
        return response
    
    def post(self):
        new_info = request.get_json()

        new_mission = Mission(
            name = new_info['name'],
            scientist_id = new_info['scientist_id'],
            planet_id = new_info['planet_id']
        )

        db.session.add(new_mission)
        db.session.commit()

        planet = new_mission.planet.to_dict()

        response = make_response(
            planet,
            201
        )

        return response

api.add_resource(Scientists, '/scientists')
api.add_resource(ScientistsByID, '/scientists/<int:id>')
api.add_resource(Planets, '/planets')
api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
