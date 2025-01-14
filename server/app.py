#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
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

class Scientists(Resource):

    def get(self):
        scientists = [scientist.to_dict(only=('id', 'name', 'field_of_study')) for scientist in Scientist.query.all()]
        return make_response(scientists, 200)
    
    def post(self):
        try:
            data = request.get_json()
            if not data.get('name'):
                raise ValueError('Name cannot be empty')
            if not data.get('field_of_study'):
                raise ValueError('Field of study cannot be empty')
            new_scientist = Scientist(
                name = data['name'],
                field_of_study = data['field_of_study']
            )
            db.session.add(new_scientist)
            db.session.commit()
            new_scientist_dict = new_scientist.to_dict()
            return make_response(new_scientist_dict, 201)
        except:
            response_body = {"errors": ["validation errors"]}
            return make_response(response_body, 400)

api.add_resource(Scientists, '/scientists')

class ScientistsByID(Resource):

    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            scientist_dict = scientist.to_dict()
            return make_response(scientist_dict, 200)
        else:
            return make_response({'error': 'Scientist not found'}, 404)
    
    def patch(self, id):
        try:
            scientist = Scientist.query.filter_by(id=id).first()
            data = request.get_json()

            if not data.get('name'):
                raise ValueError('Name cannot be empty')
            
            if not data.get('field_of_study'):
                raise ValueError('Field of study cannot be empty')
            
            if scientist:
                for attr, value, in data.items():
                    setattr(scientist, attr, value)

                db.session.add(scientist)
                db.session.commit()

                scientist_dict = scientist.to_dict()

                return make_response(scientist_dict, 202)
            else:
                return make_response({"error": "Scientist not found"}, 404)
        
        except ValueError:
            response_body = {"errors": ["validation errors"]}
            return make_response(response_body, 400)
        except Exception:
            response_body = {"errors": ["An unexpected error occurred"]}
            return make_response(response_body, 400)
    
    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            db.session.delete(scientist)
            db.session.commit()
            response_dict = {}
            return make_response(jsonify(response_dict), 204)
        else:
            return make_response({"error": "Scientist not found"}, 404)
        
class Planets(Resource):
    
    def get(self):
        planets = [planet.to_dict(only=('id', 'name', 'distance_from_earth', 'nearest_star')) for planet in Planet.query.all()]
        return make_response(planets, 200)

api.add_resource(Planets, '/planets')

class Missions(Resource):

    def post(self):
        try:
            data = request.get_json()
            if not data.get('name'):
                raise ValueError('Name cannot be empty')
            new_mission = Mission(
                name = data['name'],
                scientist_id = data['scientist_id'],
                planet_id = data['planet_id']
            )
            db.session.add(new_mission)
            db.session.commit()
            new_mission_dict = new_mission.to_dict()
            return make_response(new_mission_dict, 201)
        except:
            return make_response({'errors': ['validation errors']}, 400)

api.add_resource(Missions, '/missions')

    
    

api.add_resource(ScientistsByID, '/scientists/<int:id>')



if __name__ == '__main__':
    app.run(port=5555, debug=True)
