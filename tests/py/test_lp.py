import numpy as np
from nose.tools import assert_almost_equals
from modal.detectionfunctions.lp import burg, predict
from modal.detectionfunctions.pydetectionfunctions import burg as c_burg
from modal.detectionfunctions.pydetectionfunctions import linear_prediction as c_predict

class TestLinearPrediction(object):
    FLOAT_PRECISION = 5 # number of decimal places to check for accuracy
    order = 10
    
    def test_burg_py_c_equal(self):       
        num_runs = 100
        c_coefs = np.zeros(self.order)
        for i in range(num_runs):
            # create a random signal
            samples = (np.random.random_sample(self.order) * 2) -1
            py_coefs = burg(samples, self.order)
            c_burg(samples, self.order, c_coefs)
            # make sure both functions produce the same number of coefficients
            assert len(py_coefs) == len(c_coefs)
            # make sure coefficient values are equal
            for c in range(len(py_coefs)):
                assert_almost_equals(py_coefs[c], c_coefs[c],
                                     places=self.FLOAT_PRECISION)
            
    def test_predict_py_c_equal(self):
        num_runs = 100
        num_predictions = 5
        c_predictions = np.zeros(num_predictions)
        for i in range(num_runs):
            # create a random signal
            samples = (np.random.random_sample(self.order) * 2) -1
            # create random coefficients
            coefs = np.random.random_sample(self.order)
            # get predictions
            py_predictions = predict(samples, coefs, num_predictions)
            c_predict(samples, coefs, c_predictions)
            # make sure both functions produce the same number of predictions
            assert len(py_predictions) == len(c_predictions)
            # make sure prediction values are equal
            for c in range(len(py_predictions)):
                assert_almost_equals(py_predictions[c], c_predictions[c],
                                     places=self.FLOAT_PRECISION)
