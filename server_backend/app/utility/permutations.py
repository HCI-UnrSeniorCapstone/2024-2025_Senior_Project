import json
import random
import time
from itertools import product, permutations, combinations
from hashlib import sha256
from math import factorial
from collections import Counter


# Converting to a hash value so we can make quick comparisons to check for uniqueness amongst possible perms
def calc_perm_hash(trial_sequence):
    return sha256(json.dumps(trial_sequence).encode()).hexdigest()


# Finding num unique permutations from a possibly non-distinct list of trials
def calc_unique_perms(elements):
    denominator = 1
    counts = Counter(elements)
    n = sum(counts.values())
    for count in counts.values():
        denominator *= factorial(count)
        
    return factorial(n) // denominator


def generate_perm(unique_trial_options, trial_count, unique_requested, used_perms, iterations_needed = 1):
    unique_trial_count = len(unique_trial_options)
    
    base_pool = unique_trial_options * (trial_count // unique_trial_count)
    
    unbalanced_trial_count = trial_count % unique_trial_count
    unbalanced_trial_combos = [()]
    
    if unbalanced_trial_count > 0:
        unbalanced_trial_combos = list(combinations(unique_trial_options, unbalanced_trial_count))
    
    # Do not have to worry about permutation reuse here - easy
    if not unique_requested:
        rand_combo = random.choice(unbalanced_trial_combos)
        full_pool = base_pool + list(rand_combo)
        random.shuffle(full_pool)
        return full_pool, 'success'

    # Quick check to see if exhausted all possible unique trials before searching for unique perms which is computationally expensive
    sample_pool = base_pool + list(random.choice(unbalanced_trial_combos))
    max_unique_perms = (calc_unique_perms(sample_pool) * len(unbalanced_trial_combos)) * iterations_needed
    num_unique_used_perms = len(set(used_perms))
    print(f"Unique Possibilities: {max_unique_perms}")
    if num_unique_used_perms >= max_unique_perms:
        return None, 'exhausted'

    # For short sequence lengths, generating all perms upfront is not too expensive and better when searching for an unused one
    if trial_count <= 4:
        for combo in unbalanced_trial_combos:
            full_pool = base_pool + list(combo)
            
            all_perms = list(permutations(full_pool))
            
            for perm in all_perms:
                perm_hash = calc_perm_hash(perm)
                
                if perm_hash not in used_perms:
                    return list(perm), 'success'

    # Too expensive to compute all perms, but with a large pool of possible perms we can generate them at random and likely find a unique one quickly
    else:
        start_time = time.time()
        timeout = 5
        attempts = 0
        while time.time() - start_time < timeout:
        # while attempts < 5: # Testing purposes
            rand_combo = random.choice(unbalanced_trial_combos)
            
            full_pool = base_pool + list(rand_combo)
            random.shuffle(full_pool)
            perm_hash = calc_perm_hash(full_pool)
            
            if perm_hash not in used_perms:
                return full_pool, 'success'
        
            attempts += 1
            print(f"searching again... (attempt {attempts})")
    
    return None, 'timeout'


def get_within_perm(tasks, factors, trial_count, unique_requested, used_perms):
    unique_trial_options = list(product(tasks, factors))
    within_perm, status = generate_perm(unique_trial_options, trial_count, unique_requested, used_perms, 1)
    
    if status == 'exhausted':
        # Default to returning a non-unique random perm since all unique options used already 
        within_perm, status = generate_perm(unique_trial_options, trial_count, False, used_perms, 1)
        return within_perm, 'exhausted_fallback'
    
    if status == 'timeout':
        # Failed to find a unique perm not due to exhaustion but timeout, so rollback to returning a default
        within_perm, status = generate_perm(unique_trial_options, trial_count, False, used_perms, 1)
        return within_perm, 'timeout_fallback'
    
    if status == 'success':
        return within_perm, 'success'


def get_between_perm(tasks, factors, trial_count, unique_requested, used_perms):
    unchecked_factors = factors.copy()
    random.shuffle(unchecked_factors)
    num_factors_to_check = len(factors)
    
    all_factors_exhausted = True
    timeout_occured = False
    
    # Have to loop through and check factor-by-factor since only 1 in a trial pool at a time 
    while unchecked_factors:
        index = random.randrange(len(unchecked_factors))
        rand_factor = unchecked_factors.pop(index)
        
        unique_trial_options = list(product(tasks, [rand_factor]))
        between_perm, status = generate_perm(unique_trial_options, trial_count, unique_requested, used_perms, num_factors_to_check)
        
        if status == 'success':
            return between_perm, 'success'
        
        elif status == 'timeout':
            timeout_occured = True
            all_factors_exhausted = False
        
        elif status == 'exhausted':
            continue
        
        else: # Different error occured 
            all_factors_exhausted = False
        
    # Failed to find a unique perm so default to a perm that may not be unique (grab first one generated)
    fallback_factor = random.choice(factors)
    fallback_trials = list(product(tasks, [fallback_factor]))
    fallback_perm, _ = generate_perm(fallback_trials, trial_count, False, used_perms, 1)
    
    if all_factors_exhausted:
        return fallback_perm, 'exhausted_fallback'
    elif timeout_occured:
        return fallback_perm, 'timeout_fallback'
    else:
        return fallback_perm, 'error'


if __name__ == "__main__":
    # Sample values for the time being
    task_list = [1, 2] # These are example ids 
    factors_list = [3, 4]
    study_type = 'Within'
    trial_count = 4
    used_perms = set()
    unique_perm_requested = True
    
    for i in range(25):
        if study_type == 'Within':
            perm, status = get_within_perm(task_list, factors_list, trial_count, unique_perm_requested, used_perms)
        else:
            perm, status = get_between_perm(task_list, factors_list, trial_count, unique_perm_requested, used_perms)

        print(f"Perm Generated: {perm} \t Status: {status}")
        
        perm_hash_val = calc_perm_hash(perm)
        used_perms.add(perm_hash_val)
