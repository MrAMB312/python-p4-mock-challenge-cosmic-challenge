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


@app.route('/')
def home():
    return ''

@app.route('/scientists', methods=["GET", "POST"])
def scientists():
    if request.method == "GET":
        
        scientists = [scientist.to_dict(only=('id', 'name', 'field_of_study')) for scientist in Scientist.query.all()]
        response = make_response(scientists, 200)
        return response
    
    elif request.method == "POST":
        
        data = request.get_json()

        name = data['name']
        field_of_study = data['field_of_study']

        if not name or not field_of_study:
            return { 'errors': ['validation errors']}, 400
        
        new_scientist = Scientist(
            name=name,
            field_of_study=field_of_study
        )

        db.session.add(new_scientist)
        db.session.commit()

        response = make_response(new_scientist.to_dict(), 201)
        return response

@app.route('/scientists/<int:id>', methods=["GET", "PATCH", "DELETE"])
def scientist_by_id(id):
    if request.method == "GET":
        
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return { 'error': 'Scientist not found.' }, 404
        
        response = make_response(scientist.to_dict(), 200)
        return response
    
    elif request.method == "PATCH":
        
        data = request.get_json()
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return { 'error': ['Scientist not found.'] }, 404
        
        name = data['name']
        field_of_study = data['field_of_study']

        if not name or not field_of_study:
            return { 'errors': ['validation errors'] }, 400
        
        for attr in data:
            setattr(scientist, attr, data[attr])

        db.session.add(scientist)
        db.session.commit()

        response = make_response(scientist.to_dict(), 202)
        return response

    elif request.method == "DELETE":
        
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return jsonify({ 'error': 'Scientist not found' }), 404
        
        db.session.delete(scientist)
        db.session.commit()

        response = make_response(jsonify({}), 204)
        return response

@app.route('/planets', methods=["GET"])
def planets():
    
    planets = [planet.to_dict(only=('id', 'name', 'distance_from_earth', 'nearest_star')) for planet in Planet.query.all()]
    response = make_response(planets, 200)
    return response

@app.route('/missions', methods=["POST"])
def missions():
    
    data = request.get_json()

    name = data['name']
    scientist_id = data['scientist_id']
    planet_id = data['planet_id']

    if not name or not scientist_id or not planet_id:
        return { 'errors': ['validation errors'] }, 400
    
    new_mission = Mission(
        name=name,
        scientist_id=scientist_id,
        planet_id=planet_id
    )

    db.session.add(new_mission)
    db.session.commit()

    response = make_response(new_mission.to_dict(), 201)
    return response

if __name__ == '__main__':
    app.run(port=5555, debug=True)
