# Technical Notes — Monte Carlo Option Pricing V1

These are my notes for the main ideas used in the project, especially the parts I should be able to explain clearly in an interview.

## 1. European call option

A European call option gives the holder the right to buy the underlying asset at maturity \(T\) for a fixed strike price \(K\).

The payoff at maturity is

$$
(S_T-K)^+ = \max(S_T-K,0).
$$

So:

* if \(S_T \le K\), the option expires worthless;
* if \(S_T > K\), the payoff is \(S_T-K\).

One thing to keep clear is that the payoff at maturity is not the option price today. Since the payoff is received at time \(T\), it has to be discounted back to time 0.

---

## 2. Discounting

With continuous compounding at risk-free rate \(r\), one unit of money today becomes

$$
e^{rT}
$$

after \(T\) years.

So one unit received at time \(T\) is worth

$$
e^{-rT}
$$

today.

Therefore, under risk-neutral pricing,

$$
C_0=e^{-rT}\mathbb E^{\mathbb Q}[(S_T-K)^+].
$$

The expectation here is under the risk-neutral measure \(\mathbb Q\). We do not simulate the stock using its historical expected return and then discount it.

---

## 3. Risk-neutral stock dynamics

In Black–Scholes, the stock follows geometric Brownian motion. Under the risk-neutral measure,

$$
dS_t=rS_t\,dt+\sigma S_t\,dW_t.
$$

For this project I only need the terminal stock price, so I can use the exact solution directly:

$$
S_T
=
S_0\exp\left[
\left(r-\frac12\sigma^2\right)T
+\sigma\sqrt T Z
\right],
\qquad Z\sim N(0,1).
$$

This is useful because a European call only depends on \(S_T\). There is no reason to simulate the whole path between 0 and \(T\).

Parameters:

* \(S_0\): stock price today
* \(K\): strike price
* \(r\): continuously compounded risk-free rate
* \(\sigma\): annual volatility
* \(T\): maturity in years
* \(Z\): standard normal random variable

The \(-\frac12\sigma^2\) term comes from applying Itô's lemma to \(\log S_t\).

---

## 4. Black–Scholes benchmark

For a European call,

$$
C_{BS}=S_0\Phi(d_1)-Ke^{-rT}\Phi(d_2),
$$

where

$$
d_1=
\frac{\ln(S_0/K)+(r+\frac12\sigma^2)T}
{\sigma\sqrt T},
$$

and

$$
d_2=d_1-\sigma\sqrt T.
$$

I use this formula mainly as a benchmark for the Monte Carlo estimator.

This is actually one reason Black–Scholes is useful for this project. The analytical solution gives me a known answer under exactly the same model assumptions.

So if Monte Carlo does not converge towards the Black–Scholes price, the problem is numerical or in the implementation.

If both Black–Scholes and Monte Carlo disagree with actual market prices, that is a different issue: the model itself may be unrealistic.

So I want to keep these two things separate:

**numerical error vs model error.**

---

## 5. Standard Monte Carlo estimator

Generate

$$
Z_1,\ldots,Z_N\sim N(0,1)
$$

independently.

For every draw,

$$
S_T^{(i)}
=
S_0\exp\left[
\left(r-\frac12\sigma^2\right)T
+\sigma\sqrt T Z_i
\right].
$$

Then calculate the discounted payoff

$$
Y_i=e^{-rT}(S_T^{(i)}-K)^+.
$$

The Monte Carlo estimator is just the sample mean:

$$
\hat C_N=\frac1N\sum_{i=1}^{N}Y_i.
$$

Since every \(Y_i\) is sampled from the correct discounted payoff distribution,

$$
\mathbb E[\hat C_N]=C_0.
$$

So under the model, the estimator is unbiased.

---

## 6. Standard error and confidence interval

Suppose

$$
\operatorname{Var}(Y_i)=\sigma_Y^2.
$$

Because the Monte Carlo estimate is an average of \(N\) independent observations,

$$
\operatorname{Var}(\hat C_N)
=
\frac{\sigma_Y^2}{N}.
$$

Therefore,

$$
\operatorname{SE}(\hat C_N)
=
\frac{\sigma_Y}{\sqrt N}.
$$

In practice I do not know \(\sigma_Y\), so I estimate it using the sample standard deviation of the simulated discounted payoffs.

For large \(N\), I use the usual approximate 95% confidence interval

$$
\hat C_N \pm 1.96\,\widehat{\operatorname{SE}}(\hat C_N).
$$

Important: this confidence interval only measures the randomness coming from Monte Carlo sampling.

It does **not** mean that I am 95% confident about the true market value of the option. The model parameters and Black–Scholes assumptions are treated as fixed here.

---

## 7. Why the convergence rate is \(N^{-1/2}\)

From

$$
\operatorname{Var}(\hat C_N)
=
\frac{\sigma_Y^2}{N},
$$

we get

$$
\operatorname{SE}(\hat C_N)
=
O(N^{-1/2}).
$$

Since the estimator is unbiased,

$$
\operatorname{MSE}
=
\operatorname{Var}(\hat C_N)
+
\operatorname{Bias}(\hat C_N)^2
=
\operatorname{Var}(\hat C_N).
$$

Therefore,

$$
\operatorname{RMSE}
=
O(N^{-1/2}).
$$

So on a log-log plot of RMSE against \(N\), I expect a slope close to \(-1/2\).

This also shows the main weakness of brute-force Monte Carlo: convergence is slow.

To reduce the error by half, I need about four times as many simulation paths.

---

## 8. Why I repeat the experiment

One Monte Carlo result is only one random realization.

For example, if I run the model once with \(N=10000\), getting a price close to Black–Scholes might partly be luck.

So for each \(N\), I repeat the full pricing experiment several times.

I then calculate a few statistics from the repeated price estimates.

### Mean estimate

This checks whether the estimates are centered around the Black–Scholes benchmark.

### Estimator variance

Suppose the repeated estimates are

$$
\hat C_N^{(1)},\ldots,\hat C_N^{(R)}.
$$

Their sample variance tells me how much the Monte Carlo estimate changes between independent runs.

### RMSE

$$
\operatorname{RMSE}
=
\sqrt{
\frac1R
\sum_{j=1}^{R}
(\hat C_N^{(j)}-C_{BS})^2
}.
$$

This gives me a direct measure of the numerical error relative to the benchmark.

### Mean confidence interval width

I also track the average CI width to see how quickly the estimated sampling uncertainty decreases as \(N\) increases.

---

## 9. Antithetic variates

The first variance reduction method I implemented is antithetic sampling.

Instead of generating completely unrelated shocks, I generate a shock \(Z\) and pair it with \(-Z\).

The two terminal prices are

$$
S_T^+(Z)
=
S_0e^{(r-\frac12\sigma^2)T+\sigma\sqrt T Z},
$$

and

$$
S_T^-(Z)
=
S_0e^{(r-\frac12\sigma^2)T-\sigma\sqrt T Z}.
$$

Let the two discounted payoffs be \(Y(Z)\) and \(Y(-Z)\).

I then use

$$
A=\frac{Y(Z)+Y(-Z)}{2}.
$$

Because \(Z\) and \(-Z\) have the same standard normal distribution,

$$
\mathbb E[A]
=
\frac12
\left(
\mathbb E[Y(Z)]
+
\mathbb E[Y(-Z)]
\right)
=
C_0.
$$

So the expected value is unchanged.

The variance is

$$
\operatorname{Var}(A)
=
\frac14
\left[
\operatorname{Var}(Y(Z))
+
\operatorname{Var}(Y(-Z))
+
2\operatorname{Cov}(Y(Z),Y(-Z))
\right].
$$

The important part is the covariance term.

For a call option, if \(Z\) is large and positive, the stock price and payoff are usually high. The corresponding \(-Z\) tends to produce a lower stock price and payoff.

So the two payoffs tend to move in opposite directions.

If their covariance is negative, averaging them reduces variance.

### Interview version

Antithetic variates reduce variance by pairing each normal shock \(Z\) with \(-Z\). Both have the same \(N(0,1)\) distribution, so using the pair does not change the expected option price. But the two resulting payoffs tend to move in opposite directions. When one shock produces a relatively high payoff, the other usually produces a lower one. This gives negative covariance between the paired observations, and averaging them reduces the variance of the estimator. I test this in the project by comparing standard Monte Carlo and antithetic Monte Carlo under the same simulation budget.

---

## 10. Average the payoffs, not the stock prices

This was an implementation detail I had to be careful about.

The target quantity is

$$
\mathbb E[(S_T-K)^+].
$$

So for antithetic sampling I need to calculate both payoffs first:

$$
\frac{
f(S_T^+)+f(S_T^-)
}{2}.
$$

I should not first average the two stock prices and then apply the payoff function.

In general,

$$
\frac{f(S_T^+)+f(S_T^-)}{2}
\neq
f\left(
\frac{S_T^++S_T^-}{2}
\right).
$$

For a call,

$$
f(S_T)=\max(S_T-K,0),
$$

which is nonlinear.

So averaging the terminal stock prices first would change the quantity I am estimating.

---

## 11. Fixed-budget comparison

When comparing standard Monte Carlo with antithetic Monte Carlo, I want the comparison to be fair.

Giving one method more simulation work and then saying that it has lower variance would not be very meaningful.

So I compare them at the same target path budget.

The statistic I use is

$$
1-
\frac{
\widehat{\operatorname{Var}}(\hat C_{\text{anti}})
}{
\widehat{\operatorname{Var}}(\hat C_{\text{standard}})
}.
$$

For example, if this equals \(0.68\), the estimator variance in that experiment is about 68% lower using antithetic sampling.

The exact percentage will vary between runs because the comparison itself is based on simulation.

---

## 12. Why do this project if Black–Scholes is unrealistic?

The purpose of the project is not to claim that Black–Scholes perfectly describes real markets.

I am using it for two separate things.

### Numerical side

Because Black–Scholes has a closed-form European call price, I have a ground truth for checking the simulation.

That lets me test:

* whether the Monte Carlo estimator converges to the correct price;
* whether the observed convergence rate is around \(N^{-1/2}\);
* whether the confidence interval behaves as expected;
* whether antithetic sampling actually reduces estimator variance.

### Modelling side

Real markets obviously do not satisfy every Black–Scholes assumption.

Volatility is not constant, implied volatility depends on strike and maturity, prices can jump, and real markets have transaction costs, liquidity effects and many other complications.

But those are model issues.

They are different from asking whether the Monte Carlo algorithm correctly estimates the expectation implied by a given model.

That distinction between **model risk** and **numerical error** is probably the main thing I took away from this project.

---

## 13. Things I should be able to explain

Before putting this project on my CV, I should be able to explain these without reading the code:

1. European call payoff.
2. Why future payoffs are discounted by \(e^{-rT}\).
3. Why the risk-neutral GBM uses \(r\) as the drift.
4. The formula used to simulate \(S_T\).
5. How the Monte Carlo option-price estimator works.
6. What Monte Carlo standard error means.
7. Why the error decreases at approximately \(N^{-1/2}\).
8. Why I repeat the simulation many times in the convergence experiment.
9. How antithetic variates work.
10. Why negative covariance helps reduce variance.
11. Why I need a fixed-budget comparison.
12. Numerical error vs model error.

---

## 14. Scope of V1

I am deliberately keeping V1 small.

It includes:

* Black–Scholes European call pricing;
* standard Monte Carlo pricing;
* standard errors and confidence intervals;
* convergence experiments;
* RMSE analysis;
* antithetic variance reduction.

Things I may add later:

* real option data / calibration;
* implied volatility;
* control variates;
* quasi-Monte Carlo;
* Monte Carlo Greeks;
* path-dependent options;
* stochastic-volatility models.

For V1, the goal is mainly to show that I understand the basic pricing model, how Monte Carlo estimation works, how to check numerical convergence, and how variance reduction can improve the estimator.
