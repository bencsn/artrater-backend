import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import auth

cred = credentials.Certificate(
    "thelettersproject-firebase-adminsdk-jgkj4-b577df0515.json")
firebase_admin.initialize_app(
    cred, {'databaseURL': 'https://thelettersproject.firebaseio.com', 'authDomain': 'thelettersproject-artrater.web.app'})

db = firestore.client()
experiment_ref = db.collection(u'experiments')
experiment_type_ref = db.collection(u'experiment_types')
