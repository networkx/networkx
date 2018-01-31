
def cycle_multiplier(Wn, We):
	multiplier = 1.
	for edge_position in range(len(We)):
		if T[We[edge_position]] == Wn[edge_position]:
			multiplier *= Mu[We[edge_position]]
		else:
			multipier /= Mu[We[edge_position]]
	
	return multiplier
