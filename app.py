import os
from flask import Flask, request, abort, jsonify
from admin import experiment_ref, experiment_type_ref, db, firestore
import subprocess
import datetime
import pandas as pd
from experiment import Experiment
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
     r"/api/*": {"origins": ["http://localhost:3000", "https://thelettersproject.web.app"]}})


@app.route('/api')
def hello_world():
    return 'This is an entry point to backend services for the Letter Project\'s platform for rating van Gogh\'s artworks'


@app.route("/api/start", methods=["POST"])
def start_experiment():
    """ 
    This will 
    - create a document in the 'experiments' db collection.
    - write trials to the 'trials' subcollection
    - return experimentID.
    """
    post_data = request.get_json()
    prolificID = post_data["prolificID"]
    e = Experiment()
    e.create_experiment(prolificID=prolificID)
    return jsonify({"experimentID": e.get_experiment_id(), "trials": e.get_trials(),  "info":e.get_experiment_info()})

@app.route("/api/experiment")
def get_experiment_by_id():
    eid = request.args.get('eid')
    if (not eid):
        abort(422, "Missing experiment ID (eid)")
    e = Experiment()
    e.set_existing_experiment_from_id(eid)
    return jsonify({"experimentID":e.get_experiment_id(),"info":e.get_experiment_info(),"trials":e.get_trials()})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
