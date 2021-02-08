"""This class is a *very basic* way of building and manipulating CNF formulas and helps to output them in the DIMACS-format.
This file is part of the concealSATgen project.
Copyright (c) 2021 Jan-Hendrik Lorenz and Florian Wörz
Institute of Theoretical Computer Science
Ulm University, Germany
"""

class CNF(object):
	def __init__(self, n):
	# Initial the CNF is empty
		self.clauses = []
		self.n = n
		self.header = "Default header"

	#
	# Implementation of class methods
	#

	def __len__(self):
		"""Number of clauses in the formula
		"""
		return len(self.clauses)

	#
	# Methods for building the CNF
	#

	def add_clause(self, clause):
		"""Adds a clause to the CNF object.
		"""
		if not hasattr(clause, '__iter__'):
			raise TypeError("Invalid clause. A clauses must be iterable.")
		if not all((type(lit) is int) and (type(truth) is bool) for (truth, lit) in clause):
			raise TypeError("All literals have to be integers.")
		if any((lit > self.n) or (lit == 0) for (_, lit) in clause):
			raise ValueError(f"Invalid clause. The clause may only contain positive/negative integers up to {self.n}/{-self.n}.")
		if len( set( [lit for (_, lit) in clause] ) ) != len(clause):
			raise ValueError("This class does not accept tautological clauses or clauses with reappearing literals.")
		
		clause_list = [lit if truth else -lit for (truth, lit) in clause]
		self.clauses.append(clause_list)




	def dimacs(self):
		"""Converts the CNF file to the DIMACS format.
		"""
		output = ""
		# Write header
		for header_line in self.header.split("\n"):
			output += "c " + header_line + "\n"
	
		# Write formula specification
		output += f"p cnf {self.n} {len(self.clauses)}\n"
		
		# Write clauses
		for cls in self.clauses:
			clause_string = ' '.join([str(lit) for lit in cls])
			clause_string += " 0\n"
			output += clause_string

		return output
