# Technical Notes — Monte Carlo Option Pricing V1

These are the main ideas behind the project and the things I want to be able to explain without looking at the code.

## 1. European call option

A European call gives the holder the right to buy the underlying asset at maturity $T$ for a fixed strike price $K$.

The payoff at maturity is

$$
(S_T - K)^+ = \max(S_T - K, 0).
$$

So:

- if $S_T \le K$, the payoff is 0;
- if $S_T > K$, the payoff is $S_T - K$.

The payoff at maturity is not the option price today. Since the payoff is received at time $T$, it has to be discounted back to time 0.

---

## 2. Discounting

With continuous compounding at risk-free rate $r$, one unit of money today becomes

$$
e^{rT}
$$

at time $T$.

Therefore one unit received at time $T$ is worth

$$
e^{-rT}
$$

today.

Under risk-neutral pricing,

$$
C_0 = e^{-rT} \mathbb{E}^{\mathbb{Q}}[(S_T - K)^+].
$$

The expectation is taken under the risk-neutral measure $\mathbb{Q}$.

This is why I do not simulate the stock using a historical expected return and then discount the result. Under the risk-neutral measure, the stock drift is the risk-free rate $r$.

---

## 3. Stock dynamics under Black–Scholes

Under the Black–Scholes model, the stock follows geometric Brownian motion:

$$
dS_t = rS_t \, dt + \sigma S_t \, dW_t.
$$

For this project I only need the stock price at maturity. The exact terminal solution is

$$
S_T = S_0 \exp\left(\left(r - \frac{1}{2}\sigma^2\right)T + \sigma\sqrt{T}Z\right), \qquad Z \sim N(0,1).
$$

This is enough for a European call because the payoff only depends on $S_T$. I do not need to simulate the whole stock path between 0 and $T$.

Parameters:

- $S_0$: stock price today
- $K$: strike price
- $r$: risk-free rate
- $\sigma$: annual volatility
- $T$: time to maturity in years
- $Z$: standard normal random variable

The $-\frac{1}{2}\sigma^2$ term comes from applying Itô's lemma to $\log S_t$.

---

## 4. Black–Scholes benchmark

For a European call,

$$
C_{BS} = S_0\Phi(d_1) - Ke^{-rT}\Phi(d_2),
$$

where

$$
d_1 = \frac{\ln(S_0 / K) + \left(r + \frac{1}{2}\sigma^2\right)T}{\sigma\sqrt{T}},
$$

and

$$
d_2 = d_1 - \sigma\sqrt{T}.
$$

I mainly use Black–Scholes as a benchmark.

The Monte Carlo simulation and the closed-form formula use the same model assumptions, so I already know what value the simulation should converge to.

If Monte Carlo does not converge to the Black–Scholes value, there is probably a numerical or implementation problem.

If both Black–Scholes and Monte Carlo disagree with actual market prices, that is a different issue. The model assumptions or market inputs may be unrealistic.

So throughout the project I keep **numerical error** and **model error** separate.

---

## 5. Standard Monte Carlo estimator

Generate independent normal random variables

$$
Z_1, \ldots, Z_N \sim N(0,1).
$$

For each draw,

$$
S_T^{(i)} = S_0 \exp\left(\left(r - \frac{1}{2}\sigma^2\right)T + \sigma\sqrt{T}Z_i\right).
$$

Then calculate the discounted payoff

$$
Y_i = e^{-rT}(S_T^{(i)} - K)^+.
$$

The Monte Carlo estimate is the sample mean:

$$
\hat{C}_N = \frac{1}{N}\sum_{i=1}^{N}Y_i.
$$

Since each $Y_i$ has the correct discounted payoff distribution,

$$
\mathbb{E}[\hat{C}_N] = C_0.
$$

So the estimator is unbiased under the model.

---

## 6. Standard error and confidence interval

Suppose

$$
\mathrm{Var}(Y_i) = \sigma_Y^2.
$$

Since $\hat{C}_N$ is the average of $N$ independent observations,

$$
\mathrm{Var}(\hat{C}_N) = \frac{\sigma_Y^2}{N}.
$$

Therefore,

$$
\mathrm{SE}(\hat{C}_N) = \frac{\sigma_Y}{\sqrt{N}}.
$$

In practice, $\sigma_Y$ is unknown, so I estimate it using the sample standard deviation of the simulated discounted payoffs.

For a large number of paths, I use the approximate 95% confidence interval

$$
\hat{C}_N \pm 1.96 \, \widehat{\mathrm{SE}}(\hat{C}_N).
$$

This confidence interval only measures Monte Carlo sampling uncertainty.

It is not a confidence interval for the real market value of the option. The pricing model and its parameters are treated as fixed.

---

## 7. Why the error decreases like $N^{-1/2}$

From

$$
\mathrm{Var}(\hat{C}_N) = \frac{\sigma_Y^2}{N},
$$

we get

$$
\mathrm{SE}(\hat{C}_N) = O(N^{-1/2}).
$$

For an unbiased estimator,

$$
\mathrm{MSE} = \mathrm{Var}(\hat{C}_N) + \mathrm{Bias}(\hat{C}_N)^2 = \mathrm{Var}(\hat{C}_N).
$$

Therefore,

$$
\mathrm{RMSE} = O(N^{-1/2}).
$$

So on a log-log plot of RMSE against $N$, I expect a slope close to $-1/2$.

The practical consequence is that Monte Carlo converges quite slowly.

If I want to reduce the error by a factor of 2, I need roughly 4 times as many simulation paths.

---

## 8. Why I repeat the experiment

A single Monte Carlo estimate is random.

Even if one run happens to be very close to the Black–Scholes price, that does not tell me much about how stable the estimator is.

So for each value of $N$, I repeat the complete pricing experiment several times.

From those repeated estimates I calculate a few statistics.

### Mean estimate

This shows whether the estimates are centered near the Black–Scholes benchmark.

### Estimator variance

Suppose the repeated estimates are

$$
\hat{C}_N^{(1)}, \ldots, \hat{C}_N^{(R)}.
$$

Their sample variance measures how much the estimator changes from one independent run to another.

### RMSE

$$
\mathrm{RMSE} = \sqrt{\frac{1}{R}\sum_{j=1}^{R}\left(\hat{C}_N^{(j)} - C_{BS}\right)^2}.
$$

Since the Black–Scholes value is known, this gives a direct measure of numerical error.

### Confidence interval width

I also record the average confidence interval width to see how the sampling uncertainty changes as $N$ increases.

---

## 9. Antithetic variates

The variance reduction method used in V1 is antithetic sampling.

Instead of generating two unrelated normal shocks, I generate $Z$ and pair it with $-Z$.

The corresponding terminal prices are

$$
S_T^+(Z) = S_0 \exp\left(\left(r - \frac{1}{2}\sigma^2\right)T + \sigma\sqrt{T}Z\right),
$$

and

$$
S_T^-(Z) = S_0 \exp\left(\left(r - \frac{1}{2}\sigma^2\right)T - \sigma\sqrt{T}Z\right).
$$

Let their discounted call payoffs be $Y(Z)$ and $Y(-Z)$.

I use the pair average

$$
A = \frac{Y(Z) + Y(-Z)}{2}.
$$

Since $Z$ and $-Z$ have the same $N(0,1)$ distribution,

$$
\mathbb{E}[A] = \frac{1}{2}\left(\mathbb{E}[Y(Z)] + \mathbb{E}[Y(-Z)]\right) = C_0.
$$

So the expected value does not change.

The variance of the pair average is

$$
\mathrm{Var}(A) = \frac{1}{4}\left[\mathrm{Var}(Y(Z)) + \mathrm{Var}(Y(-Z)) + 2\mathrm{Cov}(Y(Z), Y(-Z))\right].
$$

The important part is the covariance term.

For a call option, a positive $Z$ usually pushes the terminal stock price and payoff upward. The paired value $-Z$ pushes them in the opposite direction.

This makes the two payoff observations negatively related. If their covariance is negative, averaging the pair reduces variance.

### Short interview explanation

Antithetic variates pair each normal shock $Z$ with $-Z$. Both have the same standard normal distribution, so the expected option price does not change. But the two resulting call payoffs tend to move in opposite directions. This gives negative covariance between the paired observations, and averaging them reduces the variance of the Monte Carlo estimator.

---

## 10. Average payoffs, not stock prices

This is an important implementation detail.

The quantity I want to estimate is

$$
\mathbb{E}[(S_T - K)^+].
$$

So with antithetic sampling I need to calculate both payoffs first and then average them:

$$
\frac{f(S_T^+) + f(S_T^-)}{2}.
$$

I should not average the two stock prices first and then apply the payoff function.

In general,

$$
\frac{f(S_T^+) + f(S_T^-)}{2} \neq f\left(\frac{S_T^+ + S_T^-}{2}\right).
$$

For a European call,

$$
f(S_T) = \max(S_T - K, 0),
$$

which is nonlinear.

So averaging the terminal stock prices first would estimate a different quantity.

---

## 11. Fixed-budget comparison

Standard Monte Carlo and antithetic Monte Carlo should be compared using roughly the same amount of simulation work.

Otherwise the comparison is not very meaningful.

For a fixed target path budget, I compare:

- mean price estimate
- estimator variance across repeated runs
- RMSE relative to Black–Scholes

The variance reduction statistic is

$$
1 - \frac{\widehat{\mathrm{Var}}(\hat{C}_{anti})}{\widehat{\mathrm{Var}}(\hat{C}_{standard})}.
$$

For example, a value of $0.68$ means that the observed estimator variance is about 68% lower for the antithetic estimator in that experiment.

The exact percentage changes slightly between runs because the experiment itself is random.

---

## 12. Why use Black–Scholes if it is not fully realistic?

The point of the project is not to argue that Black–Scholes perfectly describes real markets.

For V1, the closed-form Black–Scholes price is useful because it gives me a clean benchmark for the numerical method.

I can check whether:

- Monte Carlo converges to the correct value;
- RMSE behaves approximately like $N^{-1/2}$;
- the confidence interval shrinks as expected;
- antithetic sampling actually reduces estimator variance.

Real option markets are more complicated. Volatility is not constant, implied volatility changes across strikes and maturities, prices can jump, and markets have transaction costs and liquidity effects.

Those are modelling issues.

They are separate from the question of whether a Monte Carlo algorithm correctly estimates the value implied by a given model.

That distinction between **model error** and **numerical error** is one of the main things I wanted to understand from this project.

---

## 13. What I should be able to explain

Before discussing this project in an interview, I should be able to explain:

1. The payoff of a European call.
2. Why the payoff is discounted by $e^{-rT}$.
3. Why risk-neutral GBM uses $r$ as the drift.
4. The formula used to simulate $S_T$.
5. How the Monte Carlo estimator is constructed.
6. What the standard error measures.
7. Why Monte Carlo error decreases like $N^{-1/2}$.
8. Why I repeat the pricing experiment many times.
9. How antithetic variates work.
10. Why negative covariance reduces variance.
11. Why the two methods should be compared under a fixed budget.
12. The difference between numerical error and model error.

---

## 14. V1 scope

V1 includes:

- Black–Scholes European call pricing
- standard Monte Carlo pricing
- standard errors and confidence intervals
- convergence experiments
- RMSE analysis
- antithetic variance reduction

Possible extensions for a later version:

- control variates
- quasi-Monte Carlo
- Monte Carlo Greeks
- path-dependent options
- real option data
- implied volatility
- stochastic volatility

For V1, I want to keep the project focused on the basic pricing framework, Monte Carlo convergence, error measurement, and one simple variance reduction method. 