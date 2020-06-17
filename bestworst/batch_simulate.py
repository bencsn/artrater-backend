"""
batch_simulate.py

Allows you to iterate through various values of parameters and run the simulator
with each combination. Can repeat each combination of parameters multiple times,
so you can average your results across simulations.

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
import sys, argparse, os

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Interface for best-worst simulation')
    parser.add_argument("input", type=str, help="A .csv or .tsv input file containing two columns, named by default Item and LatentValue. Item is an identifying label and LatentValue is the item's True value along the dimension to be evaluated.")

    # variable parameters
    parser.add_argument("--N", type=str, default="1000,2000,4000,8000,16000", help="Comma-separated N sizes to try.")
    parser.add_argument("--noise", type=str, default="0.0,0.5,1.0,2.0", help="Comma-separted noise levels to use. Nosie is sd to use for generating noise on each decision (noise is normally distributed, mu=0).")
    parser.add_argument("--generator", type=str, default="even", help="Comma-separated list of trial generation methods to try. Options are: random, even, norepeat, norepeateven. See Hollis (2017) for details.")

    # fixed parameters
    parser.add_argument("--K", type=int, default=4, help="K sizes to try.")
    parser.add_argument("--sep", type=str, default=None, help="Column seperator for the input file")
    parser.add_argument("--dummy", type=bool, default=True, help="use a dummy player to bound tournament-based scores.")
    parser.add_argument("--iters", type=int, default=100, help="Number of iterations to run tournament-based methods for. 100 is likely sufficient to ensure convergence, if not a little overkill.")
    parser.add_argument("--item", type=str, default="Item", help="Column corresponding to item name.")
    parser.add_argument("--latentvalue", type=str, default="LatentValue", help="Column corresponding to latent value name.")
    parser.add_argument("--num_simulations", type=int, default=100, help="Number of simulations per parameter set to run.")
    parser.add_argument("--dir", type=str, default="simulations", help="Destination folder to store simulations.")
    parser.add_argument("--label", type=str, default="", help="Optional string label to add to the front of every output file.")

    args = parser.parse_args()

    Ns         = [ int(v) for v in args.N.split(",") ]
    noises     = [ float(v) for v in args.noise.split(",") ]
    generators = [ v for v in args.generator.split(",") ]
    
    # create the destination folder
    os.system("mkdir %s" % args.dir)
    
    # go through our combination of parameter sets and run the script with
    # each one
    for N in Ns:
        for noise in noises:
            for generator in generators:
                for sim in xrange(args.num_simulations):
                    # generate the name of the output file
                    # LatentValue_N_K_generator_noise_dummy_epoch.csv
                    fname = "%s_N%d_K%d_%s_noise%0.2f_dummy%s_sim%03d.csv" % \
                            (args.latentvalue, N, args.K, generator, noise,
                             str(args.dummy), sim+1)
                    if len(args.label) > 0:
                        fname = args.label + "_" + fname

                    # make the out path
                    path = os.path.join(args.dir, fname)

                    # prepare the command
                    cmd = "python scripts/simulate_results.py %s %d %d --noise=%f --generator=%s --item=%s --latentvalue=%s --dummy=%s --iters=%s" % \
                          (args.input, N, args.K, noise, generator, args.item, args.latentvalue, str(args.dummy), args.iters)
                    
                    # run the simulation
                    os.system("%s > %s" % (cmd, path))

    
if __name__ == "__main__":
    sys.exit(main())
