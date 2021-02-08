# This file is part of the concealSATgen project.
# Copyright (c) 2021 Jan-Hendrik Lorenz and Florian Wörz
# Institute of Theoretical Computer Science
# Ulm University, Germany


# Import standard python modules
import argparse
import random
import os
import sys

# Import own modules
import cnfformula
import sample_clauses as sample_clauses
import hash_clauses as hash_clauses


def main(n, m, k=None, p=None, s=None, F=None, o=None):
    """Builds random CNF formula with :math:`m` clauses
    over :math:`n` variables, each of width :math:`k`.
    The sampling of the clauses is done uniformly at random,
    such that $:math:`p_i` is the probability to add a sampled clause
    that contains :math:`i` satisfied literals under the hidden solution,
    and such that duplicate clauses will not be added twice to the formula.

    Parameters
    ----------
    n : int
        number of variables to choose from

    m : int
        number of clauses to generate

    k : int, optional (standard: k = 3)
        width of each clause

    p : list of floats, optional (standard: p = [1.00] * k)
	    :math`p_i`-values

    s : int, optional (standard: s = 42)
        seed of the random generator

    F : str, optional (standard behaviour: hidden solution will be generated randomly)
        path to the file with contains the wanted hidden solution

    o : str, optional (standard: o = './')
        output path of the DIMACS file

    Raises
    ------
    TypeError
        when n is not passed
        when m is not passed

    ValueError
        when n < 0
        when m < 0
        when k > n
        when len(p) != k
        when any(val > 1.0 for val in p)
        when any(val < 0.0 for val in p)
        when not any(val > 0.0 for val in p)
        if there are fewer clauses available than the number requested (this may take quite some time!)

    FileNotFoundError
        if the specified hidden solution file does not exist   

    Exception
        when there occurs some other error while trying to open the hidden solution file
        if hidden solution has different amount of entries than specified number of variables
        if the hidden solution contains duplicate entries
        if the hidden solution contains inconsistent entries (i.e., some i  and -i)
    """

    # -------------------------------------------------------------------------------------------

    # We want to write the call that was made to execute the program to the generated file.
    # Furthermore, the header of the generated file should contain the p-values used during generation.
    # We keep track of these facts to ensure reproducability of a given file.
    terminalstring = "Created by calling python3 generator.py"
    pvaluestring = ""

    #
    # Check what parameters are given and create header string
    #

    if n is None:
        raise ValueError("Please pass parameter n.")
    else:
        terminalstring += " -n " + str(n)


    if m is None:
        raise ValueError("Please pass parameter m.")
    else:
        terminalstring += " -m " + str(m)


    if k is None:
        k = 3 # set the standard value for k
    else:
        terminalstring += " -k " + str(k)


    if p is None:
        p = [1.00] * k # set the standard list for p
        pvaluestring = "1.00 " * k
        pvaluestring = pvaluestring[:-1] # do not include the last space
    else:
        terminalstring += " -p "
        for entry in p:
            terminalstring += str(entry) + " "
            pvaluestring += str(entry) + " "
        terminalstring  = terminalstring [:-1] # remove last space
        pvaluestring = pvaluestring[:-1] # remove last space


    if s is None:
        s = 42 # set the standard seed
    else:
        terminalstring += " -s " + str(s)

    random.seed(s)


    if F is not None:
        terminalstring += " -F " + F 


    if o is None:
        o = './' # set the standard output directory
    else:
        terminalstring += " -o " + o 

    # -------------------------------------------------------------------------------------------

    #
    # Check for Errors
    #

    if n<0 or m<0:
        raise ValueError("Parameters either not passed or negative.")

    if k<=0:
        raise ValueError("Parameters must be non-negatives.")

    if k>n:
        raise ValueError("Clauses cannot have more than {} literals.".format(n))


    if len(p) != k:
        raise ValueError("Length of list of p-values does not match k.")

    p = [float(value) for value in p]

    if any(val > 1.0 for val in p):
        raise ValueError("All p-values must be <= 1.0")

    if any(val < 0.0 for val in p):
        raise ValueError("All p-values must be >= 0.0")

    if not any(val > 0.0 for val in p):
        raise ValueError("Some p-values must be > 0.0")

    # -------------------------------------------------------------------------------------------

    #
    # Take care of the hidden solution
    #

    if F is None:
        # No hidden solution given. Create a random one
        hiddensol_listint = []
        hiddensol_string = ""

        for i in range(1,n+1):
            variable = i
            flip = random.randint(0, 1)
            if (flip == 0):
                hiddensol_listint.append(variable)
                hiddensol_string += str(variable) + " "
            else:
                hiddensol_listint.append(-variable)

    else:
        # trying to open a file (might not exist)
        try:
            #trying to open a file in read mode
            f = open(F,"rt")
        except FileNotFoundError:
            raise FileNotFoundError("Hidden Solution file does not exist")
        except:
            raise Exception("Other error while trying to open the hidden solution file")


        hiddensol_string = f.read().replace('\n', '')
        hiddensol_listint = list(map(int, hiddensol_string.split()))

        f.close()

        #
        # Check errors in hidden solution
        #

        highest_var_in_hidden_sol = abs(max(hiddensol_listint, key=abs))

        # Check if hidden solution has different amount of entries than specified number of variables
        if highest_var_in_hidden_sol != n:
            raise Exception("Number of variables in hidden solution does not match requested n.")

        # Check if the hidden solution contains duplicate entries
        if len(set(hiddensol_listint)) < len(hiddensol_listint):
            raise Exception("Hidden solution contains duplicate entries")

        # Check for inconsistent entries (if i in hiddensol_list and -i in hiddensol_list)
        if len(set(list(map(abs, hiddensol_listint)))) != len(hiddensol_listint):
            raise Exception("Hidden solution contains inconsistent entries")

    # Create a dict with the hidden solution
    hiddensol_string = ""
    for hid in hiddensol_listint:
        if hid > 0:
            hiddensol_string += str(hid) + " "
    hiddensol_string = hiddensol_string.rstrip(" ")
    hidden = {abs(var) : True if var > 0 else False for index, var in enumerate(hiddensol_listint)}


    # -------------------------------------------------------------------------------------------

    # Create the CNF object
    F = cnfformula.CNF(n)

    t = 0

    # Add the clauses to the formula
    try:
        hash_clauses.init_variable_mapping(n)
        condition = True
        while condition:
            t+=1
            # important to try different seeds if try was not sucessful
            variables, clauselist = sample_clauses.sample_clauses(k, n, m, hidden, s+t, p)
            # Check if all variables were used
            if len(variables) != n:
                continue

            F = cnfformula.CNF(n)
            
            for clause in clauselist:
                F.add_clause(clause)
            
            condition = False


    except ValueError:
        raise ValueError("There are fewer clauses available than the number requested")

    # -------------------------------------------------------------------------------------------

    # Make sure the output-path o exists
    os.makedirs(o, exist_ok=True)

    # Generate the potential filename to save later  
    file_name = f"gen_n{n}_m{m}_k{k}SAT_seed{s}.cnf"

    # Set the header of the CNF formula, that will be printed after the "c" in DIMACS
    F.header = "This file was generated by concealSATgen\n"\
    + terminalstring + "\n"\
    + f"Hidden solution: {hiddensol_string}\n"\
    + "p-values " + pvaluestring

    # Create the file and write the DIMACS content
    f2 = open(f"{o}/{file_name}", "w")
    f2.write( F.dimacs() )
    f2.close()

###################################################################################

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Creates a random CNF formula with hidden solution as specified by arguments.')
    parser.add_argument("-n", type=int, default=None, help="Specifies the number of variables in the formula.")
    parser.add_argument("-m", type=int, default=None, help="Specifies the number of clauses in the formula.")
    parser.add_argument("-k", type=int, default=None, help="Specifies the k-value of the formula.")
    parser.add_argument("-p", default=None, nargs='+', help="Specify the p-values as described in the paper.....") # Do not use typ=list with nargs='+'!!!!!
    parser.add_argument("-s", type=int, default=None, help="The seed to initialize the random number generator.")
    parser.add_argument("-F", type=str, default=None, help="The path to the file with contains the wanted hidden solution.")    
    parser.add_argument("-o", type=str, default=None, help="The output-path to save the generated cnf-file.")
    args = parser.parse_args()

    main(args.n, args.m, k=args.k, p=args.p, s=args.s, F=args.F, o=args.o)
