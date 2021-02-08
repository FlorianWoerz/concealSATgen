# This file is part of the concealSATgen project.
# Copyright (c) 2021 Jan-Hendrik Lorenz and Florian Wörz
# Institute of Theoretical Computer Science
# Ulm University, Germany


# Import standard python modules
import random



variable_mapping = {}

def init_variable_mapping(n, seed=42):
    """
    This method initializes the variable mapping. Each literal is uniquely mapped to a randomly chosen value in {0, ..., 2^32 - 1}.
    Parameter n: The number of variables.
    """
    rng = random.Random()
    rng.seed(seed)
    sample = random.sample(range(2**32-1), 2*n)
    i = 0
    for l in range(1, n+1):
        variable_mapping[(True, l)] = sample[i]
        variable_mapping[(False, l)] = sample[i+1]
        i += 2
    
def hash_clause(clause):
    """
    This method calculates the sum of literals of a clause w.r.t. the above variable mapping.
    Parameter clause: The clause is a list of the form [(Boolean, int)]. The Boolean describes the polarity of the literal. 
    """
    return sum(map(lambda x: variable_mapping[x], clause))
