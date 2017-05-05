"""
API for the STReserve application.

:Author:     Maded Batara III
:Version:    v20170503
"""

from flask import Flask
from flask import jsonify

app = Flask(__name__)

equipment_json = [
    {
        "id": 1001,
        "name": "Petri dish (small)",
        "is_consumable": False,
        "qty": 15
    }
]

chemical_json = [
    {
        "id": 1,
        "name": "Sodium chloride",
        "state": True,
        "qty": 
    }
]

@app.route("/chemicals/")
def chemicals():
    return jsonify(chemicals_json)

@app.route("/equipment/")
def equipment():
    return jsonify(equipment_json)
