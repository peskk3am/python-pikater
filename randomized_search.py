import sklearn.model_selection as model_selection

import _config_randomized_search

import scipy.stats
from numpy import NaN
import search

import database

class RandomizedSearch(search.Search):
    def __init__(self, estimator, chain_names, hyperparameter_space,
                 dataset_name, verbose=0):

        super(RandomizedSearch, self).__init__()

        # settings from config file
        self.cv = _config_randomized_search.cv_folds
        self.n_iter = _config_randomized_search.n_iter
        self.continuous_distribution = _config_randomized_search.continuous_distribution
        self.discrete_distribution = _config_randomized_search.discrete_distribution
        
        self.estimator = estimator
        self.chain_names = chain_names
        self.dataset_name = dataset_name 
        self.verbose = verbose     
       
        param_dist = self.create_param_distributions(hyperparameter_space)        
        
        self.rs = model_selection.RandomizedSearchCV(
                      estimator,
                      param_distributions=param_dist,                      
                      n_iter=self.n_iter,
                      error_score=NaN,                 
                      cv=self.cv,
                      refit=False,
                      n_jobs=1)                                
    
    def get_name(self):
        return "Randomized Search (scikit-learn)"
              
    def fit(self, X, y):
        
        self.rs.fit(X, y)
        
        # write results to the file
        f, file_name = self.results_file_open("w")                        
        
        self.write_header(f)

        f.write("# Random search params: \n")
        f.write("# -- cv: "+str(self.cv)+"\n")
        f.write("# -- n_iter: "+str(self.n_iter)+"\n")
        f.write("# -- continuous_distribution: "+self.continuous_distribution+"\n")
        f.write("# -- discrete_distribution: "+self.discrete_distribution+"\n")
        f.write("\n")
                                                                              
        f.write("# Randomized scores on development set:\n\n")

        means = self.rs.cv_results_['mean_test_score']
        stds = self.rs.cv_results_['std_test_score']        
        results = []
        for mean, std, params in zip(means, stds, self.rs.cv_results_['params']):
            f.write("%0.3f (+/-%0.03f) for %r"
                  % (mean, std * 2, params))
            f.write("\n")
            
            # write results to database
            results.append((self.experiment_id, self.get_name(), str(self.chain_names[:-1]), str(self.chain_names[-1]), str(params), self.cv, self.dataset_name, float(mean), float(std), 0))                                          
                                                    
        try:
            database.insert_results(results)
        except Exception as e:
            # print(results)
            print(e)            
            
        f.write("\n\n# Randomized Search finished.")
        f.close()

        print("Randomized Search finished.")
    
        
    def create_param_distributions(self, hyperparameter_space):
        ''' specify parameters and distributions to sample from
            example:
              param_dist = {"max_depth": [3, None],
                  "max_features": sp_randint(1, 11),
                  "min_samples_split": sp_randint(2, 11),
                  "bootstrap": [True, False],
                  "criterion": ["gini", "entropy"]}  
            
            From sci-kit doc:
            param_distributions : dict
            Dictionary with parameters names (string) as keys and distributions
            or lists of parameters to try. Distributions must provide a rvs 
            method for sampling (such as those from scipy.stats.distributions).
            If a list is given, it is sampled uniformly.            
        '''
        
        # if self.continuous_distribution:
        #    cont_dist_f = eval("scipy.stats."+self.continuous_distribution)        
        
        # if self.discrete_distribution:
        #    disc_dist_f = eval("scipy.stats."+self.discrete_distribution)

        param_dict = {}
        
        for param in hyperparameter_space.hyperparameters:
            value = None                        
            if param.__class__.__name__ == "FloatHyperparameter":            
                if self.continuous_distribution=="uniform":                
                # In the standard form, the distribution is uniform on [0, 1]. 
                # Using the parameters loc and scale, one obtains the uniform 
                # distribution on [loc, loc + scale].
                    value = scipy.stats.uniform(loc=param.lower, scale=param.upper-param.lower)
                
                if self.continuous_distribution=="norm":
                    raise Exception("Klara's Exception: randomized_search.py: norm is yet to be implemented")
                    pass                
                
            if param.__class__.__name__ == "CategoricalHyperparameter":
                value = param.value
                
            if param.__class__.__name__ == "IntegerHyperparameter":
                # .rvs(low, high, loc=0, size=1, random_state=None)
                if self.discrete_distribution=="randint":                
                    value = scipy.stats.randint(low=param.lower, high=param.upper+1)                    
                
                if self.discrete_distribution=="geom":
                    raise Exception("Klara's Exception: randomized_search.py: geom is yet to be implemented")
                    pass                
                                   
            if param.__class__.__name__ == "Constant":
                value = param.value
                # [0] ... there is only one value for the constant parameter  
                
            param_dict[param.name] = value 
        if self.verbose > 0:
            print ("Randomized search params:", end="")
            print(param_dict)
                                                                                                      
        return param_dict
        