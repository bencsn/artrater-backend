"""
trialgen.py

Various methods for generating best-worst trials from a list of items.

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
import random
import itertools


def build_trials_even_bigram_norepeat(items, N=1, K=4):
    """Builds N trials with K items each.

       ensures any 2 pairs of items do not repeat, and that each item appears
       an equal number of times.

       This is the suggested algorithm to use, unless you have a very large
       dataset (10k+ items). Then, reduce the restriction of repeating bigrams
       for computational efficiency and run build_trials_even.
    """
    items_orig = [w for w in items]
    if (N * K) % len(items) != 0:
        raise Exception(
            "For an even design, trials * K MOD items must equal 0.")
    trials_per_batch = len(items) / K
    batches = int(N / trials_per_batch)
    trials = []
    pairs = set()

    for i in range(batches):
        items = [w for w in items_orig]
        random.shuffle(items)

        fails = 0
        while len(items) > 0:
            trial = tuple(items[:K])
            combos = [c for c in itertools.combinations(trial, 2)]
            unique = sum([p in pairs for p in combos]) == 0

            if unique == True or fails >= 20:
                for c in combos:
                    pairs.add(c)
                trials.append(list(trial))
                items = items[K:]
                fails = 0
            else:
                random.shuffle(items)
                fails += 1
    return trials


def build_trials_even(items, N=1, K=4):
    """Builds N trials with K items each.

       Ensures each item appears an equal number of times.
    """
    if (N * K) % len(items) != 0:
        raise Exception("For an even design, trials * K % items must equal 0.")
    trials_per_batch = len(items) / K
    batches = int(N / trials_per_batch)
    trials = []
    for i in range(batches):
        items_copy = [w for w in items]
        random.shuffle(items_copy)
        while len(items_copy) > 0:
            trials.append(items_copy[:K])
            items_copy = items_copy[K:]
    return trials


def build_trials_random(items, N=1, K=4):
    """Builds N trials with K items each.

       Items are randomly pulled for each trial.
    """
    trials = []
    for i in range(N):
        trials.append(random.sample(items, K))
    return trials


def build_trials_random_bigram_norepeat(items, N=1, K=4):
    """Builds N trials with K items each.

       ensures any 2 pairs of items do not repeat, but items are randomly
       selected with no guarantee of an even number of appearances of each
       item. 
    """
    pairs = set()

    trials = []
    while len(trials) < N:
        sample = tuple(random.sample(items, K))

        # build the pairlist
        combos = [c for c in itertools.combinations(sample, 2)]
        unique = sum([p in pairs for p in combos]) == 0

        if unique == True:
            trials.append(list(sample))
            for c in combos:
                pairs.add(c)
    return trials


def build_trials_semirandom(items, N=1, K=4, even_pct=0.5):
    """forces some number of batches to be evenly distributed, but everything
    else is random.
    """
    trials_per_batch = len(items) / K
    t_even = build_trials_even(items, int(N * even_pct), K)
    t_random = build_trials_random(items, int(N*(1.0 - even_pct)), K)
    return t_even + t_random
