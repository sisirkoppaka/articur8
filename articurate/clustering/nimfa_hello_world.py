# Import nimfa library entry point for factorization.
import nimfa

# Here we will work with numpy matrix.
import numpy as np

# Generate random target matrix.
V = np.random.rand(30, 20)

# Generate random matrix factors which we will pass as fixed factors to Nimfa.
init_W = np.random.rand(30, 4)
init_H = np.random.rand(4, 20)
# Obviously by passing these factors we want to use rank = 4.

# Run NMF.
# We don't specify any algorithm parameters. Defaults will be used.
# We specify fixed initialization method and pass matrix factors.
fctr = nimfa.mf(V, method = "nmf", seed = "fixed", W = init_W, H = init_H, rank = 4)
fctr_res = nimfa.mf_run(fctr)

# Print the loss function (Euclidean distance between target matrix and its estimate). 
print "Euclidean distance: %5.3e" % fctr_res.distance(metric = "euclidean")

# It should print 'fixed'.
print fctr_res.seeding

# By default, max 30 iterations are performed.
print fctr_res.n_iter

