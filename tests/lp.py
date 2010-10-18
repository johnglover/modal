# Copyright (c) 2010 John Glover, National University of Ireland, Maynooth
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from modal.lp import burg, predict
from modal.pydetectionfunctions import burg as c_burg, linear_prediction as c_predict
import numpy as np
import unittest


class TestLinearPrediction(unittest.TestCase):
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
            self.assertEquals(len(py_coefs), len(c_coefs))
            # make sure coefficient values are equal
            for c in range(len(py_coefs)):
                self.assertAlmostEquals(py_coefs[c], c_coefs[c],
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
            self.assertEquals(len(py_predictions), len(c_predictions))
            # make sure prediction values are equal
            for c in range(len(py_predictions)):
                self.assertAlmostEquals(py_predictions[c], c_predictions[c],
                                        places=self.FLOAT_PRECISION)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestLinearPrediction('test_burg_py_c_equal'))
    suite.addTest(TestLinearPrediction('test_predict_py_c_equal'))
    unittest.TextTestRunner().run(suite)
