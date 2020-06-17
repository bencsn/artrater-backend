"""
flag_noncompliant_users.py

Uses already-scored best-worst data to identify participants who do not seem
to be on task. For example, they might answer randomly or according to some 
other strategy that makes their answers deviate from the consensus.

This script can additionally filter noncompliant participants from your data
and output a "clean" dataset.

Created by Geoff Hollis
http://www.ualberta.ca/~hollis
hollis at ualberta dot ca

This software is released under the Creative Commons licence: 
  Attribution-NonCommerical-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
  https://creativecommons.org/licenses/by-nc-sa/4.0/

For published academic research using these tools, please cite:
  Hollis, G. (2017). Scoring best/worst data in unbalanced, many-item designs,
    with applications to crowdsourcing semantic judgments. Behavior Research 
    Methods, XX(X), 1-19. doi: 10.3758/s13428-017-0898-2
"""
import sys, argparse, scoring
from spreadsheet import Spreadsheet



def main(argv = sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Command line for filtering noncompliant participants from best-worst data.')
    parser.add_argument("scores", type=str, help="Path to a file containing scores computed over all users (including noncompliant ones).")
    parser.add_argument("input", nargs="*", type=str, help="Path to a file(s) containing trial-level data.")
    parser.add_argument("--id_column", type=str, default=None, help="A column in your input data that specifies user ID. If no value is supplied, uses the name of the file.")
    parser.add_argument("--best", type=str, default="best", help="Name of column that holds string of 'best' choice.")
    parser.add_argument("--worst", type=str, default="worst", help="Name of column that holds string of 'worst' choice.")
    parser.add_argument("--score_method", type=str, default="Value", help="The scoring method to calculate compliance by.")
    parser.add_argument("--filter", type=float, default=None, help="If you want to filter users by compliance, specify the threshold here. The output will be the trials for just users who met your threshold of compliance, as a single file. This can be submitted to score_trials.py for rescoring.")

    args = parser.parse_args()

    # read the scores
    ss = Spreadsheet.read_csv(args.scores)
    scores = { }
    for row in ss:
        scores[row[0]] = row[args.score_method]

    # go through each file and calculate participant compliance and log their
    # trials
    compliance  = { }
    paircount   = { }
    user_trials = { }
    
    for file in args.input:
        # if a participant ID column is not specified, use the name of the file.
        # Otherwise, use values in the specified column to determine ID.
        id_col = None
        if args.id_column != None:
            ss = Spreadsheet.read_csv(file)
            id_col = ss[args.id_column]
                        
        # read in the user's data, calculate compliance for each trial
        trials = scoring.parse_bestworst_data(file, bestCol=args.best, worstCol=args.worst)
        # generate a user ID based on the file name
        if id_col == None:
            id_col = [ file ] * len(trials)

        # check for agreement on each trial
        for i in xrange(len(trials)):
            id    = id_col[i]
            trial = trials[i]
            best, worst, others = trial
            
            # something funny going on in your data; check it out
            duplic = best == worst
            # skip trial if best == worst
            if duplic == True:
                continue

            # set default values for participant if needed
            if id not in compliance:
                compliance[id] = 0
                paircount[id]  = 0
                user_trials[id]= [ ]

            # calculate compliance
            pairs = [ (best, other) for other in ((worst,) + others) ] + [ (other, worst) for other in others ]
            consistent = [ scores[pair[0]] > scores[pair[1]] for pair in pairs ]
            compliance[id] += sum(consistent)
            paircount[id]  += len(pairs)
            user_trials[id].append(trial)
                
    # calculate overall accuracy for each participant
    accuracy = { }
    for user in compliance.iterkeys():
        accuracy[user] = float(compliance[user]) / paircount[user]

    # print compliance for each person
    if args.filter == None:
        # sort users by their accuracy
        users = accuracy.keys()
        users.sort(lambda a,b: cmp(accuracy[a], accuracy[b]), reverse=True)

        print "ID,Compliance"
        for user in users:
            print "%s,%0.3f" % (str(user), accuracy[user])
            
    # print trials for users that meet the filter threshold
    else:
        user_count = 0
        for user in accuracy.iterkeys():
            # skip by everyone who doesn't make the cut
            if accuracy[user] < args.filter:
                continue

            # print out data for everyone else
            best,worst,others = user_trials[user][0]
            options = list(others)

            # do we need to print the header?
            if user_count == 0:
                optCols = [ "option%d" % (i+1) for i in xrange(len(options)) ]
                header  = [ "User", "best", "worst" ] + optCols
                print ",".join(header)

            # print out each trial for the user
            for trial in user_trials[user]:
                best,worst, others = trial
                options = list(others)

                out = [ user, best, worst ] + options
                out = [ str(v) for v in out ]
                print ",".join(out)

            # increment our users
            user_count += 1
    
if __name__ == "__main__":
    sys.exit(main())

