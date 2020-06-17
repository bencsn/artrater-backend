"""
Runs a simulated best-worst experiment, according to specified parameters.

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
import sys, argparse, scoring, trialgen, random
from spreadsheet import Spreadsheet



################################################################################
# HELPER FUNCTIONS
################################################################################
def sort_words(trial, latent_values, noise=0):
    """Returns a sorted list of the words in trial (not in place), by their
       latent value, plus added noise.
    """
    trial = [ item for item in trial ]
    if noise == 0:
        trial.sort(lambda a,b: cmp(latent_values[a], latent_values[b]), reverse=True)
        return trial
    
    tmpvals = { }
    for item in trial:
        tmpvals[item] = latent_values[item] + random.gauss(0,noise)
    trial.sort(lambda a,b: cmp(tmpvals[a], tmpvals[b]), reverse=True)
    return trial



################################################################################
# MAIN
################################################################################
def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Interface for best-worst simulation')
    parser.add_argument("input", type=str, help="A .csv or .tsv input file containing two columns, named by default Item and LatentValue. Item is an identifying label and LatentValue is the item's True value along the dimension to be evaluated.")
    parser.add_argument("N", type=int, help="Number of trials to generate for the simulation.")
    parser.add_argument("K", type=int, default=4, help="Number of items per trial, defaults to 4.")
    parser.add_argument("--noise", type=float, default=0.0, help="the sd to use for generating noise on each decision (noise is normally distributed).")
    parser.add_argument("--generator", type=str, default="even", help="The type of trial generation method for running the simulation. Options are: random, even, norepeat, norepeateven. See Hollis (2017) for details.")
    parser.add_argument("--sep", type=str, default=None, help="Column seperator for the input file")
    parser.add_argument("--item", type=str, default="Item", help="Column corresponding to item name.")
    parser.add_argument("--latentvalue", type=str, default="LatentValue", help="Column corresponding to latent value name.")
    parser.add_argument("--dummy", type=bool, default=True, help="use a dummy player to bound tournament-based scores.")
    parser.add_argument("--iters", type=int, default=100, help="Number of iterations to run tournament-based methods for. 100 is likely sufficient to ensure convergence, if not a little overkill.")

    args = parser.parse_args()

    # determine the column seperator for our input data
    sep = args.sep
    if sep == None and args.input.endswith(".tsv"):
        sep = "\t"
    elif sep == None:
        sep = ","
    
    # read in latent values from the input data
    latent_values = { }
    ss = Spreadsheet.read_csv(args.input, delimiter=sep)
    for row in ss:
        latent_values[str(row[args.item])] = row[args.latentvalue]

    # get the names of our unique items
    items = latent_values.keys()

    # parse our N and K
    K = args.K
    N = args.N

    # generate trials from items
    trials = [ ]
    if args.generator == "norepeateven":
        trials = trialgen.build_trials_even_bigram_norepeat(items, N=N, K=K)
    elif args.generator == 'even':
        trials = trialgen.build_trials_even(items, N=N, K=K)
    elif args.generator == 'random':
        trials = trialgen.build_trials_random(items, N=N, K=K)
    elif args.generator == "norepeat":
        trials = trialgen.build_trials_random_bigram_norepeat(items, N=N, K=K)
    else:
        raise Exception("You must specify a proper generation method: norepeateven, even, random, norepeat.")

    
    # sort words in each trial by their latent value, plus noise
    trials = [ sort_words(trial, latent_values, args.noise) for trial in trials ]
    
    # convert the trials into format: (best, worst, (others,))
    trials = [ (trial[0], trial[-1], tuple(trial[1:-1])) for trial in trials ]

    # perform scoring. This takes awhile.
    methods = ["Value","Elo","RW","Best","Worst","Unchosen","BestWorst","ABW","David","ValueLogit","RWLogit","BestWorstLogit"]
    results = scoring.score_trials(trials, methods, iters=args.iters, dummy=args.dummy)

    # print the header and results
    header = [ args.item, args.latentvalue ] + methods
    print ",".join(header)
    for name, data in results.iteritems():
        # skip dummy items
        if type(name) != str:
            continue
        
        scores = [ scoring.scoring_methods[method](data) for method in methods ]
        out    = [ name, latent_values[name] ] + [ str(score) for score in scores ]
        print ",".join([ str(v) for v in out ])

if __name__ == "__main__":
    sys.exit(main())
