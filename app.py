import os

from flask import Flask, request, abort

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'This is an entry point to backend services for the Letter Project\'s platform for rating van Gogh\'s artworks'

@app.route("/start")
def start_experiment():
    """ 
    This will create an experiment in the database and return an experiment ID
    """ 


@app.route('/trialgen')
def trialgen():
    """ 
    This will return one trial containing 4 items.
    Requires users to submit an experiment ID.
    Requires users to submit a trial number as a query string, starting from t = 1 (e.g. ?t=1).
    """
    t = request.args.get('t')
    id = request.args.get('id')
    if (t==None or t.strip()==""):
        abort(422, "A trial number t is required and must be provided as a query string")
    if (id==None or id.strip()==""):
        abort(422, "An experiment ID id is required and must be provided as a query string")
    return 'I am a trial generator! :D: ---> ' + str(t)


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))