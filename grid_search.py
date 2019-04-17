import sklearn.model_selection as model_selectionimport _config_grid_searchimport numpy as npimport searchimport databaseclass GridSearch(search.Search):    def __init__(self, estimator, chain_names, hyperparameter_space,                 dataset_name, verbose=0):        self.cv = _config_grid_search.cv_folds        self.chain_names = chain_names                        self.gs = model_selection.GridSearchCV(                 estimator, hyperparameter_space,                                  cv=self.cv,                 error_score=np.NaN,                                  verbose=0)                      self.estimator = estimator        self.dataset_name = dataset_name                  def get_name(self):        return "Grid Search (scikit-learn)"                                    def fit(self, X, y):                       self.gs.fit(X, y)                # write results to the file        f, file_name = self.results_file_open("w")                                        self.write_header(f)                                                                                                                                  f.write("# Grid scores on development set:\n\n")        means = self.gs.cv_results_['mean_test_score']        stds = self.gs.cv_results_['std_test_score']        results = []        for mean, std, params in zip(means, stds, self.gs.cv_results_['params']):            f.write("%0.3f (+/-%0.03f) for %r"                  % (mean, std * 2, params))            f.write("\n")            # write results to database            results.append((str(self.chain_names[:-1]), str(self.chain_names[-1]), str(params), self.cv, self.dataset_name, float(mean), float(std)))                                                  f.write("\n\n# Grid Search finished.")        f.close()                                                            try:            database.insert_results(results)        except Exception as e:            # print(results)            print(e)                                    print("Grid Search finished.")        