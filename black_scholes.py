import numpy as np

from scipy.stats import norm
from monte_carlo import monte_carlo_call, monte_carlo_call_antithetic

def call_payoff(S_T, K):
    """
    Calculate the payoff of a European call option.

    Parameters:
        S_T: Stock price at maturity (could possibly be 0)
        K: Strike price

    Returns:
        The call option payoff
    """
    if S_T < 0:
        raise ValueError("Stock price at maturity cannot be negative.")

    if K <= 0:
        raise ValueError("Strike price should be strictly positive.")

    return max(S_T - K, 0)


def black_scholes_call(S_0, K, r, sigma, T):
    """
    Calculate the European call option price using the Black-Scholes model.

    Parameters:
        S_0: Initial stock price
        K: Strike price
        r: Annual risk-free interest rate
        sigma: Annual volatility
        T: Time to maturity

    Returns:
        Black-Scholes call option price
    """
    if S_0 <= 0:
        raise ValueError("Initial stock price should be strictly positive.")

    if K <= 0:
        raise ValueError("Strike price should be strictly positive.")

    if sigma <= 0:
        raise ValueError("Volatility should be strictly positive.")

    if T <= 0:
        raise ValueError("Time to maturity should be strictly positive.")

    d1 = (
        np.log(S_0 / K) + (r + 0.5 * sigma**2) * T
    ) / (sigma * np.sqrt(T))

    d2 = d1 - sigma * np.sqrt(T)

    C_BS = S_0 * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2)
    
    return C_BS