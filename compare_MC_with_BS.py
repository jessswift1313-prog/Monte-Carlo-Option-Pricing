from black_scholes import black_scholes_call
from monte_carlo import monte_carlo_call

def compare_mc_with_bs():
    C_BS = black_scholes_call(
        S_0 = 100,
        K = 100,
        r = 0.05,
        sigma = 0.20,
        T = 1.0,
    )
    print(f"Black-Scholes call price: {C_BS : .6f}")

    for i in range(2, 7):
        C_0, standard_error, ci_low, ci_high = monte_carlo_call(
            S_0 = 100,
            K = 100,
            r = 0.05,
            sigma = 0.20,
            T = 1.0,
            n_paths = 10 ** i,
            seed = 42
        )
        print(f"\nMonte Carlo call price by {10 ** i} times simulation: {C_0 : .6f}")
        print(f"The difference between Monte Carlo call price and Black-Scholes call price is {abs(C_0-C_BS) : .6f}")

def main():
    compare_mc_with_bs()

if __name__ == "__main__":
    main()