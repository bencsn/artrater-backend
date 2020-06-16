import os

from flask import Flask, request, abort, jsonify

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'This is an entry point to backend services for the Letter Project\'s platform for rating van Gogh\'s artworks'

@app.route("/start")
def start_experiment():
    """ 
    This will 
    1) create a document in the 'experiments' db collection.
    2) call a function to generate trials. 
    3) add the trials to the 'trials' subcollection under the 'experiment' collection.
    4) return experimentID.
    """ 
    return jsonify({"message":"I create an experiment and add it to the database and return the experiment ID"})


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))