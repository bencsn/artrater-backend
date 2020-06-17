"""
score_trials.py

After you have collected best-worst data, process it with this script to
generate latent scores for each item in your dataset. This script requires input
formatted something like this:

best,worst,option1,option2,option3,option4
dog,ennui,justice,dog,haven,ennui
tooth,hatred,hatred,microbe,photon,hatred

The underlying latent dimension in this example was intended to be concept 
concreteness.

Your input data may contain other columns (e.g., participant data), but it MUST
contain these K+2 columns.

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
import sys, argparse, trialgen, math, scoring
from spreadsheet import Spreadsheet




################################################################################
# MAIN
################################################################################
def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Command line for scoring best-worst data.')
    parser.add_argument("input", nargs="*", type=str, help="Path to a file(s) containing data to score.")
    parser.add_argument("--sep", type=str, default=None, help="Specify the column separator. If None specified, use default (tab for .tsv, comma for all else)")
    parser.add_argument("--name", type=str, default="Word", help="The name of the column we should use for outputting the item. Defaults to 'Word'.")
    parser.add_argument("--best", type=str, default="best", help="Name of column that holds string of 'best' choice.")
    parser.add_argument("--worst", type=str, default="worst", help="Name of column that holds string of 'worst' choice.")
    
    args = parser.parse_args()

    # go over each supplied input file and collect data
    trials = [ ]
    for file in args.input:
        trials += scoring.parse_bestworst_data(file, bestCol=args.best, worstCol=args.worst, sep=args.sep)
        
    # perform scoring. This takes awhile.
    methods = ["Value","Elo","RW","Best","Worst","Unchosen","BestWorst","ABW","David","ValueLogit","RWLogit","BestWorstLogit"] # "EloLogit",
    results = scoring.score_trials(trials, methods)

    # start building table of scored values for each item

    # gotta find eloMin and eloMax
    #   elos   = [ item.elo for item in results.itervalues() ]
    #   eloMin = min(elos)
    #   eloMax = max(elos)
    
    # print the header and results
    header = [ args.name ] + methods
    print(",".join(header))
    for name, data in results.iteritems():
        # skip dummy items
        if type(name) != str:
            continue
        
        scores = [ scoring.scoring_methods[method](data) for method in methods ]
        out    = [ name ] + [ str(score) for score in scores ]
        print(",".join(out))
    
if __name__ == "__main__":
    sys.exit(main())
