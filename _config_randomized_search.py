#----------
# Randomized Search Parameters
#----------

n_iter = 500

cv_folds = 10

# A distribution for continuous values: 
#
# "uniform" or "norm"
#  (or any continuous distribution function name 
#  from scipy.stats.distributions - must be 
#  implemented in randomized_search.py first)
# 

continuous_distribution = "uniform"    

# A distribution for continuous values: 
#
# "randint" (uniform), "geom" 
#  (or any continuous distribution function name 
#  from scipy.stats.distributions - must be 
#  implemented in randomized_search.py first)
# 

discrete_distribution = "randint"    
