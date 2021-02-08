# This file is part of the concealSATgen project.
# Copyright (c) 2021 Jan-Hendrik Lorenz and Florian Wörz
# Institute of Theoretical Computer Science
# Ulm University, Germany


# Import standard python modules
import random
import itertools

# Import own modules
from hash_clauses import hash_clause



def unfair_coin_flip(p):
    """Given a float p in the range [0,1), this function will return True with probability p, and False otherwise.
    """
    return True if random.random() < p else False
    # random.random() returns a uniformly distributed pseudo-random floating point number in the range [0, 1).
    # This number is less than a given number p in the range [0,1) with probability p.


def number_of_satisfied_literals(clause, assignment):
    """Given a clause and an assignment, this function calculated the number of satisfied literals
    in the clause w.r.t. the assignment.
    """
    satisfied_lits = [var in assignment and polarity == assignment[var] for (polarity, var) in clause]
    return sum(satisfied_lits)

    
def sample_clauses(k, n, m, hidden_solution, s, p):
    """Create a sampled list of m clauses of width k with with variables 1,...,n,
    that are satisfied by the hidden_solution and are added to the list according
    to the list p (where the i-th entry specifies the probability that a clause
    with i satisfied literals under the hidden_solution gets added to the list).
    """ 

    random.seed(s)

    clauses = []
    
    highestvariablecreated = 0

    variableset = set()
    clause_hash_set = set()
    
    while len(clauses) < m:
        clause = tuple((random.choice([True,False]),i)
                       for i in random.sample(range(1,n+1),k))        

        i = number_of_satisfied_literals(clause, hidden_solution)

        if i > 0 and unfair_coin_flip(p[i-1]) == True:
            hash_value = hash_clause(clause)
            if hash_value in clause_hash_set:
                continue # clause is already present            

            clause_hash_set.add(hash_value)
            maxtupel = max(clause, key = lambda x: x[1])

            if maxtupel[1] > highestvariablecreated:
                highestvariablecreated = maxtupel[1]

            for tuples in clause:
                variableset.add(tuples[1])

            clauses.append(clause)

    return variableset, clauses
