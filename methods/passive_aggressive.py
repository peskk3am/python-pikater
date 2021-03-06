from methods.hyperparameters import *
from sklearn.linear_model.passive_aggressive import PassiveAggressiveClassifier


def get_name():
    return "Passive aggressive"


def get_model_class():
    return PassiveAggressiveClassifier


def get_hyperparameter_search_space():

    hs = HyperparameterSpace()
    
    loss = CategoricalHyperparameter("passive_aggressive__loss",
                                     ["hinge", "squared_hinge"],
                                     default="hinge")
    fit_intercept = CategoricalHyperparameter("passive_aggressive__fit_intercept", [True, False], default=False)
    max_iter = IntegerHyperparameter("passive_aggressive__max_iter", 1, 1000, default=5)
    C = FloatHyperparameter("passive_aggressive__C", 1e-5, 10.0, default=1.0)
    shuffle = CategoricalHyperparameter("passive_aggressive__shuffle", [True, False], default=True)
        
    hs.add_hyperparameter(loss)
    hs.add_hyperparameter(fit_intercept)
    hs.add_hyperparameter(max_iter)
    hs.add_hyperparameter(C)
    hs.add_hyperparameter(shuffle)
        
    return hs
