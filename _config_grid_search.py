#----------
# Grid Search Parameters
#----------

# set either grid_n parameter or max_number_of_evaluations
# (if both are set, only max_number_of_evaluations is used)

# number of options to try for each parameter
# for categorical parameters, first 'grid_n' is used
# grid_n must be greater than 1

# grid_n = 2

max_number_of_evaluations = 500

cv_folds = 10
                                 
# applies for integer and float parameters
logarithmic_scale = False # True/False