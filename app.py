"""
API for the STReserve application.

:Author:     Maded Batara III
:Version:    v20170508
"""

import csv
import datetime
import os
import re

from flask import Flask
from flask import jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_heroku import Heroku
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)

if 'DYNO' in os.environ:
    import psycopg2
    hr = Heroku(app)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

############
## SCHEMA ##
############

class Chemical(db.Model):
    __tablename__ = 'chemicals'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    state = db.Column(db.Boolean)
    qty = db.Column(db.Integer)

    def __repr__(self):
        return "<Chemical '{0}', {1}{2}>".format(
            self.name, self.qty, "g" if self.state else "mL")

class Equipment(db.Model):
    __tablename__ = 'equipment'

    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String)
    is_consumable = db.Column(db.Boolean)
    qty = db.Column(db.Integer)

    def __repr__(self):
        return "<Equipment '{0}'{1}, qty {2}>".format(
            self.name, " (consumable)" if self.is_consumable else "", self.qty)

class ChemicalLog(db.Model):
    __tablename__ = 'chemical_log'

    id = db.Column(db.Integer, primary_key=True)
    chemical_id = db.Column(db.Integer, db.ForeignKey("chemicals.id"))
    chemical = db.relationship("Chemical", backref="logs")
    group_code = db.Column(db.Integer)
    qty = db.Column(db.Integer)
    date_procured = db.Column(db.DateTime)

class EquipmentLog(db.Model):
    __tablename__ = 'equipment_log'

    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"))
    equipment = db.relationship("Equipment", backref="logs")
    group_code = db.Column(db.Integer)  
    qty = db.Column(db.Integer)
    date_procured = db.Column(db.DateTime)
    date_return = db.Column(db.DateTime)

class ChemicalSchema(ma.ModelSchema):
    class Meta:
        model = Chemical
    logs = ma.List(ma.HyperlinkRelated('get_chemical_log_by_id'))

class EquipmentSchema(ma.ModelSchema):
    class Meta:
        model = Equipment
    logs = ma.List(ma.HyperlinkRelated('get_equipment_log_by_id'))

class ChemicalLogSchema(ma.ModelSchema):
    class Meta:
        model = ChemicalLog
    chemical = ma.HyperlinkRelated('get_chemical_by_id')

class EquipmentLogSchema(ma.ModelSchema):
    class Meta:
        model = EquipmentLog
    equipment = ma.HyperlinkRelated('get_equipment_by_id')

chemicals = []
chemicals.append(Chemical(name="Sodium chloride", state=True, qty=200))
chemicals.append(Chemical(name="Water", state=False, qty=100))

equipment = []
with open("equipment.csv") as equipment_csv:
    equipment_list = csv.reader(equipment_csv)
    for row in equipment_list:
        if row[-1] == "LOCATION":
            continue
        is_consumable = True if row[1].lower() in [
            "consumable", "many", "assorted"] else False
        qty = -1 if is_consumable else int(re.sub('[^0-9]', '', row[1]))
        equipment.append(Equipment(name=row[0], 
            is_consumable=is_consumable, qty=qty))

if 'DYNO' not in os.environ:
    db.reflect()
    db.drop_all()
db.create_all()
if 'DYNO' not in os.environ:
    for chemical in chemicals:
        db.session.add(chemical)
    for equip in equipment:
        db.session.add(equip)
    db.session.commit()
 
chemical_schema = ChemicalSchema()
equipment_schema = EquipmentSchema()
chemical_log_schema = ChemicalLogSchema()
equipment_log_schema = EquipmentLogSchema()

#########
## APP ##
#########

VERSION = "20170508"

@app.route("/")
def home():
    return jsonify({
        "status": "OK",
        "version": VERSION
    })

@app.route("/chemicals/")
def get_all_chemicals():
    result = [
        chemical_schema.dump(chemical).data 
        for chemical in Chemical.query.all()
    ]
    return jsonify(result)

@app.route("/equipment/")
def get_all_equipment():
    result = [
        equipment_schema.dump(equipment).data 
        for equipment in Equipment.query.all()
    ]
    return jsonify(result)

@app.route("/chemicals/<int:id>/")
def get_chemical_by_id(id):
    return jsonify(chemical_schema.dump(Chemical.query.get(id)).data)

@app.route("/equipment/<int:id>/")
def get_equipment_by_id(id):
    return jsonify(equipment_schema.dump(Equipment.query.get(id)).data)

@app.route("/chemicals/logs/")
def get_all_chemical_logs():
    result = [
        chemical_log_schema.dump(chemical_log).data 
        for chemical_log in ChemicalLog.query.all()
    ]
    return jsonify(result)

@app.route("/equipment/logs/")
def get_all_equipment_logs():
    result = [
        equipment_log_schema.dump(equipment_log).data 
        for equipment_log in EquipmentLog.query.all()
    ]
    return jsonify(result)

@app.route("/chemicals/logs/<int:id>")
def get_chemical_log_by_id(id):
    return jsonify(chemical_log_schema.dump(ChemicalLog.query.get(id)).data)

@app.route("/equipment/logs/<int:id>")
def get_equipment_log_by_id(id):
    return jsonify(equipment_log_schema.dump(EquipmentLog.query.get(id)).data)

@app.route("/chemicals/add/")
def add_chemical():
    pass

@app.route("/equipment/add/")
def add_equipment():
    pass

@app.route("/chemicals/<int:id>/remove/")
def remove_chemical():
    pass

@app.route("/equipment/<int:id>/remove/")
def remove_equipment():
    pass

@app.route("/chemicals/<int:id>/update/")
def update_chemical(id):
    chemical = Chemical.query.get(id)
    name = request.args.get('name', None)
    state = request.args.get('state', None)
    qty = request.args.get('qty', None)
    if name is not None:
        chemical.name = name
    if state is not None:
        chemical.state = bool(state)
    if qty is not None:
        chemical.qty = qty
    return jsonify({
        "status": "OK",
        "log": chemical_schema.dump(chemical).data
    })


@app.route("/equipment/<int:id>/update/")
def update_equipment(id):
    equipment = Equipment.query.get(id)
    name = request.args.get('name', None)
    is_consumable = request.args.get('consumable', None)
    qty = request.args.get('qty', None)
    if name is not None:
        chemical.name = name
    if is_consumable is not None:
        chemical.is_consumable = bool(is_consumable)
    if qty is not None:
        chemical.qty = qty
    return jsonify({
        "status": "OK",
        "log": chemical_schema.dump(chemical).data
    })

"""
Reserve a chemical.

URL args:
    id (int): ID of chemical to be reserved.
GET args:
    groupcode (int): Group code that reserved item, in the format BBBBSSNN
        (where B is the group's batch, S is the group's section (01 for Charm 
        to 16 for Res2 H), and N is the group number).
    qty (int): Amount of chemical to be reserved.
    dateprocured (DateTime): Date that chemical was procured in ISO format
        (YYYYMMDD).
"""
@app.route("/chemicals/<int:id>/reserve/")
def reserve_chemical(id):
    success = True
    # Get all required stuff
    chemical = Chemical.query.get(id)
    group_code = request.args.get('groupcode', None)
    qty = request.args.get('qty', None)
    date_procured = request.args.get('dateprocured', None)
    # Convert all items to Python objects
    try:
        date = datetime.datetime.strptime(
            date_procured, "%Y%m%d").date()
        date_procured = datetime.datetime.combine(
            date, datetime.datetime.min.time())
    except:
        success = False
        error = "Error parsing date"
    # Checks
    if group_code is None or qty is None or date_procured is None:
        success = False
        error = "Too few arguments"
    elif chemical.qty - int(qty) < 0:
        success = False
        error = "Reserved too much"
    elif int(qty) < 0:
        success = False
        error = "Reserved too little"
    elif int(group_code) < 20180000:
        success = False
        error = "Unrecognized group code"
    # Create object
    if success:
        log = ChemicalLog(
            chemical=chemical, group_code=int(group_code), qty=int(qty), 
            date_procured=date_procured)
        chemical.qty -= int(qty)
        db.session.add(log)
        db.session.commit()
        return jsonify({
            "status": "OK",
            "log": chemical_log_schema.dump(log).data
        })
    else:
        return jsonify({
            "status": "Error",
            "error": error
        })
    
"""
Reserve equipment.

URL args:
    id (int): ID of equipment to be reserved.
GET args:
    groupcode (int): Group code that reserved item, in the format BBBBSSNN
        (where B is the group's batch, S is the group's section (01 for Charm 
        to 16 for Res2 H), and N is the group number).
    qty (int): Amount of equipment to be reserved.
    dateprocured (DateTime): Date that equipment was procured in ISO format
        (YYYYMMDD).
    datereturn (DateTime): Date that equipment is to be returned in ISO format
        (YYYYMMDD).
"""
@app.route("/equipment/<int:id>/reserve/")
def reserve_equipment(id):
    success = True
    # Get all required stuff
    equipment = Equipment.query.get(id)
    group_code = request.args.get('groupcode', None)
    qty = request.args.get('qty', None)
    date_procured = request.args.get('dateprocured', None)
    date_return = request.args.get('datereturn', None)
    # Convert all items to Python objects
    try:
        date = datetime.datetime.strptime(
            date_procured, "%Y%m%d").date()
        date_procured = datetime.datetime.combine(
            date, datetime.datetime.min.time())
        date = datetime.datetime.strptime(
            date_return, "%Y%m%d").date()
        date_return = datetime.datetime.combine(
            date, datetime.datetime.max.time())
    except:
        success = False
        error = "Error parsing date"
    # Checks
    if group_code is None or qty is None or date_procured is None or date_return is None:
        success = False
        error = "Too few arguments"
    elif not equipment.is_consumable and equipment.qty - int(qty) < 0:
        success = False
        error = "Reserved too much"
    elif int(qty) < 0:
        success = False
        error = "Reserved too little"
    elif int(group_code) < 20180000:
        success = False
        error = "Unrecognized group code"
     # Create object
    if success:
        log = EquipmentLog(
            equipment=equipment, group_code=int(group_code), qty=int(qty), 
            date_procured=date_procured, date_return=date_return)
        if not equipment.is_consumable:
            equipment.qty -= int(qty)
        db.session.add(log)
        db.session.commit()
        return jsonify({
            "status": "OK",
            "log": equipment_log_schema.dump(log).data
        })
    else:
        return jsonify({
            "status": "Error",
            "error": error
        })

if __name__ == '__main__':
    app.debug = True
    app.run()