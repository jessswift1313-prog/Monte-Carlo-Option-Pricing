import numpy as np

def monte_carlo_call(S_0, K, r, sigma, T, n_paths, seed = None):
    '''
    Estimate the European call option price using risk-neutral Monte Carlo simulation.

    Parameters:
        S_0: Initial stock price
        K: Strike price
        r: Annual risk-free interest rate
        sigma: Annual volatility
        T: Time to maturity
        n_paths: The number of Monte Carlo simulation paths
        seed: Seed for the random number generator
              If None, results are not reproducible across runs

    Returns:
        price: Monte carlo call option price
        standard_error: The standatd error of this simulation
        ci_low: Lower bound of a confidence interval(CI)
        ci_high: Upper bound of a confidence interval(CI) 
    '''
    if S_0 <= 0:
        raise ValueError("Initial stock price should be strictly positive.")

    if K <= 0:
        raise ValueError("Strike price should be strictly positive.")

    if sigma <= 0:
        raise ValueError("Volatility should be strictly positive.")

    if T <= 0:
        raise ValueError("Time to maturity should be strictly positive.")

    if not isinstance(n_paths, int) or n_paths <= 0:
        raise ValueError("The number of simulation paths should be a positive integer.")

    rng = np.random.default_rng(seed)

    Z = rng.standard_normal(size = n_paths)
    S_T = S_0 * np.exp((r-0.5*sigma**2)*T + sigma*np.sqrt(T)*Z) 

    payoff = np.maximum(S_T - K, 0)
    discounted_payoff = np.exp(-r * T) * payoff
    price = np.mean(discounted_payoff)

    standard_error = np.std(discounted_payoff, ddof = 1) / np.sqrt(n_paths) # Here we use sample standard deviation to replace `sigma_X`

    ci_low = price - 1.96 * standard_error
    ci_high = price + 1.96 * standard_error # Because approximately in normal distribution:
                                            # P(-1.96 <= X <= 1.96) = 95% 

    return price, standard_error, ci_low, ci_high

def monte_carlo_call_antithetic(S_0, K, r, sigma, T, n_paths, seed = None):
    '''
    Estimate the European call option price using risk-neutral Monte Carlo simulation.

    Parameters:
        S_0: Initial stock price
        K: Strike price
        r: Annual risk-free interest rate
        sigma: Annual volatility
        T: Time to maturity
        n_paths: The number of Monte Carlo simulation paths
        seed: Seed for the random number generator
              If None, results are not reproducible across runs

    Returns:
        price: Monte carlo call option price
        standard_error: The standard error of this simulation
        ci_low: Lower bound of a confidence interval(CI)
        ci_high: Upper bound of a confidence interval(CI) 
    '''
    if S_0 <= 0:
        raise ValueError("Initial stock price should be strictly positive.")

    if K <= 0:
        raise ValueError("Strike price should be strictly positive.")

    if sigma <= 0:
        raise ValueError("Volatility should be strictly positive.")

    if T <= 0:
        raise ValueError("Time to maturity should be strictly positive.")

    if not isinstance(n_paths, int) or n_paths <= 0:
        raise ValueError("The number of simulation paths should be should be a positive integer.")

    rng = np.random.default_rng(seed)

    # Z = rng.normal(loc = 0, scale = 1, size = n_paths)
    Z = rng.standard_normal(size = n_paths // 2)
    S_T1 = S_0 * np.exp((r-0.5*sigma**2)*T + sigma*np.sqrt(T)*Z)
    S_T2 = S_0 * np.exp((r-0.5*sigma**2)*T + sigma*np.sqrt(T)*(-Z)) 

    payoff1 = np.maximum(S_T1 - K, 0)
    payoff2 = np.maximum(S_T2 - K, 0)
    discounted_payoff = np.exp(-r * T) * (payoff1+payoff2)/2
    price = np.mean(discounted_payoff)

    standard_error = np.std(discounted_payoff, ddof = 1) / np.sqrt(n_paths) # Here we use sample standard deviation to replace `sigma_X`

    ci_low = price - 1.96 * standard_error
    ci_high = price + 1.96 * standard_error # Because approximately in normal distribution:
                                            # P(-1.96 <= X <= 1.96) = 95% 

    return price, standard_error, ci_low, ci_high