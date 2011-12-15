import numpy as np

def autocorrelation(signal, order):
    """Using the autocorrelation method and Levinson-Durbin
    recursion, calculate order coefficients.
    Returns a numpy array."""
    # calculate auto_coefs, the autocorrelation coefficients
    auto_coefs = np.zeros(order+1)
    for i in range(len(auto_coefs)):
        for j in range(len(signal)-i):
            auto_coefs[i] += signal[j] * signal[j+i]
    # Levinson-Durbin recursion
    coefs = np.zeros(order+1)
    coefs[0] = 1
    e = auto_coefs[0]
    for i in range(order):
        # calculate lambda
        lda = 0
        for j in range(i+1):
            lda -= coefs[j] * auto_coefs[i+1-j]
        lda /= e
        # update coefficients
        for j in range(((i+1)/2) +1):
            temp = coefs[i+1-j] + (lda * coefs[j])
            coefs[j] = coefs[j] + (lda * coefs[i+1-j])
            coefs[i+1-j] = temp
        # update e
        e *= 1 - (lda * lda)
    return coefs[1:]

def covariance(signal, order, n):
    """Using the covariance method, calculate order coefficients.
    Returns a numpy array."""
    if len(signal) < n + order:
        raise Exception("signal must be at least order + n samples long")
    # calculate covariance and solution matrices
    cov = np.matrix(np.zeros((order, order)))
    B = np.matrix(np.zeros((order, 1)))
    for i in range(order+1):
        for k in range(order):
            for sample in range(len(signal)-n, len(signal)):
                if i == 0:
                    # B is the 0th row of the matrix
                    B[k] += signal[sample] * signal[sample-k]
                else:
                    # to save space, the covariance matrix is still indexed starting
                    # at 0. However, each row is really row+1 in terms of the
                    # mathematical equations. 
                    cov[i-1,k] += signal[sample-i] * signal[sample-k]
    return np.linalg.solve(cov, -B).T.A[0]

def burg(signal, order):
    """Using the burg method, calculate order coefficients.
    Returns a numpy array."""
    coefs = np.array([1.0])
    # initialise f and b - the forward and backwards predictors
    f = np.zeros(len(signal))
    b = np.zeros(len(signal))
    for i in range(len(signal)):
        f[i] = b[i] = signal[i]
    # burg algorithm
    for k in range(order):
        # fk is f without the first element
        fk = f[1:]
        # bk is b without the last element
        bk = b[0:b.size-1]
        # calculate mu
        if sum((fk*fk)+(bk*bk)):
            # check for division by zero
            mu = -2.0 * sum(fk*bk) / sum((fk*fk)+(bk*bk))
        else:
            mu = 0.0
        # update coefs
        # coefs[::-1] just reverses the coefs array
        coefs = np.hstack((coefs,0)) + (mu * np.hstack((0, coefs[::-1])))
        # update f and b
        f = fk + (mu*bk)
        b = bk + (mu*fk)
    return coefs[1:]

def burg_rec(signal, order):
    """Using the burg (recursive) method, calculate order coefficients.
    Returns a numpy array.
    todo: The recursive calculation of the denominator does not seem to be correct.
          The initial values of both d and mu are good, the updated f and b seem good,
          so it would seem that the update of d is the problem."""
    coefs = np.zeros(order+1)
    coefs[0] = 1.0
    # initialise f and b - the forward and backwards predictors
    f = np.zeros(len(signal))
    b = np.zeros(len(signal))
    for i in range(len(signal)):
        f[i] = b[i] = signal[i]
    # initialise d - denominator of mu
    d = 0.0
    for i in range(len(signal)):
        d += 2 * (f[i]*b[i])
    d -= (f[0]*f[0]) + (b[len(signal)-1]*b[len(signal)-1])
    # burg recursion
    for k in range(order):
        # calculate mu
        mu = 0
        for n in range(len(signal)-k-1):
            mu += f[n+k+1] * b[n]
        mu *= -2.0 / d
        # update coefs
        for n in range(((k+1)/2) +1):
            t1 = coefs[n] + mu * coefs[k+1-n]
            t2 = coefs[k+1-n] + mu * coefs[n]
            coefs[n] = t1
            coefs[k+1-n] = t2
        # update f and b
        for n in range(len(signal)-k-1):
            t1 = f[n+k+1] + mu * b[n]
            t2 = b[n] + mu * f[n+k+1]
            f[n+k+1] = t1
            b[n] = t2
        # update d
        d = ((1 - (mu*mu)) * d) - (f[k+1]*f[k+1]) - (b[len(signal)-k-1]*b[len(signal)-k-1])
    return coefs[1:]

def predict(signal, coefs, num_predictions):
    """Using Linear Prediction, return the estimated next num_predictions
    values of signal, using the given coefficients.
    Returns a numpy array."""
    predictions = np.zeros(num_predictions)
    past_samples = np.zeros(len(coefs))
    for i in range(len(coefs)):
        past_samples[i] = signal[-1-i]
    sample_pos = 0
    for i in range(num_predictions):
        # each sample in past_samples is multiplied by a coefficient
        # results are summed
        for j in range(len(coefs)):
            predictions[i] -= coefs[j] * past_samples[(j+sample_pos) % len(coefs)]
        sample_pos -= 1
        if sample_pos < 0:
            sample_pos = len(coefs) - 1
        past_samples[sample_pos] = predictions[i] 
    return predictions
    
# Testing ---------------------------------------------------------------------
if __name__ == '__main__':
    import unittest
    import testsignals
    FLOAT_PRECISION = 3 # number of decimal places to check for accuracy

    class TestLP(unittest.TestCase):
        def test_autocorrelation(self):
            """test_autocorrelation"""
            num_samples = 4096
            test_signal = testsignals.noisy_sine_wave(num_samples)
            order = 5
            # calculate autocorrelation coefficients
            r = np.zeros(order+1)
            for i in range(order+1):
                for k in range(num_samples-i):
                    r[i] += test_signal[k] * test_signal[k+i]
            # form matrices
            rows = []
            for i in range(order):
                rows.append([r[abs(i-k)] for k in range(order)])
            A = np.matrix(rows)
            B = np.matrix(np.array([[-r[i]] for i in range(1, order+1)]))
            coefs = np.linalg.solve(A, B)
            ld_coefs = autocorrelation(test_signal, order)
            # compare coefficients
            self.assertEquals(order, coefs.T.A[0].size)
            self.assertEquals(order, ld_coefs.size)
            for i in range(order):
                self.assertAlmostEquals(coefs.T.A[0][i], ld_coefs[i],
                                        places=FLOAT_PRECISION)
                
        def test_covariance(self):
            """test_covariance"""
            num_samples = 4096
            test_signal = testsignals.noisy_sine_wave(num_samples)
            order = 5
            n = 50
            coefs = covariance(test_signal, order, n)
            cp = predict(test_signal, coefs, 3)
            raise Exception("NotYetImplemented")

        def test_burg(self):
            """test_burg"""
            num_samples = 1024
            test_signal = testsignals.noisy_sine_wave(num_samples)
            order = 5
            b_coefs = burg(test_signal, order)
            brec_coefs = burg_rec(test_signal, order)
            self.assertEquals(b_coefs.size, brec_coefs.size)
            for i in range(order):
                self.assertAlmostEquals(b_coefs[i], brec_coefs[i],
                                        places=FLOAT_PRECISION)
        
        def test_predict(self):
            """test_predict"""
            coefs = np.array([1,2,3,4,5])
            test_signal = np.ones(5)
            predictions = predict(test_signal, coefs, 2)
            self.assertEquals(predictions[0], -sum(coefs))
            self.assertEquals(predictions[1], -sum(coefs[1:])-predictions[0])
        
    suite = unittest.TestSuite()
    suite.addTest(TestLP('test_autocorrelation'))
    suite.addTest(TestLP('test_covariance'))
    suite.addTest(TestLP('test_burg'))
    suite.addTest(TestLP('test_predict'))
    unittest.TextTestRunner().run(suite)
