# This file contains the unit test for the script `generator.py`.
# This file is part of `concealSATgen`.
# Copyright (c) 2021 Jan-Hendrik Lorenz and Florian Wörz.
# Institute of Theoretical Computer Science
# Ulm University, Germany

import unittest
import os, glob
import filecmp
from shutil import rmtree, copy2
from scipy.stats import chisquare

import sys
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)

from random import randint, seed, uniform

import generator as g

# Specify the folderpaths used during testing
tmpfolder = "./tmp_test"
tmpcopyfolder = "./tmp_test_copy"
nonexistingfolder = "./temporary_test_folder_non_existant"

class TestGenerator(unittest.TestCase):

	def setUp(self):
		"""This setUp procedure will be called before every test.
		Ensures that no cnf-files exist in the base folder.
		Ensures that the folders `tmp_test` and `tmp_test2` exists. 
		These folders will be used for some tests.

		Creates the file `hidden.solution` in the base folder.
		This file contains the solution "1 -2 3 -4 5 ... 99 -100".      

		Additionally, a file `hidden2.solution` will be created.
		This file contains line breaks in the solution.
		The solution itself will be randomly generated.
		For this, variables between 1 and 1000 will be used.
		"""

		for f in glob.glob("./gen*.cnf"):
			os.remove(f)

		os.makedirs(tmpfolder, exist_ok=True)
		os.makedirs(tmpcopyfolder, exist_ok=True)

		with open("hidden.solution", "w") as hidden_sol:
			sol = ""
			for i in range(1, 101):
				if i % 2 == 0:
					sol += "-"
				sol += str(i)+" "
			hidden_sol.write(sol[:-1]) # do not write the last " "        
		
		seed()
		self.hidden2 = [] # The second hidden solution will additionaly be safed in a list.
		with open("hidden2.solution", "w") as hidden_sol:
			sol = ""            
			# Count the amount of positive literals in the solution with a counter variable.
			# This measure is used to randomly include line breaks.
			# The beginning of the file `hidden2.solution` might look something like this:
			#    -1 
			#    -2 
			#    3 -4 -5 -6 7 -8 9 10 11 -12 13 -14 15 16 17 18 
			#    19 -20 21 22 23 24 -25 26 27 -28 -29 -30 31 32 -33 -34 35 
			#    36 -37 -38 -39 40 41 42 43 44 45 46 -47 -48 49 -50 -51 52 
			#    -53 
			#    54 -55 -56 57 -58 59 -60 -61 -62 -63 64 65 -66 67 68 69 -70 -71 -72 73 74 
			#    -75 
			counter = 0 
			for i in range(1, 1001):
				# Choose randomly 0 or 1.
				# If rand == 1, the variable i will be added positively to the solution.
				# Otherwise, we will include -i as part of the hidden solution.                
				rand = randint(0,1)
				if rand == 1:
					counter += 1
					sol += str(i)+" "
					self.hidden2.append(i)
				else:
					sol += "-"+str(i)+" "
				# Add the random line breaks:
				if counter % 10 == 0:
					sol += "\n"
			hidden_sol.write(sol[:-1]) # do not write the last " "


		
	def tearDown(self):
		"""Will be executed after every test.
		Ensures that all cnf-files that were generated during the test will be deleted after the test.
		Ensures that all temporary test folder will be deleted.
		Additionally, the files `hidden.solution` and `hidden2.solution` will be deleted.
		"""

		rmtree(tmpfolder)
		rmtree(tmpcopyfolder)
		rmtree(nonexistingfolder, ignore_errors=True) # this folder does only get generated during one test

		os.remove("hidden.solution")
		os.remove("hidden2.solution")

		for f in glob.glob("./gen_*.cnf"):
			os.remove(f)



	def test_okay(self):
		"""Test if the test framework works propertly by doing a very simple test.
		"""

		print(sys._getframe(  ).f_code.co_name)
		self.assertTrue(True)
		print("Test Framework okay.")
		print("Started from " + os.getcwd())


	
	def test_p_values(self):
		"""In this this test we check if invalid p-values will be declined.
		There are the following sources of error:
		1) A list of p-values was given but the length of this list is smaller than k.
		2) A list of p-values was given but
		   a) some entry is > 1.0, or
		   b) some entry is < 0.0, or
		   c) no entry is > 0.0.
		"""

		print(sys._getframe(  ).f_code.co_name)

		n = 1000
		m = 4000
		o = tmpfolder

		# The standard case is k=3. We pass a p-value list with only two entries.
		# This should raise a ValueError.
		p = [0.3, 0.5]        
		with self.assertRaises(ValueError):
			g.main(n, m, p=p, o=o)

		# We also pass a list with too many entries. We expect a ValueError.
		p = [0.5, 0.3, 0.2, 0.1]
		with self.assertRaises(ValueError):
			g.main(n, m, p=p, o=o)
		

		# What happens when there is a p-value > 1.0? We again expect a ValueError.
		p = [0.3, 1.2, 0.5]
		with self.assertRaises(ValueError):
			g.main(n, m, p=p, o=o)
			
		# And what if there is a p-value < 0.0?
		p = [0.0, 1.0, -0.5]
		with self.assertRaises(ValueError):
			g.main(n, m, p=p, o=o)

		# Does the programm accept lists where no entry is > 0.0?
		p = [0.0, 0.0, 0.0]
		with self.assertRaises(ValueError):
			g.main(n, m, p=p, o=o)


			
	def test_valid_parameters(self):
		"""This test veryfies that only valid parameter combinations will be accepted.
		"""

		print(sys._getframe(  ).f_code.co_name)

		o = tmpfolder

		# Test if we can generate files without passing the required positional arguments `n` and `m`.
		with self.assertRaises(TypeError):
			g.main(o=o)

		with self.assertRaises(TypeError):
			g.main(n=30, o=o)

		with self.assertRaises(TypeError):
			g.main(m=90, o=o)

		# Test whether negative n-values will be declined.
		n = -1000
		m = 4000        
		with self.assertRaises(ValueError):
			g.main(n, m, o=o)
		
		# Test whether negative m-values will be declined.
		n = 1000
		m = -4000
		with self.assertRaises(ValueError):
			g.main(n, m, o=o)

		# Test whether k-values smaller or equal than 0 will be declined.
		m = 4000
		k = 0
		with self.assertRaises(ValueError):
			g.main(n, m, k=k, o=o)

		# Check if a non-existing file will be accepted as a hidden solution.
		k = 3
		F = os.path.join(tmpfolder, "hid.sol")
		with self.assertRaises(FileNotFoundError):
			g.main(n, m, k=k, o=o, F=F)



	def calculate_file_name(self, n, m, k=3, s=42):
		"""Given the parameters `n`, `m`, `k` (optional, standard 3), `s` (optional, standard 42),
		this method returns the correct file name of the file generated with these parameters as a string.
		"""
		return f"gen_n{n}_m{m}_k{k}SAT_seed{s}.cnf"



	def test_generated_name(self):
		"""Checks if the generated file have the correct filename.
		Checks if the files are in the correct folders as well.
		"""

		print(sys._getframe(  ).f_code.co_name)

		# First, let's check if the file gets generated in the base folder if no output folder is specified.
		# The files then should be generated in "./".

		# The filename should read "gen_n100_m420_k3SAT_seed42.cnf".
		n = 100
		m = 420
		path = os.path.join('./', self.calculate_file_name(n, m))
		g.main(n, m)
		self.assertTrue(os.path.isfile(path))
		os.remove(path)

		# The filename should read "gen_n100_m420_k6SAT_seed42.cnf".
		n = 100
		m = 420
		k = 6
		path = os.path.join('./', self.calculate_file_name(n, m, k=k))
		g.main(n, m, k=k)
		self.assertTrue(os.path.isfile(path))
		os.remove(path)

		# The filename should read "gen_n999_m9090_k9SAT_seed1909.cnf".
		n = 999
		m = 9090
		k = 9
		s = 1909
		path = os.path.join('./', self.calculate_file_name(n, m, k=k, s=s))
		g.main(n, m, k=k, s=s)
		self.assertTrue(os.path.isfile(path))
		os.remove(path)


		# The parameters `p` and `F` should have no influence on the filename.

		# Here, only the influence of `p` gets tested.
		n = 999
		m = 9090
		k = 9
		p = [0.1*c for c in range(1,k+1)]
		s = 1909
		path = os.path.join('./', self.calculate_file_name(n, m, k=k, s=s))
		g.main(n, m, k=k, p=p, s=s)
		self.assertTrue(os.path.isfile(path))
		os.remove(path)

		# Here, only the `F` parameter gets tested.
		n = 1000
		m = 9090
		k = 9
		F = './hidden2.solution'
		s = 123
		path = os.path.join('./', self.calculate_file_name(n, m, k=k, s=s))
		g.main(n, m, k=k, s=s, F=F)
		self.assertTrue(os.path.isfile(path))
		os.remove(path)

		# Finally, both parameters get tested.
		n = 1000
		m = 9090
		k = 3
		p = [0.25*c for c in range(1,k+1)]
		s = 123
		F = './hidden2.solution'
		path = os.path.join('./', self.calculate_file_name(n, m, k=k, s=s))
		g.main(n, m, k=k, p=p, s=s, F=F)
		self.assertTrue(os.path.isfile(path))
		os.remove(path)


		# Do the files get created properly in the specified output path?

		# Note, that the folder `./tmp_test` already exists (see setUp method).
		# To begin with, it gets tests if the program passes if
		# the output folder gets specified as `./tmp_test`.
		n = 1300
		m = 4201
		k = 5
		p = [0.16, 0.32, 0.64, 0.1, 0.00]
		s = 9
		o = tmpfolder
		path = os.path.join(o, self.calculate_file_name(n, m, k=k, s=s)) 
		g.main(n, m, k=k, p=p, s=s, o=o)
		self.assertTrue(os.path.isfile(path))
		os.remove(path)

		# Next, we test what happens if the folder gets specified as `./tmp_test/`
		# (notice the additional / at the end of the string!).
		o = tmpfolder
		g.main(n, m, k=k, s=s, o=o)
		self.assertTrue(os.path.isfile(path))
		os.remove(path)

		# Finally, we test what happens if a non-existing folder gets passed.
		# The folder `nonexistingfolder` does not exist.
		o = f'./{nonexistingfolder}/tmp'
		path = os.path.join(o, self.calculate_file_name(n, m, k=k, s=s)) 
		g.main(n, m, k=k, s=s, o=o)
		self.assertTrue(os.path.isfile(path))
		os.remove(path)



	def test_reproducibility(self):
		"""Here, it gets tested whether two calls with identical seeds also deliver identical files.
		This test generates one file in `./tmp_test` and copies it to `./tmp_test2`.
		The file then gets generated again in `./tmp_test` and gets compared to the one in `./tmp_test2`.
		"""        
		print(sys._getframe(  ).f_code.co_name)

		# First test:
		n = 100
		m = 420

		filename = self.calculate_file_name(n, m)
		path1 = os.path.join(tmpfolder, filename) 
		path2 = os.path.join(tmpcopyfolder, filename) 

		g.main(n, m, o=tmpfolder)
		copy2(path1, path2)
		g.main(n, m, o=tmpfolder)
		# filecmf.cmp(_,_) checks if two files are identical.
		# However, only statistics (hash values, etc.) get compared.
		# For a byte-by-byte check one has to set shallow=False.
		self.assertTrue(filecmp.cmp(path1, path2))     


		# We run a second test including a hidden solution and all parameters.
		n = 1000
		m = 9999
		k = 8
		p = [0.3, 0.1, 0.5, 0.1, 0.3, 0.0, 0.7, 0.01]
		s = 9
		F = './hidden2.solution'

		filename = self.calculate_file_name(n, m, k=k, s=s)
		path1 = os.path.join(tmpfolder, filename) 
		path2 = os.path.join(tmpcopyfolder, filename) 

		g.main(n, m, k=k, p=p, s=s, F=F, o=tmpfolder)
		copy2(path1, path2)
		g.main(n, m, k=k, p=p, s=s, F=F, o=tmpfolder)
		self.assertTrue(filecmp.cmp(path1, path2))


		
	def get_header(self, filename, n_lines):
		"""This method reads the first `n_lines` of the file specified in `filename`
		and returns them as a list."""        
		lines = []
		with open(filename, 'r') as file:
			for _ in range(n_lines):
				lines.append(file.readline())
		return lines        



	def get_all_lines(self, filename):
		"""This method returns all lines of the given file as a list.
		"""
		with open(filename, 'r') as file:
			lines = file.readlines()
		return lines



	def test_header(self):
		"""Here we test whether the files get generated with the correct comment lines at the beginning of the file.
		We also check the parameter line.
		"""

		print(sys._getframe(  ).f_code.co_name)

		# First test case:
		n = 2222
		m = 10000
		k = 2
		p = [0.16, 0.32]
		s = 16
		o = tmpfolder
		path = os.path.join(o, self.calculate_file_name(n, m, k=k, s=s))
		g.main(n, m, k=k, p=p, s=s, o=o)
		header = self.get_header(path, 6)
		# The header should have the following form:
		#   "c This file was generated by _"
		#   "c Created by calling python3 generator.py -n 2222 -m 6666 -k 2 -p 0.16 0.32 -s 16 -o ./tmp_test"
		#   "c Hidden solution: pos.int pos.int pos.int ..."
		#   "c p-values 0.16 0.32"
		#   "p cnf 2222 6666"
		#   "'int' 'int' 0"
		self.assertRegex(header[0], "^c This file was generated by[\w\s\.]+\n$")
		self.assertRegex(header[1], f"^c Created by calling python3 generator\.py -n {n} -m {m} -k {k} -p 0\.16 0\.32 -s {s} -o {tmpfolder}\n$")
		self.assertRegex(header[2], "^c Hidden solution: ([\d]+ )*[\d]+\n$")
		self.assertRegex(header[3], "^c p-values 0\.16 0\.32\n$")
		self.assertRegex(header[4], "^p cnf 2222 10000\n$")
		self.assertRegex(header[5], "^(-?[1-9][\d]* ){2}0\n$")
		

		# We also check the case where a hidden solution was delivered.
		n = 100
		m = 4312
		k = 3
		s = 166
		F = './hidden.solution'
		path =  os.path.join('./', self.calculate_file_name(n, m, k=k, s=s))
		g.main(n, m, k=k, s=s, F=F)
		header = self.get_header(path, 6)
		# The header should have the following form:
		#   "c This file was generated by _"
		#   "c Created by calling python3 generator.py -n 1010 -m 4312 -k 3 -s 166 -F ./hidden.solution"
		#   "c Hidden solution: 1 3 5 ... 99"
		#   "c p-values 1.00 1.00 1.00"
		#   "p cnf 1010 4312"
		#   "'int' 'int' 'int' 0"
		self.assertRegex(header[0], "^c This file was generated by[\w\s\.]+\n$")
		self.assertRegex(header[1], f"^c Created by calling python3 generator\.py -n {n} -m {m} -k {k} -s {s} -F \./hidden\.solution\n$")
		# The hidden solution will be checked in the next block of code.
		self.assertRegex(header[3], "^c p-values 1\.00 1\.00 1\.00\n$")
		self.assertRegex(header[4], f"^p cnf {n} {m}\n$")
		self.assertRegex(header[5], "^(-?[1-9][\d]* ){3}0\n$")

		# The line specifying the hidden solution will be split at every whitespace.
		# We then first check the part coming before the actual hidden solution.
		hidden_sol_line = header[2].split()
		self.assertEqual(hidden_sol_line[0], "c")
		self.assertEqual(hidden_sol_line[1], "Hidden")
		self.assertEqual(hidden_sol_line[2], "solution:")        
		# Next, we iterate over the part specifying the hidden solution.
		# Recall that the hidden solution is 1 3 5 ... 9 (note that only positive literals get written to this line).
		hid = 1
		for i in range(3, len(hidden_sol_line)):
			self.assertEqual(hidden_sol_line[i], str(hid))
			hid += 2
		

		# A final, last test for the second randomly generated hidden solution file with an randomly generated p-list.
		n = 1000
		m = 4200
		k = 3
		p = [uniform(0.01, 1.00) for _ in range(k)] # randomly generate a p-list
		F = './hidden2.solution'
		path =  os.path.join('./', self.calculate_file_name(n, m))
		g.main(n, m, F=F)
		header = self.get_header(path, 6)
		# The header should have the following form:
		#   "c This file was generated by _"
		#   "c Created by calling python3 generator.py -n 1000 -m 4200 -F ./hidden2.solution"
		#   "c Hidden solution: {randomly generated}"
		#   "c p-values {randomly generated}"
		#   "p cnf 1000 4200"
		#   "'int' 'int' 'int' 0"
		self.assertRegex(header[0], "^c This file was generated by[\w\s\.]+\n$")
		self.assertRegex(header[1], f"^c Created by calling python3 generator\.py -n {n} -m {m} -F \./hidden2\.solution\n$")
		# The hidden solution will be checked in the next block of code.
		self.assertRegex(header[3], "^c p-values [\s\d\w\.]*\n$")
		self.assertRegex(header[4], "^p cnf 1000 4200\n$")
		self.assertRegex(header[5], "^(-?[1-9][\d]* ){3}0\n$")
		
		# The line specifying the hidden solution will be split at every whitespace.
		# We then first check the part coming before the actual hidden solution.
		hidden_sol_line = header[2].split()
		self.assertEqual(hidden_sol_line[0], "c")
		self.assertEqual(hidden_sol_line[1], "Hidden")
		self.assertEqual(hidden_sol_line[2], "solution:")
		# Next, we iterate over the part specifying the hidden solution.
		for i in range(3, len(hidden_sol_line)):
			self.assertEqual(hidden_sol_line[i], str(self.hidden2[i-3]))



	def check_clause_width_and_used_variables(self, lines, n, k=3):
		"""This method checks if all clauses given by the `lines` of a generated file
		have width `k`.
		We also check whether every variable (from 1 up to `n`) is used at least once
		and that every clause contains variables between 1 and `n` and ends with a "0".
		"""
		used_vars = set()
		for i in range(5, len(lines)):
			literals = lines[i].rstrip().split()
			# Each time we should discover a clause of width k, i.e., k literals plus a terminating 0.
			self.assertEqual(len(literals), k+1)
			self.assertEqual(literals[-1], "0")

			for l in literals[:-1]:
				lit = abs(int(l))
				self.assertGreaterEqual(lit, 1)
				self.assertLessEqual(lit, n)
				used_vars.add(lit)   

		# Here comes the (double) check whether every variable is present in at least one clause:
		self.assertEqual(len(used_vars), n)

		for l in range(1, n+1):
			self.assertIn(l, used_vars)      



	def test_parameters_n_m_k(self):
		"""Here we test whether the generated files abide by the boundary conditions,
		i.e., if when the progam gets called with `n`, `m`, and `k`,
		the generated formula is in k-CNF with n variables over m clauses.
		All clauses get checked for proper format.
		We also test the strict assumption (to make all SAT-solvers happy) that
		clauses in the generated file are not separated by empty lines.
		"""
		
		print(sys._getframe(  ).f_code.co_name)

		# We check the standard case k=3.
		n = 1234
		m = 5182
		o = tmpfolder
		path =  os.path.join(o, self.calculate_file_name(n, m))
		g.main(n, m, o=o)
		lines = self.get_all_lines(path)

		# In the first 5 lines the header can be found.
		# The header, however, gets already checked in test_header.
		# Thus, we can skip the first 5 lines.
		# Our first check will be the number of lines: This number should be m+5.        
		self.assertEqual(m+5, len(lines))

		# After that we check every line that contains a clause and make sure that
		# the width of the clause equals k.
		# Simultaneously, we check whether every variable is used at least once
		# and that every variable is between 1 and n.
		self.check_clause_width_and_used_variables(lines, n)
		

		# We repeat everything with k=5 and a hidden solution.
		n = 100
		m = 4000
		k = 5
		s = 99
		F = "./hidden.solution"
		o = tmpfolder
		path =  os.path.join(o, self.calculate_file_name(n, m, k=k, s=s))
		g.main(n, m, k=k, s=s, o=o, F=F)
		lines = self.get_all_lines(path)

		# In the first 5 lines the header can be found.
		# The header, however, gets already checked in test_header.
		# Thus, we can skip the first 5 lines.
		# Our first check will be the number of lines: This number should be m+5.
		self.assertEqual(m+5, len(lines))

		# After that we check every line that contains a clause and make sure that
		# the width of the clause equals k.
		# Simultaneously, we check whether every variable is used at least once
		# and that every variable is between 1 and n.
		self.check_clause_width_and_used_variables(lines, n, k=k)



	def convert_hidden_sol_to_set(self, hid_string, n):
		"""This method converts the hidden solution string in a set.
		A literal is in this set if and only if it is part of the hidden solution.
		"""
		hid_list = hid_string.rstrip().split()
		hid = set()
		for i in range(1, n+1):
			if str(i) in hid_list:
				hid.add(str(i))
			else:
				hid.add(str(-i))
		return hid


		
	def check_if_hidden_solution_sats_clauses(self, hid, lines):
		"""This method checks if a given hidden solution (passed as a set) satisfies
		all clauses specified by the `lines` of the file.
		"""       
		for i in range(5, len(lines)):
			# We convert every clause into a list of strings.
			# The last entry of every such list gets removed since it is equal to "0" (the end-of-clause-symbol).
			literals = lines[i].split()[:-1]
			satisfied = False
			for lit in literals:
				if lit in hid:
					satisfied = True # it suffices that one literal in every clause is satisfied
					break
			# if not satisfied:
			#     print(literals)
			#     print(sorted( [int(x) for x in hid], key=abs ))
			self.assertTrue(satisfied)        
	 


	def test_hidden_solution(self):
		"""Here we test if the given hidden solutions does indeed
		constitute a satisfying assignment of the generated instance.
		"""

		print(sys._getframe(  ).f_code.co_name)

		# We begin with the standard value of k=3.
		n = 700
		m = 2961
		s = 101010
		o = tmpfolder
		path =  os.path.join(o, self.calculate_file_name(n, m, s=s))
		g.main(n, m, s=s, o=o)
		lines = self.get_all_lines(path)        
		# The hidden solution is written in lines[2].
		hid = self.convert_hidden_sol_to_set(lines[2],n)
		self.check_if_hidden_solution_sats_clauses(hid, lines)
		

		# We also check if this works with a given hidden solution.
		n = 100
		m = 1200
		k = 4
		s = 111
		p = [0.1, 0.2, 0.4, 0.8]
		F = './hidden.solution'
		o = tmpfolder
		path =  os.path.join(o, self.calculate_file_name(n, m, k=k, s=s))
		g.main(n, m, k=k, s=s, p=p, o=o, F=F)
		lines = self.get_all_lines(path)
		# The hidden solution is written in lines[2].
		hid = self.convert_hidden_sol_to_set(lines[2],n)
		self.check_if_hidden_solution_sats_clauses(hid, lines)
		

		# A final check with the second hidden solution file.
		n = 1000
		m = 6000
		k = 2
		s = 1919
		F = './hidden2.solution'
		path =  self.calculate_file_name(n, m, k=k, s=s)
		g.main(n, m, k=k, s=s, F=F)
		lines = self.get_all_lines(path)
		# The hidden solution is written in lines[2].
		hid = self.convert_hidden_sol_to_set(lines[2],n)
		self.check_if_hidden_solution_sats_clauses(hid, lines)


		
	def check_clause_validity(self, lines):
		"""This method checks if the clauses in `lines` are tautologies or improper k-SAT clauses 
		(this second part of the test kind of duplicates check_clause_width_and_used_variables).
		"""
		for i in range(5, len(lines)):
			# We convert every clause in a list of strings.
			# The last entry of every list can be removed since it is equal to "0" (the end-of-clause-symbol).       
			literals = lines[i].split()[:-1]
			lit_set = set( [ abs((int(s))) for s in literals ] )
			self.assertEqual(len(literals), len(lit_set))


			
	def test_constraints(self):
		"""We test the following two side constraints:
		1) The generator is not allowed to produce tautological clauses.
		2) The generator has to produce proper k-SAT clauses.
		"""

		print(sys._getframe(  ).f_code.co_name)
		
		# The higher k and the more clauses are present the liklier it gets 
		# to generate a tautological clause or a clause with a double literal,
		# e.g., clauses of the form {x, y, -x} or {x, y, x}.
		n = 100
		m = 1000
		k = 40
		s = 19
		o = tmpfolder
		path =  os.path.join(o, self.calculate_file_name(n, m, k=k, s=s))
		g.main(n, m, k=k, s=s, o=o)
		lines = self.get_all_lines(path)
		self.check_clause_validity(lines)
		
		
		# A second try:
		n = 1000
		m = 2000
		k = 6
		s = 199
		o = tmpfolder
		path =  os.path.join(o, self.calculate_file_name(n, m, k=k, s=s))
		g.main(n, m, k=k, s=s, o=o)
		lines = self.get_all_lines(path)
		self.check_clause_validity(lines)


		
	def calculate_rejected_prob(self, p):
		"""This function calculated the probability that an arbitrary clause that was generated will be
		rejected by the sampling process based on the given p-values.
		"""

		# Python is a zero-based numbering programming languages (one of its few drawbacks in our opinion).
		# The p-vector used in the description of the generator is one-based, i.e., p = (p_1, ..., p_k).
		# Thus, we extract the p-vector from the p-list to not confuse the reader.
		p1 = p[0]
		p2 = p[1]
		p3 = p[2]

		# If a 3-clause C = (a_1, a_2, a_3) gets sampled ramdomly, we can calculate the probability R
		# that C gets rejected by the p-list based sampling as follows:
		# R = Prob[C gets rej. \cap C contains 3 false literals w.r.t. the hidden solution]
		#   + Prob[C gets rej. \cap C contains 2 false literals w.r.t. the hidden solution]
		#   + Prob[C gets rej. \cap C contains 1 false literals w.r.t. the hidden solution]
		#   + Prob[C gets rej. \cap C contains 0 false literals w.r.t. the hidden solution]
		#   = 1 + 3 * (1-p_1) + 3 * (1-p_2) + (1-p_3),
		# since clauses with 3 false literals always get rejected and (3 choose 2) = (3 choose 1) = 3.
		return (1 + 3*(1-p1) + 3*(1-p2) + (1-p3))/8.0


		
	def calculate_add_probabilities(self, p, W):
		"""This function calculates the probabilities that a clause will be added.

		Fix a complete assignment alpha to all variables of the formula.
		For i = 0, ..., 3 we call a clause that has i literals set to true under alpha an i-clause.
		Given a randomly generated claues, consider the following scheme:
			FFF
			FFT <--
			FTF <--
			FTT
			TFF <--
			TFT
			TTF
			TTT
		It is easy to see that for example
			q_1 := Prob[a 1-clause will be created] = 3/8 (see arrows).
		More generally, letting
			q_i := Prob[a i-clause will be created],
		we have
			q_0 = 1/8,
			q_1 = 3/8,
			q_2 = 3/8,
			q_3 = 1/8.
		Thus
			P_1 := Prob[a 1-clause will be added]
				 = Prob[a 1-clause will be created in round 1 AND this 1-clause gets sampled in round 1]
				   + Prob[a non-1-clause will be created in round 1] * Prob[a 1-clause will be created in round 2 AND this 1-clause gets sampled in round 2]
				   + ...
				 = q_1 * p_1 + [q_0 * 1 + q_1 * (1 - p_1) + q_2 * (1 - p_2) + q_3 * (1 - p_3)] * q_1 * p_1 + ...
				 = q_1 * p_1 + (5/8 - 3/8 * p_2 - 1/8 * p_3) + ...
				 = q_1 * p_1 * sum_{t=0}^{infty} (5/8 - 3/8 * p_2 - 1/8 * p_3)^{t}
				 = 3/8 * p_1 * 1 / (1 - W_1),
		where
			W_i := q_0 + sum_{j=1}^{3} q_j * (1 - p_j).
		In general,
			P_i := Prob[an i-clause will be added]
				 = q_i * p_i * 1 / (1-W).
		"""
		p1 = p[0]
		p2 = p[1]
		p3 = p[2]
		return p1*3/(8.0 * (1-W)), p2*3/(8.0 * (1-W)), p3*1/(8.0 * (1-W))
	


	def count_p_clauses(self, clauses, hidden_list, total_num_of_vars):
		"""This method counts the number of "correct" literals in the list `clauses` w.r.t. the given `hidden_list`.
		The method needs also `total_num_of_vars`, the total number of variables appearing in the whole formula.
		Note, that this method is only implemented for the 3-CNF case.
		"""

		# We create a dictionary that in the end will contain the number of clauses with 1, 2, or 3 "correct" literals.
		# Nota bene: There cannot be a clause with 0 "correct" literals, as this would mean that the clause (and thus the whole formula)
		# gets falsified. However, we construct satisfiable formulas. This was checked via `test_hidden_solution`.
		clause_count = {1:0, 2:0, 3:0}

		# The passed `hidden_list` will be an incomplete hidden solution in the sense that only positive literals of
		# the underlying hidden solution will be listed.
		# Thus, we convert the list `hidden_list` into a dictionary `hidden_complete_dict` whereby we can identify ne negative literals.
		hidden_complete_dict = {}
		for i in range(1, total_num_of_vars+1):
			if i in hidden_list:
				hidden_complete_dict[i] = 1
			else:
				hidden_complete_dict[i] = -1
		
		# For each clause check how many "correct" literals it contains.
		for clause in clauses:
			# We convert each clause in a list of strings.
			# The last entry "0" (signaling the end of the line/clause) will be removed.
			literals = clause.split()[:-1]
			count_correct = 0
			for l in literals:
				lit = int(l)
				sign = hidden_complete_dict[abs(lit)]
				# Check if the literal in the clause and the literal in the hidden solution has the same signum.
				# If yes, then the literal is "correct" w.r.t. the hidden solution.
				if lit * sign > 0:
					count_correct += 1
				
			clause_count[count_correct] += 1

		return [clause_count[1], clause_count[2], clause_count[3]]



	def test_probabilities(self):
		"""This is a probabilistic check (using the chi-squared test) of the clause sampling due to the p-list.
		We only check the standard case k=3.
		"""

		print(sys._getframe(  ).f_code.co_name)

		p = [0.25, 0.125, 0.3]
		n = 1000
		m = 5000		
		s = randint(1,10000) # We use a random seed. Repeating this test leads to more confidence in the result.
		o = tmpfolder
		F = './hidden2.solution'
		path =  os.path.join(o, self.calculate_file_name(n, m, s=s))
		g.main(n, m, s=s, o=o, p=p, F=F)
		lines = self.get_all_lines(path)
		
		# We count how many times a 1-correct, 2-correct, and 3-correct clause appears.
		# We compare these values to the expected values.
		# The clauses begin at lines[5].
		observed_frequency_list = self.count_p_clauses(lines[5:], self.hidden2, 1000)
		W = self.calculate_rejected_prob(p)
		P1, P2, P3 = self.calculate_add_probabilities(p, W)
		# Letting Q_i be the number of i-clauses (for this notion see `calculate_add_probabilities`),
		# it holds E[Q_i] = m * P_i, where P_i is calculated via `calculate_add_probabilities(p, W)`.
		exp_frequency_list = [m*P1, m*P2, m*P3]

		# We use Pearson's chi-squared test to determine whether there is a statistically significant difference between 
		# the expected frequencies and the observed frequencies in the categories 1-correct, 2-correct, and 3-correct.
		_, p = chisquare(observed_frequency_list, exp_frequency_list)
		if p < 0.05:
			print("WARNING, WARNING. Self-destruction initialized.")
			print("p-value for the generated instance is", p)
		print("Everything's fine... probably. p-value for the generated instance is", p)   



	def check_for_duplicate_clauses(self, lines):
		"""This method checks whether there are any duplicate clauses in `lines`.
		"""
		in_formula_set = set()
		for i in range(5, len(lines)):			
			# We convert each clause in a list of strings.
			# The last entry "0" (signaling the end of the line/clause) will be removed.
			literals = lines[i].split()[:-1]
			lit_set = frozenset( [ int(s) for s in literals ] )
			# Ensures that the current clause has not been seen.
			self.assertNotIn(lit_set, in_formula_set)
			in_formula_set.add(lit_set)



	def test_unique_clauses(self):
		"""We test whether the generated formula contains only unique clauses.
		"""

		print(sys._getframe(  ).f_code.co_name)

		# We assume that there are no duplicate clauses. This tests checks that assumption.
		n = 20
		m = 1000
		s = 111
		o = tmpfolder
		path =  os.path.join(o, self.calculate_file_name(n, m, s=s))
		g.main(n, m, s=s, o=o)
		lines = self.get_all_lines(path)
		self.check_for_duplicate_clauses(lines)

		# Let's do a second test.
		n = 100
		m = 10000
		s = 11
		k = 2
		o = tmpfolder
		path =  os.path.join(o, self.calculate_file_name(n, m, k=k, s=s))
		g.main(n, m, s=s, k=k, o=o)
		lines = self.get_all_lines(path)
		self.check_for_duplicate_clauses(lines)

		
		
if __name__ == 'main':
	unittest.main()
