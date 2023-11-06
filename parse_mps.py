import casadi as ca
from pulp import LpProblem, LpMinimize, lpSum, value, LpVariable, LpStatus,LpConstraintEQ, LpConstraintGE, LpConstraintLE
import numpy as np

# Test the function
file_path = "fome12.mps" # https://plato.asu.edu/ftp/lptestset/fome/fome12.bz2
file_path = "binkar10_1.mps" # https://miplib.zib.de
file_path_output = file_path.replace(".mps",".pkl")
# Load the MPS file using PuLP
var,prob = LpProblem.fromMPS(file_path)

assert np.all([v.cat in ['Continuous','Integer'] for k,v in var.items()])

var_names = list(sorted(var.keys()))
n = len(var_names)

# Map names to integers
index = dict((v,k) for k,v in enumerate(var_names))



discrete = [var[k].cat=='Integer' for k in var_names]

def value(e,none):
	if e is None: return none
	return e

lbx = ca.vcat([value(var[k].lowBound,-np.inf) for k in var_names])
ubx = ca.vcat([value(var[k].upBound,np.inf) for k in var_names])


def parse_affine_expression(e):
	ret = ca.DM.zeros(n,1)
	for (v,c) in e.items():
		ret[index[v.name]] = c
	return ret

g = parse_affine_expression(prob.objective)


A = []
lba = []
uba = []

for c in prob.constraints.values():
	a = ca.sparsify(parse_affine_expression(c))
	if a.nnz()==0: continue # Purge empty rows
	c.sense == 0
	if c.sense == LpConstraintEQ:
		A.append(a.T)
		lba.append(-c.constant)
		uba.append(-c.constant)
	elif c.sense == LpConstraintGE:
		#print(c," | >=",a.nonzeros(),-c.constant)
		A.append(a.T)
		lba.append(-c.constant)
		uba.append(np.inf)
	elif c.sense == LpConstraintLE:
		#print(c," | <=",a.nonzeros(),-c.constant)
		A.append(a.T)
		lba.append(-np.inf)
		uba.append(-c.constant)
	else:
		raise Exception()

A = ca.vcat(A)
lba = ca.vcat(lba)
uba = ca.vcat(uba)

kwargs = {"a": A, "lbx": lbx, "ubx": ubx, "lba": lba, "uba": uba, "g": g, "discrete": discrete}

import pickle

pickle.dump(kwargs,open(file_path_output,'wb'))

