"""
API for the STReserve application.

:Author:     Maded Batara III
:Version:    v20170508
"""

from flask import Flask
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS, cross_origin
from datetime import datetime

app = Flask(__name__)
CORS(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

############
## SCHEMA ##
############

class Chemical(db.Model):
    __tablename__ = 'chemicals'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    state = db.Column(db.Boolean)
    qty = db.Column(db.Integer)
    logs = db.relationship("ChemicalLog", back_populates="chemical")

    def __init__(self, name, state, qty):
        self.name = name
        self.state = state
        self.qty = qty

    def __repr__(self):
        return "<Chemical {0}, {1}{2}>".format(
            self.name, self.qty, "g" if self.state else "mL")

class Equipment(db.Model):
    __tablename__ = 'equipment'

    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String)
    is_consumable = db.Column(db.Boolean)
    qty = db.Column(db.Integer)
    logs = db.relationship("EquipmentLog", back_populates="equipment")

    def __init__(self, name, is_consumable, qty):
        self.name = name
        self.is_consumable = is_consumable
        self.qty = qty

    def __repr__(self):
        return "<Equipment {0}{1}, qty {2}>".format(
            self.name, " (consumable)" if self.is_consumable else "", self.qty)

class ChemicalLog(db.Model):
    __tablename__ = 'chemical_log'

    id = db.Column(db.Integer, primary_key=True)
    group_code = db.Column(db.Integer)
    chemical_id = db.Column(db.Integer, db.ForeignKey("chemicals.id"))
    chemical = db.relationship("Chemical", back_populates="logs")
    time_procured = db.Column(db.DateTime)

    def __init__(self, group_code, reserved_id, time_procured):
        self.group_code = group_code
        self.chemical = chemical
        self.time_procured = time_procured

class EquipmentLog(db.Model):
    __tablename__ = 'equipment_log'

    id = db.Column(db.Integer, primary_key=True)
    group_code = db.Column(db.Integer)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"))
    equipment = db.relationship("Equipment", back_populates="logs")
    time_procured = db.Column(db.DateTime)
    time_return = db.Column(db.DateTime)

    def __init__(self, group_code, equipment, time_procured, time_return):
        self.group_code = group_code
        self.equipment = equipment
        self.time_procured = time_procured
        self.time_return = time_return

class ChemicalSchema(ma.ModelSchema):
    class Meta:
        model = Chemical

class EquipmentSchema(ma.ModelSchema):
    class Meta:
        model = Equipment

# chemical_schema = ChemicalSchema()
# equipment_schema = EquipmentSchema()

# chemicals = []
# chemicals.append(Chemical("Sodium chloride", True, 200))
# chemicals.append(Chemical("Water", False, 100))
# equipment_sample = Equipment("Petri dish (small)", False, 15)

# db.create_all()
# db.session.add(chemical_sample)
# db.session.add(chemical_sample_2)
# db.session.add(equipment_sample)
# db.session.commit()

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

@app.route("/chemicals")
def chemicals():
    chemical_schema.dump(author).dat

@app.route("/equipment")
def equipment():
    return jsonify(list(Equipment.query.all()))

@app.route("/chemicals/add")
def add_chemical():
    pass

@app.route("/equipment/add")
def add_equipment():
    pass

@app.route("/chemicals/<id:id>/modify")
def modify_chemical(id):
    pass

@app.route("/equipment/<id:id>/modify")
def modify_equipment(id):
    pass

@app.route("/chemicals/<id:id>/reserve")
def reserve_chemical(id):
    pass

@app.route("/equipment/<id>/reserve")
def reserve_equipment(id):
    pass

if __name__ == '__main__':
    app.debug = True
    app.run()