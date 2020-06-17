import os

from flask import Flask, request, abort, jsonify
from admin import experiment_ref, experiment_type_ref, db
from firebase_admin import firestore
import subprocess
import datetime
import pandas as pd
from experiment import Experiment

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'This is an entry point to backend services for the Letter Project\'s platform for rating van Gogh\'s artworks'


@app.route("/start")
def start_experiment():
    """ 
    This will 
    - create a document in the 'experiments' db collection.
    - write trials to the 'trials' subcollection
    - return experimentID.
    """
    e = Experiment()
    e.create_experiment()
    return jsonify({"experimentID": e.get_experiment_id(), "trials": e.get_full_trials(),  "info":e.get_experiment_info()})

@app.route("/experiment")
def get_experiment_by_id():
    eid = request.args.get('eid')
    if (not eid):
        abort(422, "Missing experiment ID (eid)")
    e = Experiment()
    e.set_existing_experiment_from_id(eid)
    return jsonify({"experimentID":e.get_experiment_id(),"info":e.get_experiment_info(),"trials":e.get_full_trials()})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
