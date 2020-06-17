"""
aggregate_simulations.py

Aggregates batches of simulations with the same parameters.

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
import sys, os, argparse
from spreadsheet import Spreadsheet
from scipy.stats.stats import pearsonr



def main(argv = sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Interface for best-worst simulation aggregator. Output will be r^2 between latent dimension and scoring method, by simulation. Unique file created for each parameter set found.')
    parser.add_argument("folders", nargs="*", type=str, help="A list of folders to find simulation results in. Aggregate simulations by shared parameters.")
    parser.add_argument("--dir", type=str, default="sim_aggregates", help="The diretory to dump simulation aggregation results into.")

    args = parser.parse_args()

    # the unique conditions we've found across folders
    conditions = { }

    # iterate over all of the paths and collect the filenames of each of the
    # conditions that were simulatated
    for path in args.folders:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.startswith("."):
                    continue

                index = filename.split("_sim")[0]
                if index not in conditions:
                    conditions[index] = [ ]
                flpath = os.path.join(dirpath,filename)
                conditions[index].append(flpath)

    # create the destination folder
    os.system("mkdir %s" % args.dir)
                
    # aggregate values for each of the simulations
    for condition, files in conditions.iteritems():
        results_table = { }
        method_order  = None
        
        # read in the data for each file and save it
        for file in files:
            ss = Spreadsheet.read_csv(file)

            # the column name for the latent dimension, always 2nd column.
            # first column is Item name.
            latentCol   = ss.header[1]
            latent_vals = ss[latentCol]
            
            # the column names for each scoring method we used
            methods= ss.header[2:]

            if method_order == None:
                method_order = methods

            # calculate correlation coefficients for each method
            for method in methods:
                # get scored values
                scores = ss[method]

                # make sure the method is in the results table
                if method not in results_table:
                    results_table[method] = [ ]

                # save the data
                r, p = pearsonr(latent_vals, scores)
                results_table[method].append(r**2)

        # print results for this condition
        dest = os.path.join(args.dir, condition + "_aggregate.csv")
        fl   = open(dest, "w")
        header = ",".join(["Simulation"] + method_order) + "\n"
        fl.write(header)
        for i in xrange(len(results_table[method_order[0]])):
            row = [i+1] + [ results_table[method][i] for method in method_order ]
            fl.write(",".join([str(v) for v in row]) + "\n")
        fl.close()
        
if __name__ == "__main__":
    sys.exit(main())
