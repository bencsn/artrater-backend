from admin import experiment_type_ref, experiment_ref, db
from firebase_admin import firestore
import pandas as pd
from flask import abort
import datetime


class Experiment:
    def __init__(self,  experiment_doc_ref=None, age="Not specified", gender="Not specified", completed=False, types=[], prev_experiments=[], starts_from_trial_index=0, ends_at_trial_index=10, trials=[]):
        self.age = age
        self.gender = gender
        self.types = types
        self.prev_experiments = prev_experiments
        self.ends_at_trial_index = ends_at_trial_index
        self.starts_from_trial_index = starts_from_trial_index
        self.trials = trials
        self.experiment_doc_ref = experiment_doc_ref
        self.completed = completed

    def set_existing_experiment_from_id(self, experiment_id):
        doc_ref = experiment_ref.document(experiment_id)
        self.set_existing_experiment(doc_ref)

    def set_existing_experiment(self, experiment_doc_ref):
        self.experiment_doc_ref = experiment_doc_ref
        self.__fetch_types()
        experiment = self.get_experiment_info()
        if (experiment):
            self.age = experiment["age"]
            self.gender = experiment["gender"]
            self.completed = experiment["completed"]
            self.starts_from_trial_index = experiment["starts_from_trial_index"]
            self.ends_at_trial_index = experiment["ends_at_trial_index"]
        # Get trials of this experiment
        trial_docs = experiment_doc_ref.collection('trials').stream()
        self.trials = [t.to_dict()['options'] for t in trial_docs]


    def get_experiment_id(self):
        if (self.experiment_doc_ref):
            return self.experiment_doc_ref.id
        else:
            return None

    def get_experiment_info(self):
        experiment_doc = self.experiment_doc_ref.get()
        if (experiment_doc.exists):
            experiment = experiment_doc.to_dict()
        else:
            print("Experiment doesn't exist'")
            experiment = None
        return experiment


    def get_full_trials(self):
        if (not self.trials or len(self.trials) <= 0 or len(self.types) <= 0 or not self.types):
            abort(422, "Missing trials or types")
        full_trials = []
        print(self.trials)
        tdf = pd.read_csv('https://firebasestorage.googleapis.com/v0/b/thelettersproject.appspot.com/o/artwork_with_hm_entropy.csv?alt=media&token=e3822a2a-8af8-433f-b840-e1edd4a1ece3')
        for type in self.types:
            for t in self.trials:
                options_with_images=[]
                # del t["options"]['Unnamed: 0']
                options_dict = t
                options_dict.pop("Unnamed: 0", None)
                options = list(options_dict.values())
                for o in options:
                    current_t = tdf[tdf["id"] == o]
                    options_with_images.append({"option_id":o, "imageURL":current_t["img"].iloc[0], "title":current_t["title"].iloc[0]})
                full_trials.append(
                    {'name': type["name"], "best_question": type["best"], "worst_question": type["worst"], "options":options_with_images})
        return full_trials

    def __prepare(self):
        self.__fetch_types()
        self.__fetch_prev_experiments()
        self.__fetch_trials()

    def __fetch_types(self):
        type_docs = experiment_type_ref.stream()
        types = [t.to_dict() for t in type_docs]
        self.types = types

    def __fetch_prev_experiments(self):
        prev_experiment_docs = experiment_ref.order_by(
            u'createdAt', direction=firestore.Query.DESCENDING).stream()
        prev_experiments = [exp.to_dict() for exp in prev_experiment_docs]
        self.prev_experiments = prev_experiments
        if (len(prev_experiments) > 0):
            last_experiment = prev_experiments[-len(prev_experiments)]
            self.starts_from_trial_index = last_experiment['ends_at_trial_index']
            self.ends_at_trial_index = self.starts_from_trial_index + 10
        else:
            last_experiment = None
            self.starts_from_trial_index = 0
            self.ends_at_trial_index = 10

    def __fetch_trials(self):
        print(self.starts_from_trial_index, self.ends_at_trial_index)
        trials = pd.read_csv('https://firebasestorage.googleapis.com/v0/b/thelettersproject.appspot.com/o/all_trials.csv?alt=media&token=91d42c7c-5d8f-4f1a-ae89-59acd0bc6ff9')
        if (trials.shape[0]-1 <= self.ends_at_trial_index and self.starts_from_trial_index < trials.shape[0]-1):
            # Last batch
            # Return the remaining trials
            self.ends_at_trial_index = trials.shape[0]-1
        if (trials.shape[0]-1 <= self.ends_at_trial_index and self.starts_from_trial_index >= trials.shape[0]-1):
            # Out of bound
            # check if there are any unfinished experiments; if so, return that experiment instead
            undone_experiments = self.__check_inprogress()
            if (undone_experiments):
                exp = undone_experiments[0]
                exp_id = exp["experimentID"]
                doc = experiment_ref.document(exp_id).get()
                exp_info = doc.to_dict()
                print(exp_info)
                self.starts_from_trial_index = exp_info['starts_from_trial_index']
                self.ends_at_trial_index = exp_info['ends_at_trial_index']
            else:
                # No more experiments to do
                #TODO: mark everything as complete
                abort(404, "No more experiments")
        selected_trials = trials[self.starts_from_trial_index:self.ends_at_trial_index]
        self.trials = selected_trials.to_dict('records')

    def create_experiment(self):
        self.__prepare()
        new_experiment_data = {
            u'createdAt': datetime.datetime.now(),
            u'age': self.age,
            u'gender': self.gender,
            u'starts_from_trial_index': self.starts_from_trial_index,
            u'ends_at_trial_index': self.ends_at_trial_index,
            u'completed': self.completed
        }
        doc_ref = experiment_ref.document()
        doc_ref.set(new_experiment_data)
        self.experiment_doc_ref = doc_ref
        self.__add_trials_to_db()
        self.__add_to_inprogress(doc_ref.id)

    def __add_trials_to_db(self):
        if (self.experiment_doc_ref == None):
            abort(500, "Something went wrong while trying to add trials")
        for t in self.trials:
            trial_ref = self.experiment_doc_ref.collection("trials").document()
            trial_ref.set({"options": t})

    def __add_to_inprogress(self, experiment_id):
        ref = db.collection("inprogress").document(experiment_id)
        ref.set({"experimentID": experiment_id,
                 "createdAt": datetime.datetime.now()})

    def complete_experiment(self):
        if (experiment_doc_ref):
            # Remove from inprogress
            db.collection("inprogress").document(
                self.experiment_doc_ref.id).delete()
            # Mark as completed
            self.experiment_doc_ref.set({u'completed': True}, merge=True)
            self.completed = True

    def __check_inprogress(self):
        docs = db.collection("inprogress").order_by(
            u'createdAt', direction=firestore.Query.DESCENDING).stream()
        inp = [d.to_dict() for d in docs]
        if (len(inp) > 0):
            # There are still some in-progress left left
            return inp
        else:
            return None