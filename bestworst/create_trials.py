"""
create_trials.py

Takes a plaintext file (.txt, .csv, or .tsv, sorry no .xls!) containing a list
of words and, from those words, generates a series of best-worst trials. The
input file may either be a list of words separated by whitespace (.txt), or
some sort of structured text file where a column name of specified.

Script provides options for customizing how best-worst trials are generated.
Default options are the suggested options. Don't screw around unless you know
what you are doing.

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
import sys, argparse, trialgen
from spreadsheet import Spreadsheet



def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Command line for generating best-worst trials from a list of items.')
    parser.add_argument("input", type=str, help="Path to a file containing input data (i.e., a list of words or other text stimuli).")
    parser.add_argument("N", nargs="?", type=int, default=None, help="Number of best-worst trials to generate. Suggested amount: number of items, times 8. So if you have 1000 items, 8000 trials. You may get *slightly* better results up to an N of 16, but gains are marginal. You may need fewer trials if your K is larger. Empirical testing not yet done.")
    parser.add_argument("K", nargs="?", type=int, default=4, help="Number of items per best-worst trial.")
    parser.add_argument("--generator", type=str, default="norepeateven", help="Method for generating trials. Don't screw with unless you know what you are doing. Options are: random, even, norepeat, norepeateven.") 
    parser.add_argument("--column", type=str, default=None, help="If inputting a structured text file, indicate which column to pull data from.")
    parser.add_argument("--sep", type=str, default=None, help="Specify the column separator. If None specified, use default (tab for .tsv, comma for all else)")

    args = parser.parse_args()
    
    # read in the items to build trials from
    items = [ ]
    if args.input.endswith(".txt") and args.sep == None and args.column == None:
        items = [item.strip() for item in open(args.input, "r").read().split() ]
    elif args.column == None:
        raise Exception("You must specify a column name with --column= to generate trials this way.")
    else:
        # comma by default or if specified, tab if .tsv
        sep = args.sep
        if sep == None and args.input.endswith(".tsv"):
            sep = "\t"
        elif sep == None:
            sep = ","
        ss = Spreadsheet.read_csv(args.input, delimiter=sep)

        # take the first column if no column specified
        items = ss[args.column]

    # filter out empty strings
    items = [ item for item in items if len(item) > 0 ]

    # parse our N and K
    K = args.K
    N = args.N
    if N == None:
        N = len(items) * 8
        
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

    # print the output, complete with header.
    # header = [ "option%d" % (i+1) for i in range(K) ]
    # print(",".join(header))
    for trial in trials:
        print(",".join(trial))
    # return trials
        
if __name__ == "__main__":
    sys.exit(main())
