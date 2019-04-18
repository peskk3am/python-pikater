import _config_simulated_annealing_searchimport scipy.statsimport randomfrom numpy import std, nan, isnanimport mathfrom sklearn.model_selection import cross_val_scoreimport searchimport databaseclass SimulatedAnnealingSearch(search.Search):    def __init__(self, estimator, chain_names, hyperparameter_space,                 dataset_name, verbose=0):                super(SimulatedAnnealingSearch, self).__init__()                self.cv = _config_simulated_annealing_search.cv_folds        self.n_iter = _config_simulated_annealing_search.n_iter        self.temperature = _config_simulated_annealing_search.temperature                self.a = _config_simulated_annealing_search.a        self.L = _config_simulated_annealing_search.L                         self.estimator = estimator        self.chain_names = chain_names        self.dataset_name = dataset_name         self.verbose = verbose                 self.hyperparameter_space = hyperparameter_space                                                                  def init_params(self):        # generate attrs automatically                               self.params = {}        self.constant_params = {}                for param in self.hyperparameter_space.hyperparameters:                                    if param.__class__.__name__ == "FloatHyperparameter":                            self.params[param.name] = random.uniform(param.lower, param.upper)            if param.__class__.__name__ == "CategoricalHyperparameter":                self.params[param.name] = random.choice(param.value)            if param.__class__.__name__ == "IntegerHyperparameter":                self.params[param.name] = random.randint(param.lower, param.upper)            if param.__class__.__name__ == "Constant":                self.constant_params[param.name] = param.value                # ... there is only one value for the constant parameter                      if self.verbose > 0:            print("Params", self.params)            print("Constant params", self.constant_params)                def get_name(self):        return "Simulated Annealing Search (scikit-learn)"                def evalFitness(self, params):         ''' evaluates the given estimator+params using cv            params ... dict of changable parameters                        -> to file: cv_results                       ['mean_score'],                     ['std_score'],                     ['params']         '''                score = 0        cv_result = {}        try:                    # self.estimator.__init__()             params = {**params, **self.constant_params}             self.estimator.set_params(**params)            # print(self.estimator.get_params())                            scores = cross_val_score(self.estimator, self.X, self.y, cv=self.cv)            # scores ... array of scores => count average            if self.verbose > 2:                print("---- scores:", scores)            mean_score = sum(scores)/self.cv            std_score = std(scores)                         cv_result["mean_score"] = mean_score            cv_result["std_score"] = std_score                                                except Exception as e:           # TODO: odchytavat jenom tu spravnou vyjimku !!!                 print("Exception: "+str(e))           cv_result["mean_score"] = nan  # numpy nan           cv_result["std_score"] = nan                cv_result["params"] = params                return cv_result            def P(self, score, score_new, t):        ''' acceptance probability function             (returns probability to accept the new solution            as the next solution)        '''                        if self.verbose > 2:            print("-- P function:")            print("----score:", score)            print("----score_new", score_new)                        if isnan(score_new):            score_new = 0                if isnan(score) or score_new > score:            prob = 1                               else:            ''' formula: exp(-(score_new-score)/t)                                 the formula is to minimize the energy            '''                         prob = math.exp((score_new-score)/t)            # print (prob, (score_new-score), t)         if self.verbose > 2:            print("-- prob:", prob)                                   return prob             def get_temperature(self, k, k_max):                                 t = self.temperature*self.a**(math.floor(k/self.L))                        return t            def neighbour(self, params):        params_new = {}        k_max = self.n_iter        for param in self.hyperparameter_space.hyperparameters:                                    if param.__class__.__name__ == "FloatHyperparameter":                  d = ((param.upper - param.lower) / k_max) * random.choice([-1,1])                new_value = params[param.name] + d                if new_value > param.upper or new_value < param.lower:                    new_value = new_value * -1                                                              params_new[param.name] = new_value             if param.__class__.__name__ == "CategoricalHyperparameter":                params_new[param.name] = random.choice(param.value)            if param.__class__.__name__ == "IntegerHyperparameter":                d = int(round(((param.upper - param.lower) / k_max)))                 if d < 1:                    d = 1                d = d * random.choice([-1,1])                    new_value = params[param.name] + d                                if new_value > param.upper or new_value < param.lower:                    new_value = params[param.name] + d*(-1)                                                              params_new[param.name] = new_value                            if param.__class__.__name__ == "Constant":                self.constant_params[param.name] = param.value                # ... there is only one value for the constant parameter                                      return params_new        def fit(self, X, y):        ''' X ... data            y ... classes                    '''            self.X = X        self.y = y                   self.X_train, self.X_test, self.y_train, self.y_test = self.split_dataset(X,y)                # the main part        cv_results = {             "mean_score": [],            "std_score":  [],            "params":     [],            }                self.init_params()                params = self.params        score = self.evalFitness(params)["mean_score"]          #                             ^ evalFitness returns a dictionary                for k in range(0, self.n_iter):            t = self.get_temperature(k, self.n_iter)            if self.verbose > 0:                print("\nTemperature:", t)                        params_new = self.neighbour(params)                                                                         res = self.evalFitness(params_new)            score_new = res["mean_score"]                          if self.P(score, score_new, t) >= random.random() or len(cv_results["mean_score"]) == 0:   # it is the first evaluation                params = params_new                                score = res["mean_score"]                                # save results of the selected neighbour                cv_results["mean_score"].append(res["mean_score"])                                 cv_results["std_score"].append(res["std_score"])                cv_results["params"].append(res["params"])                                                if self.verbose > 1:                    print("-- New solution:")                    print("---- avg score:", res["mean_score"])                    print("---- std score:", res["std_score"])                    print("---- params:", res["params"])                elif self.verbose > 0:                    print("---- score:", res["mean_score"])                            else:                # copy previous results                                                    cv_results["mean_score"].append(cv_results["mean_score"][-1])                                 cv_results["std_score"].append(cv_results["std_score"][-1])                cv_results["params"].append(cv_results["params"][-1])                                # write results to the file        f, file_name = self.results_file_open("w")                                        self.write_header(f)                means = cv_results['mean_score']        stds = cv_results['std_score']        results = []                for mean, std, params in zip(means, stds, cv_results['params']):            f.write("%0.3f (+/-%0.03f) for %r"                  % (mean, std * 2, params))            f.write("\n")                        # write results to database                        results.append((self.experiment_id, self.get_name(), str(self.chain_names[:-1]), str(self.chain_names[-1]), str(params), self.cv, self.dataset_name, float(mean), float(std)))                                                                                                      try:            database.insert_results(results)        except Exception as e:            # print(results)            print(e)         # TODO:                    #         best        #            ['mean_test_score'],         #            ['std_test_score'],         #            ['params']             f.write("\n\n# Simulated Annealing Search finished.")        f.close()        print("Simulated Annealing Search finished.")                                    