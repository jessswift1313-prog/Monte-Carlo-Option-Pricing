# Monte Carlo Option Pricing

A compact numerical-finance project implementing European call option pricing under the Black–Scholes framework, with Monte Carlo simulation, convergence diagnostics, confidence intervals, and antithetic variates for variance reduction.

The goal of this V1 project is not to build a production derivatives library. It is to demonstrate the core quantitative workflow:

1. start from a financial pricing model;
2. implement an analytical benchmark;
3. reproduce the price numerically with Monte Carlo simulation;
4. quantify simulation error and convergence;
5. improve estimator efficiency with a variance-reduction technique.

## Project structure

```text
monte-carlo-option-pricing/
│
├── README.md
├── black_scholes.py
├── monte_carlo.py
├── experiments.py
├── notes.md
├── requirements.txt
├── .gitignore
│
└── figures/
    ├── convergence.png
    └── variance_comparison.png
```

### File responsibilities

- `black_scholes.py`  
  European call payoff and closed-form Black–Scholes pricing benchmark.

- `monte_carlo.py`  
  Standard Monte Carlo pricing and antithetic-variates Monte Carlo pricing.

- `experiments.py`  
  Sanity checks, repeated convergence experiments, empirical RMSE / estimator variance calculations, confidence-interval diagnostics, and fixed-budget comparison between the two estimators.

- `notes.md`  
  Short mathematical and financial notes explaining the model assumptions, estimator construction, convergence rate, and variance reduction.

- `figures/`  
  Main numerical results used to communicate the project quickly.

## Model

Under the Black–Scholes assumptions, the risk-neutral stock-price dynamics are

\[
dS_t = rS_t\,dt + \sigma S_t\,dW_t.
\]

The terminal stock price therefore has the exact representation

\[
S_T = S_0\exp\left[\left(r-\frac{1}{2}\sigma^2\right)T + \sigma\sqrt{T}Z\right],
\qquad Z\sim N(0,1).
\]

For a European call with strike \(K\), the terminal payoff is

\[
(S_T-K)^+ = \max(S_T-K,0).
\]

Its time-0 risk-neutral value is

\[
C_0 = e^{-rT}\mathbb{E}^{\mathbb{Q}}[(S_T-K)^+].
\]

## Monte Carlo estimator

Using \(N\) independent simulated terminal prices,

\[
\hat C_N
= e^{-rT}\frac{1}{N}\sum_{i=1}^{N}(S_T^{(i)}-K)^+.
\]

The implementation also reports a standard error and a 95% confidence interval for the Monte Carlo estimate.

For an unbiased Monte Carlo estimator with finite variance,

\[
\mathrm{SE}(\hat C_N) \propto N^{-1/2},
\]

so achieving roughly half the statistical error requires about four times as many simulation paths.

## Convergence experiment

The project compares Monte Carlo estimates against the analytical Black–Scholes call price using repeated simulations at

```text
N = 10^2, 10^3, 10^4, 10^5, 10^6 paths.
```

For each simulation budget, the experiment records:

- mean price estimate;
- mean reported standard error;
- empirical RMSE relative to Black–Scholes;
- empirical estimator variance;
- mean confidence-interval width.

The log-log convergence plot checks the expected

\[
\mathrm{RMSE} \approx \mathrm{SE} \propto N^{-1/2}
\]

behaviour.

![Monte Carlo convergence](figures/convergence.png)

## Variance reduction: antithetic variates

The second estimator uses paired normal draws \(Z\) and \(-Z\).

Instead of generating two unrelated paths, each random shock is paired with a shock in the opposite direction. Because the call payoffs generated from these paths tend to be negatively correlated, averaging the paired payoffs can reduce estimator variance without changing the pricing target.

At a fixed simulation budget, the project compares:

- mean estimate;
- empirical estimator variance;
- RMSE;
- percentage variance reduction.

A representative run at \(N=100{,}000\) produced approximately:

| Metric | Standard MC | Antithetic MC |
|---|---:|---:|
| Mean estimate | 10.449834 | 10.445185 |
| Estimator variance | 0.00286638 | 0.00092640 |
| RMSE | 0.052644 | 0.030408 |

This corresponds to an empirical variance reduction of about **67.7%** in that run. Because the experiment uses fresh random samples, exact numbers vary between executions.

![Estimator variance comparison](figures/variance_comparison.png)

## Validation

The project uses the Black–Scholes closed-form price as a numerical benchmark.

For the standard parameter set

```text
S0    = 100
K     = 100
r     = 0.05
sigma = 0.20
T     = 1.0
```

the analytical call price is approximately

```text
10.4506
```

The experiment script also includes basic payoff and analytical-pricer sanity checks before running the simulations.

## How to run

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the experiments:

```bash
python experiments.py
```

The script prints the convergence statistics and the fixed-budget variance comparison, and generates the two figures used above.

## What this project demonstrates

This V1 focuses on a small set of transferable quantitative skills:

- translating a stochastic model into code;
- risk-neutral valuation of a derivative payoff;
- using an analytical solution as a benchmark for a numerical method;
- understanding Monte Carlo standard error and \(N^{-1/2}\) convergence;
- distinguishing model value from simulation error;
- measuring estimator performance with repeated experiments and RMSE;
- implementing and evaluating a variance-reduction technique;
- presenting numerical results clearly rather than reporting a single simulated price.

## Scope and limitations

This is intentionally a controlled benchmark problem. The Black–Scholes model assumes, among other things, constant volatility and interest rates and lognormal stock dynamics. Real markets violate these assumptions.

The purpose of the project is therefore **not** to claim that Black–Scholes perfectly describes real stock prices. Instead, the closed-form solution gives a known ground truth under the model, making it possible to test whether the Monte Carlo implementation is correct, measure its convergence, and evaluate variance-reduction methods cleanly.

Possible V2 extensions include implied-volatility inputs, market-data calibration, additional payoffs, or models for which no simple closed-form benchmark is available.
