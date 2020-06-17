"""
Helper functions for scoring best-worst trials. Provides various options for
scoring data, including Elo, Rescorla-Wagner, Value Scoring, and various
count-based methods. See README.txt for further info on the scoring methods.

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
import random, math
from spreadsheet import Spreadsheet



################################################################################
# VARIABLES
################################################################################

# A table mapping the names of scoring methods to their appropriate function
# calls.
scoring_methods = {
    # data taken from TRIALS
    "Best"           : lambda item: item.best,
    "Worst"          : lambda item: item.worst,
    "Unchosen"       : lambda item: item.trials - item.best - item.worst,
    "BestWorst"      : lambda item: item.bestworst_score(),
    "BestWorstLogit" : lambda item: item.bestworst_score(),
    "ABW"            : lambda item: item.abw_score(),
    "David"          : lambda item: item.david_unbalanced_score(),

    # data taken from PAIRINGS
    "Wins"         : lambda item: item.wins,
    "Losses"       : lambda item: item.losses,
    "Ties"         : lambda item: item.unranked,
    "WinLoss"      : lambda item: item.winloss_norm_score(),
    "WinLossLogit" : lambda item: item.winloss_logit_score(),

    # Tournament methods, data taken from PAIRINGS
    "Elo"          : lambda item: item.elo,
    "Value"        : lambda item: item.value,
    "RW"           : lambda item: item.reswag_score(),
    "EloLogit"     : lambda item,eloMax,eloMin: item.elo_logit_score(eloMin,eloMax),
    "ValueLogit"   : lambda item: item.value_logit_score(),
    "RWLogit"      : lambda item: item.reswag_logit_score(),
    }



################################################################################
# CLASSES
################################################################################
class ItemEntry(object):
    """Contains an entry for a single item in your best-worst experiment. Used
       for tracking wins, losses, and ratings for various scoring methods.
    """
    def __init__(self, entity, base=0):
        self.entity = entity

        # for elo scoring
        self.elo    = base

        # for win-loss SCORING
        self.wins   = 0
        self.losses = 0

        # for win-loss COUNTING
        self.trials  = 0
        self.best    = 0
        self.worst   = 0
        self.unranked= 0

        # for value scoring
        self.value = 0.5

        # for rescorla-wagner scoring
        self.reswag_win  = 0.0
        self.reswag_lose = 0.0

        # opponents beat and lost to
        self.beat        = set()
        self.lose        = set()

    def win(winner, loser, iteration=1):
        winner.win_elo(loser, iteration)
        winner.win_value_discrim(loser, iteration)
        winner.win_reswag(loser, iteration)

        winner.beat.add(loser)
        loser.lose.add(winner)

    def win_value_discrim(winner, loser, iteration):
        """Update Value Score based on win/loss
        """
        rate = 0.025 / iteration

        rwin = winner.value / (1.0 - winner.value)
        rlos = loser.value  / (1.0 - loser.value)
        salience = 1.0 - rwin / (rwin + rlos)

        # handle the rescorla-wagner updates
        Dw = salience * rate * (1.0 - winner.value)
        Dl = salience * rate * (0   - loser.value)
        winner.value += Dw
        loser.value  += Dl

    def win_reswag(winner, loser, iteration):
        """Updates Rescrola-Wagner scores based on win/loss
        """
        # set the rate of learning.
        rate = 0.025 / iteration

        # calculate total association strengths
        w_v_tot = winner.reswag_win + winner.reswag_lose
        l_v_tot = loser.reswag_win + loser.reswag_lose

        # calculate the probabily of winning for each player --
        # 50/50 in the case of no exposure
        try:
            w_pwin = winner.reswag_win / w_v_tot
        except:
            w_pwin = 0.5
        try:
            l_pwin = loser.reswag_win  / l_v_tot
        except:
            l_pwin = 0.5

        # calculate the salience of the outcome
        rwin = w_pwin / max(0.0001, (1.0 - w_pwin))
        rlos = l_pwin  / max(0.0001, (1.0 - l_pwin))
        try:
            salience = 1.0 - rwin / (rwin + rlos)
        except:
            salience = 1.0
        w_salience = salience
        l_salience = salience
        
        # handle the rescorla-wagner updates
        winner.reswag_win += w_salience * rate * (1.0 - w_v_tot)
        loser.reswag_lose += l_salience * rate * (1.0 - l_v_tot)
        
    def win_elo(winner, loser, iteration):
        """Updates Elo scores based on win/loss
        """
        winner.wins  += 1
        loser.losses += 1

        Qw = 10 ** (winner.elo / 400.)
        Ql = 10 ** (loser.elo / 400.)
        Ew = Qw / (Qw + Ql)
        delta = float(30.0 * (1. - Ew))
        winner.elo += delta
        loser.elo  -= delta

    ############################################################################
    # SCORING FUNCTIONS
    ############################################################################
    def david_unbalanced_score(self):
        """Calculates the score proposed by H. David (1987)
        """
        wsum = sum([opp.wins for opp in self.beat])
        lsum = sum([opp.losses for opp in self.lose])
        return wsum - lsum
    
    def winloss_norm_score(self):
        # should range between [-1, 1]
        winloss = (self.wins - self.losses) / max(1.0, float(self.wins + self.losses + self.unranked))

        # normalize to [0, 1]
        winloss = (winloss + 1.0) / 2.0
        return winloss

    def winloss_logit_score(self):
        wln = self.winloss_norm_score()

        # to avoid div0 errors
        wln = min(max(wln, 0.0001), 0.9999)
        return math.log(winloss / (1.0-winloss))

    def bestworst_score(self):
        """normalized bestworst score"""
        # scales between [-1, 1]
        bestworst = (self.wins - self.losses) / float(self.trials)

        # rescale to [0, 1]
        return (bestworst + 1.0) / 2.0

    def bestworst_logit_score(self):
        bw = self.bestworst_score()
        # avoid div0 errors
        bw = min(max(bw, 0.0001), 0.9999)
        return math.log(bw/(1.0-bw))
        
    def abw_score(self):
        """calculates analytic best-worst score (Marley, Islam, & Hawkins, 2016)
        """
        ratio = (self.best - self.worst) / float(self.trials)
        # to avoid div0 errors
        ratio = min(max(ratio, -0.9999), 0.9999)
        
        NUM = 1.0 + ratio
        DEN = 1.0 - ratio
        return math.log(NUM/DEN)

    def value_logit_score(self):
        # to avoid div0 errors
        value = min(max(self.value,0.0001), 0.9999)
        return math.log(value/(1.0-value))

    def reswag_score(self):
        """calculates rescorla-wagner score based on associations with win
           and loss outcomes
        """
        if self.reswag_win + self.reswag_lose == 0:
            win_weight = 0.5
        else:
            win_weight = self.reswag_win / (self.reswag_win + self.reswag_lose)
        return win_weight

    def reswag_logit_score(self):
        """logit-adjusted rescorla-wagner score
        """
        rw = self.reswag_score()
        # to avoid div0 errors
        rw = min(max(rw, 0.0001), 0.9999)
        return math.log(rw/(1.0-rw))

    def elo_logit_score(self, eloMin, eloMax):
        """Calculates the logit elo value after scaling between min and max
           elo values.
        """
        scaleelo = (self.elo - eloMin) / (eloMax-eloMin)
        # avoid div0 errors
        scaleelo = min(max(scaleelo, 0.0001), 0.9999)
        return math.log(scaleelo / (1.0 - scaleelo))
        
        
        
################################################################################
# SUPPORT FUNCTIONS
################################################################################
def parse_bestworst_data(file, bestCol="best", worstCol="worst", sep=None):
    """parses best-worst data from file, where each trial is returned as tuple:
         (best, worst, (unchosen1, unchosen2, ..., unchosen[K-2]))

       A list of parsed trials is returned.
    """
    # figure out our seperator first
    if sep == None and file.endswith(".tsv"):
        sep = "\t"
    elif sep == None:
        sep = ","

    # read in the trials
    ss = Spreadsheet.read_csv(file, delimiter=sep)
    trials = [ ]
    for row in ss:
        # read best and worst choices
        best  = row[bestCol]
        worst = row[worstCol]
        opts  = [ ]

        # read all options that were choosable
        i = 1
        while True:
            col = "option%d" % i
            if col in ss.header:
                opts.append(row[col])
                i  += 1
            else:
                break

        # strip best and worst choices from the list of other options
        if best in opts:
            opts.remove(best)
        if worst in opts:
            opts.remove(worst)

        trials.append((best, worst, tuple(opts)))

    # return the parsed trials
    return trials

def compile_pairings(trials):
    """Takes a list of trials in the format (best, worst, (others)) and 
       generates win/loss pairings based on the trial. Pairings are always
       returned as a tuple in the format (winner, loser)
    """
    pairings = [ ]
    for trial in trials:
        best, worst, others = trial

        pairings.append((best,worst))
        for other in others:
            pairings.append((best,other))
            pairings.append((other,worst))
    return pairings

def run_error_correction_scoring(item_data, pairings, iters=100):
    """run our various error-correction scoring methods on entries in item_data
       according to the (winner, loser) pairings supplied. Makes changes to
       item_data in place, and returns the results as well.
    """
    # repeat iter number of times
    for i in range(iters):
        # shuffle our data to eliminate order effects
        random.shuffle(pairings)

        # register a pairing in the item data
        for winner,loser in pairings:
            winner_data, loser_data = item_data[winner], item_data[loser]
            winner_data.win(loser_data, iteration=(i+1))

    # values were updated in-place; return original data structure
    return item_data

def score_trials(trials, methods, iters=100, dummy=True):
    """The wrapper function for scoring trials. Parameters are:
         iters   = for error-correction methods (elo, Value, RescorlaWagner),the
                   number of iterations over the data to perform when scoring.
         dummy   = Whether always-win and always-lose dummy players should be
                   added to keep items in a bounded range for error-correction
                   methods. Highly suggested.
         methods = The different scoring methods to apply.
    """
    # first, extract out all of our unique items
    items = set()
    for trial in trials:
        best, worst, others = trial
        items.add(best)
        items.add(worst)
        for other in others:
            items.add(other)

    # create data for each item
    item_data = { }
    for item in items:
        item_data[item] = ItemEntry(item)

    # calculate scores from count-based methods 
    for trial in trials:
        winner, loser, others      = trial
        item_data[winner].best    += 1
        item_data[loser].worst    += 1
        for item in (winner, loser) + others:
            item_data[item].trials += 1
        # track how many unranked MATCHES (not TRIALS) we had, used for
        # PAIRINGS methods
        for item in others:
            item_data[item].unranked += len(others)-1

    # now that count-based methods are done, use error-correction methods for
    # scoring. We need to reformat trials into a series of pairings where we
    # know winners and losers, and then calculate scores based on match wins
    # and losses. See Hollis (2017; reference in file header) for details.
        
    # generate pairings from trials
    pairings = compile_pairings(trials)
        
    # if we have dummy players, add those as well. Also add pairings for each
    # item and the two dummies.
    if dummy == True:
        BEST_WINNER = object()
        WORST_LOSER = object()
        item_data[BEST_WINNER] = ItemEntry(BEST_WINNER)
        item_data[WORST_LOSER] = ItemEntry(WORST_LOSER)
        for item in items:
            pairings.append([BEST_WINNER, item])
            pairings.append([item, WORST_LOSER])

    # apply our various error-correction scoring methods
    item_data = run_error_correction_scoring(item_data, pairings, iters=iters)
    return item_data
