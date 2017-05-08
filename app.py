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
    qty = db.Column(db.Integer)
    date_procured = db.Column(db.DateTime)

    def __init__(self, group_code, chemical, qty, date_procured):
        self.group_code = group_code
        self.chemical = chemical
        self.qty = qty
        self.date_procured = date_procured

class EquipmentLog(db.Model):
    __tablename__ = 'equipment_log'

    id = db.Column(db.Integer, primary_key=True)
    group_code = db.Column(db.Integer)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"))
    equipment = db.relationship("Equipment", back_populates="logs")
    qty = db.Column(db.Integer)
    date_procured = db.Column(db.DateTime)
    date_return = db.Column(db.DateTime)

    def __init__(self, group_code, equipment, qty, date_procured, date_return):
        self.group_code = group_code
        self.equipment = equipment
        self.qty = qty
        self.date_procured = date_procured
        self.date_return = date_return

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
# for chemical in chemicals:
#     db.session.add(chemical)
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
@app.route("/chemicals/")
def chemicals():
    return jsonify([
        {
            "id": 1,
            "name": "Sodium chloride",
            "state": True,
            "qty": 200
        }
    ])

@app.route("/equipment")
@app.route("/equipment/")
def equipment():
    return jsonify([
        {
            "id": 1001,
            "name": "Petri dish",
            "is_consumable": False,
            "qty": 15
        }
    ])

@app.route("/chemicals/add")
def add_chemical():
    pass

@app.route("/equipment/add")
def add_equipment():
    pass

@app.route("/chemicals/remove")
def remove_chemical():
    pass

@app.route("/equipment/remove")
def remove_equipment():
    pass

@app.route("/chemicals/<int:id>/update")
def update_chemical(id):
    pass

@app.route("/equipment/<int:id>/update")
def update_equipment(id):
    pass

@app.route("/chemicals/<int:id>/reserve")
def reserve_chemical(id):
    date_reserved = request.args.get('date_reserved', None)
    qty = request.args.get('qty', None)
    group_code = request.args.get('group_code', None)
    chemical = Chemical.query.filter(Chemical.id == id).first
    log = ChemicalLog(group_code, chemical, qty, datetime(date_reserved))

@app.route("/equipment/<int:id>/reserve")
def reserve_equipment(id):
    date_reserved = request.args.get('date_reserved', None)
    date_return = request.args.get('date_return', None)
    qty = request.args.get('qty', None)
    group_code = request.args.get('group_code', None)
    chemical = Chemical.query.filter(Chemical.id == id).first
    log = ChemicalLog(group_code, chemical, qty, datetime(date_reserved), datetime(date_return))

if __name__ == '__main__':
    app.debug = True
    app.run()