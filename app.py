"""
API for the STReserve application.

:Author:     Maded Batara III
:Version:    v20170508
"""

import datetime
import os

from flask import Flask
from flask import jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_heroku import Heroku
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
if 'DYNO' in os.environ:
    import psycopg2
    hr = Heroku(app)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

db.reflect()
db.drop_all()

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
equipment.append(Equipment(name="Petri dish (small)", 
    is_consumable=False, qty=15))

db.create_all()
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
    return jsonify()

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
    pass

@app.route("/equipment/<int:id>/update/")
def update_equipment(id):
    pass

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
    chemical = Chemical.query.filter(Chemical.id == id).first()
    print(chemical)
    group_code = int(request.args.get('groupcode', None))
    qty = int(request.args.get('qty', None))
    date_procured = request.args.get('dateprocured', None)
    # Convert all items to Python objects
    try:
        date = datetime.datetime.strptime(
            date_procured, "%Y%m%d").date()
        date_procured = datetime.datetime.combine(
            date, datetime.datetime.min.time())
    except:
        pass
    # Quantity check
    if group_code is None or qty is None or date_procured is None:
        success = False
        error = "Too few arguments"
    elif chemical.qty - qty < 0:
        success = False
        error = "Reserved too much"
    elif qty < 0:
        success = False
        error = "Reserved too little"
    elif group_code < 20180000:
        success = False
        error = "Unrecognized group code"
    # Create object
    if success:
        log = ChemicalLog(
            chemical=chemical, group_code=group_code, qty=qty, 
            date_procured=date_procured)
        chemical.qty -= qty
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
    

@app.route("/equipment/<int:id>/reserve/")
def reserve_equipment(id):
    pass

if __name__ == '__main__':
    app.debug = True
    app.run()