import numpy as np
import matplotlib.pyplot as plt

from black_scholes import black_scholes_call, call_payoff
from monte_carlo import monte_carlo_call, monte_carlo_call_antithetic

def test_payoff():
    assert call_payoff(80, 100) == 0
    assert call_payoff(100, 100) == 0
    assert call_payoff(120, 100) == 20


def test_bs_call_standard():
    C_BS = black_scholes_call(
        S_0 = 100,
        K = 100,
        r = 0.05,
        sigma = 0.20,
        T = 1.0,
    )
    assert np.isclose(C_BS, 10.4506)

def repeated_convergence_experiment(pricing_function, output_option = True):
    n_paths = [100, 1000, 10000, 100000, 1000000]
    repeated_times = 30

    results = {
        "n_paths": [],
        "mean_estimates": [],
        "mean_ses": [],
        "rmses": [],
        "variances": [],
        "mean_ci_widths": []
    }

    rmses = []
    mean_ses = []

    C_BS = black_scholes_call(
        S_0 = 100,
        K = 100,
        r = 0.05,
        sigma = 0.20,
        T = 1.0,
    )

    for N in n_paths:
        price_estimates = []
        standard_errors = []
        ci_widths = []

        for _ in range(repeated_times):
            price, standard_error, ci_low, ci_high = pricing_function(
                S_0 = 100,
                K = 100,
                r = 0.05,
                sigma = 0.20,
                T = 1.0,
                n_paths = N,
                seed = None
            )

            price_estimates.append(price)
            standard_errors.append(standard_error)
            ci_widths.append(ci_high - ci_low)

        price_estimates = np.array(price_estimates)

        mean_estimate = np.mean(price_estimates)
        mean_standard_error = np.mean(standard_errors)
        mean_ci_width = np.mean(ci_widths)
        estimator_variance = np.var(price_estimates, ddof = 1)
        rmse = np.sqrt(
            np.mean((price_estimates - C_BS) ** 2)
        )

        rmses.append(rmse)
        mean_ses.append(mean_standard_error)

        if output_option:
            print(f"\nN = {N}, repeated {repeated_times} times")
            print(f"    Mean price estimate:          {mean_estimate:.6f}")
            print(f"    Mean standard error:         {mean_standard_error:.6f}")
            print(f"    Empirical RMSE:              {rmse:.6f}")
            print(f"    Mean confidence interval width: {mean_ci_width:.6f}")

            

        results["n_paths"].append(N)
        results["mean_estimates"].append(mean_estimate)
        results["mean_ses"].append(mean_standard_error)
        results["rmses"].append(rmse)
        results["variances"].append(estimator_variance)
        results["mean_ci_widths"].append(mean_ci_width)

    if output_option:
        fig, ax = plt.subplots(figsize=(8, 6)) 
 
        ax.plot( 
            n_paths, 
            rmses, 
            marker="o", 
            label="Monte Carlo RMSE" 
        ) 
    
        ax.set_xscale("log") 
        ax.set_yscale("log") 
    
        ax.set_xlabel("Number of simulation paths") 
        ax.set_ylabel("RMSE") 
        ax.set_title("Monte Carlo RMSE Convergence (Log-Log Scale)") 
    
        ax.plot( 
            n_paths,  
            rmses[0] * np.sqrt(n_paths[0]) * np.array(n_paths) ** -0.5,  
            color = "black",  
            linestyle = '--', 
            linewidth = 0.8,  
            label = "N^-0.5 reference line" 
        ) 
    
        ax.grid(True, which = "both", alpha=0.3) 
        ax.legend() 

        ax.text(
            0.05,
            0.07,
            r"Unbiased Monte Carlo estimator"
            "\n"
            r"$\mathrm{RMSE} \approx \mathrm{SE} \propto N^{-1/2}$",
            transform = ax.transAxes,
            fontsize = 10,
            verticalalignment = "bottom",
            horizontalalignment = "left",
            bbox = dict(
                boxstyle = "round",
                facecolor = "white",
                edgecolor = "0.7",
                alpha = 0.9
            )
        )
        
        fig.tight_layout() 
        fig.savefig("convergence.png", dpi=300) 

    return results

def variance_reduction_experiment():
    results_standard = repeated_convergence_experiment(monte_carlo_call, False)
    results_antithetic = repeated_convergence_experiment(monte_carlo_call_antithetic, False)

    target_N = 100000

    index = results_standard["n_paths"].index(target_N)

    standard_mean = results_standard["mean_estimates"][index]
    antithetic_mean = results_antithetic["mean_estimates"][index]

    standard_rmse = results_standard["rmses"][index]
    antithetic_rmse = results_antithetic["rmses"][index]

    standard_variance = results_standard["variances"][index]
    antithetic_variance = results_antithetic["variances"][index]

    variance_reduction = 1 - antithetic_variance / standard_variance

    print(f"\nFixed-budget comparison: N = {target_N}")

    print(
        f"{'Metric':<25}"
        f"{'Standard MC':>20}"
        f"{'Antithetic MC':>20}"
    )

    print("-" * 65)

    print(
        f"{'Mean estimate':<25}"
        f"{standard_mean:>20.6f}"
        f"{antithetic_mean:>20.6f}"
    )

    print(
        f"{'Estimator variance':<25}"
        f"{standard_variance:>20.8f}"
        f"{antithetic_variance:>20.8f}"
    )

    print(
        f"{'RMSE':<25}"
        f"{standard_rmse:>20.6f}"
        f"{antithetic_rmse:>20.6f}"
    )

    print(
        f"\nVariance reduction: "
        f"{variance_reduction:.2%}"
    )

    fig, ax = plt.subplots(figsize=(7, 5))

    methods = ["Standard MC", "Antithetic MC"]
    variances = [standard_variance, antithetic_variance]

    ax.bar(methods, variances)

    ax.set_ylabel("Estimator Variance")
    ax.set_title(f"Estimator Variance Comparison (N = {target_N})")

    ax.grid(True, axis="y", alpha = 0.3)

    fig.tight_layout()
    fig.savefig("variance_comparison.png", dpi=300)


def main():
    test_payoff()
    test_bs_call_standard()

    repeated_convergence_experiment(monte_carlo_call)
    variance_reduction_experiment()

    print("\nAll tests passed!")


if __name__ == "__main__":
    main()