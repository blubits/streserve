"""
API for the STReserve application.

:Author:     Maded Batara III
:Version:    v20170508
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
        "qty": 200
    }
]

VERSION = "20170508"

@app.route("/")
def home():
    return jsonify({
        "status": "OK",
        "version": VERSION
    })

@app.route("/chemicals/")
def chemicals():
    return jsonify(chemical_json)

@app.route("/equipment/")
def equipment():
    return jsonify(equipment_json)

if __name__ == '__main__':
    app.debug = True
    app.run()