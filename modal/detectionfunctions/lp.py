import numpy as np


def autocorrelation(signal, order):
    '''
    Using the autocorrelation method and Levinson-Durbin
    recursion, calculate order coefficients.
    Returns a numpy array.
    '''
    # calculate auto_coefs, the autocorrelation coefficients
    auto_coefs = np.zeros(order + 1)
    for i in range(len(auto_coefs)):
        for j in range(len(signal) - i):
            auto_coefs[i] += signal[j] * signal[j + i]
    # Levinson-Durbin recursion
    coefs = np.zeros(order + 1)
    coefs[0] = 1
    e = auto_coefs[0]
    for i in range(order):
        # calculate lambda
        lda = 0
        for j in range(i + 1):
            lda -= coefs[j] * auto_coefs[i + 1 - j]
        lda /= e
        # update coefficients
        for j in range(((i + 1) / 2) + 1):
            temp = coefs[i + 1 - j] + (lda * coefs[j])
            coefs[j] = coefs[j] + (lda * coefs[i + 1 - j])
            coefs[i + 1 - j] = temp
        # update e
        e *= 1 - (lda * lda)
    return coefs[1:]


def covariance(signal, order, n):
    '''
    Using the covariance method, calculate order coefficients.
    Returns a numpy array.
    '''
    if len(signal) < n + order:
        raise Exception('signal must be at least order + n samples long')
    # calculate covariance and solution matrices
    cov = np.matrix(np.zeros((order, order)))
    B = np.matrix(np.zeros((order, 1)))
    for i in range(order + 1):
        for k in range(order):
            for sample in range(len(signal) - n, len(signal)):
                if i == 0:
                    # B is the 0th row of the matrix
                    B[k] += signal[sample] * signal[sample - k]
                else:
                    # to save space, the covariance matrix is still indexed
                    # starting at 0. However, each row is really row+1 in
                    # terms of the mathematical equations.
                    cov[i - 1, k] += signal[sample - i] * signal[sample - k]
    return np.linalg.solve(cov, -B).T.A[0]


def burg(signal, order):
    '''Using the burg method, calculate order coefficients.
    Returns a numpy array.'''
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
        bk = b[0:b.size - 1]
        # calculate mu
        if sum((fk * fk) + (bk * bk)):
            # check for division by zero
            mu = -2.0 * sum(fk * bk) / sum((fk * fk) + (bk * bk))
        else:
            mu = 0.0
        # update coefs
        # coefs[::-1] just reverses the coefs array
        coefs = np.hstack((coefs, 0)) + (mu * np.hstack((0, coefs[::-1])))
        # update f and b
        f = fk + (mu * bk)
        b = bk + (mu * fk)
    return coefs[1:]


def predict(signal, coefs, num_predictions):
    '''Using Linear Prediction, return the estimated next num_predictions
    values of signal, using the given coefficients.
    Returns a numpy array.'''
    predictions = np.zeros(num_predictions)
    past_samples = np.zeros(len(coefs))
    for i in range(len(coefs)):
        past_samples[i] = signal[-1 - i]
    sample_pos = 0
    for i in range(num_predictions):
        # each sample in past_samples is multiplied by a coefficient
        # results are summed
        for j in range(len(coefs)):
            predictions[i] -= coefs[j] * \
                past_samples[(j + sample_pos) % len(coefs)]
        sample_pos -= 1
        if sample_pos < 0:
            sample_pos = len(coefs) - 1
        past_samples[sample_pos] = predictions[i]
    return predictions


if __name__ == '__main__':
    import unittest
    import testsignals
    FLOAT_PRECISION = 3  # number of decimal places to check for accuracy

    class TestLP(unittest.TestCase):
        def test_autocorrelation(self):
            num_samples = 4096
            test_signal = testsignals.noisy_sine_wave(num_samples)
            order = 5
            # calculate autocorrelation coefficients
            r = np.zeros(order + 1)
            for i in range(order + 1):
                for k in range(num_samples - i):
                    r[i] += test_signal[k] * test_signal[k + i]
            # form matrices
            rows = []
            for i in range(order):
                rows.append([r[abs(i - k)] for k in range(order)])
            A = np.matrix(rows)
            B = np.matrix(np.array([[-r[i]] for i in range(1, order + 1)]))
            coefs = np.linalg.solve(A, B)
            ld_coefs = autocorrelation(test_signal, order)
            # compare coefficients
            self.assertEquals(order, coefs.T.A[0].size)
            self.assertEquals(order, ld_coefs.size)
            for i in range(order):
                self.assertAlmostEquals(coefs.T.A[0][i], ld_coefs[i],
                                        places=FLOAT_PRECISION)

        def test_covariance(self):
            num_samples = 4096
            test_signal = testsignals.noisy_sine_wave(num_samples)
            order = 5
            n = 50
            coefs = covariance(test_signal, order, n)
            predict(test_signal, coefs, 3)

        def test_burg(self):
            num_samples = 1024
            test_signal = testsignals.noisy_sine_wave(num_samples)
            order = 5
            burg(test_signal, order)

        def test_predict(self):
            coefs = np.array([1, 2, 3, 4, 5])
            test_signal = np.ones(5)
            predictions = predict(test_signal, coefs, 2)
            self.assertEquals(predictions[0], -sum(coefs))
            self.assertEquals(predictions[1], -sum(coefs[1:]) - predictions[0])

    suite = unittest.TestSuite()
    suite.addTest(TestLP('test_autocorrelation'))
    suite.addTest(TestLP('test_covariance'))
    suite.addTest(TestLP('test_burg'))
    suite.addTest(TestLP('test_predict'))
    unittest.TextTestRunner().run(suite)
