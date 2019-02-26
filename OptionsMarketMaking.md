---
title: Options market making <small> and stochastic volatility </small>
author:
- Douglas Vieira
- Imperial College London
date: London, 26 February 2019
---


# Introduction

## Options market making

- Gap in the literature
  - Known studies: [@stoikov2009option] and [@el2015stochastic]
  
- Focus on high-frequency market making

- Combine option pricing theory with optimal market making

## ... and stochastic volatility

- Long and short time scales
  - Option pricing: Days/Months
  - Microstructure: Seconds/Minutes

- Microstructure prices don't exhibit stochastic volatility

- How does microstructure option prices depend on volatility?
  
## Approach

#. Start with price dynamics from option theory
#. Find local behaviour via small time asymptotics
#. Incorporate local dynamics to market making model

# Small time asymptotics

## Heston model example

- The price $S$ follows the SDE

$$\begin{align}
  dS_t      & = \mu S_t dt + \sqrt{V_t} S_t dW_t \\
  dV_t      & = \kappa (\theta - V_t) dt + \nu \sqrt{V_t} dZ_t \\
  d[W, Z]_t & = \rho dt \end{align}$$

- Market state is the pair $(S, V)$

## Small time asymptotics of global dynamics

*Theorem* Let $X$ be an Itô diffusion, of the form

$$ dX_t = \mu_t dt + \sigma_t dW_t, $$

$$ \text{then } \frac{X_t - \tilde X_t}{\sqrt t} \xrightarrow{L^2} 0, \text{ as } t\to 0,$$

$$ \text{where } d\tilde X_t = \sigma_0 dW_t. $$

## Heston model simulation

## {data-background-iframe="20180528/heston.html"}

## S&P 500 futures

## {data-background-iframe="20180528/sp500.html"}

## Options dynamics representation

*Theorem.* Assume the market state process $X$ is an Itô diffusion with locally
Lipschitz coefficients, invertible diffusion coefficient matrix and with open
connected support. Then, under no arbitrage, the option $C$ with
square-integrable payoff $f(X_T)$ follows

$$ C_t = \varphi(X_t), \quad dC_t = \nabla_x\varphi(X_t)dX_t, $$

$$ \text{where } \varphi(x) = \mathbb E^{\mathbb Q}[f(X_T)\mid X_t=x]. $$

## Local option price dynamics

- Applying small time asymptotics to option prices,

$$ d\tilde C_t = \nabla_x\varphi(X_0) d\tilde X_t $$

- In particular, if the market state is $(S, V)$,

$$ d\tilde C_t = \Delta_0 d\tilde S_t + \mathcal{V}_0 d\tilde V_t$$

- Options still depend on volatility
  - Despite prices losing stochastic volatility
  - Volatility links different time scales

# Market making problem

## Overview

- Following [@gueant2017optimal]

- Bid and ask quotes $S^\mathrm{ask}_t$ and $S^\mathrm{bid}_t$ are posted around
  a reference price

$$ dS_t = \sigma dW_t $$

- Trades at bid and ask prices are point processes with arrival rates

$$ \Lambda^\mathrm{ask}_t = \Lambda(S^\mathrm{ask}_t - S_t), \quad
   \Lambda^\mathrm{bid}_t = \Lambda(S^\mathrm{bid}_t - S_t) $$
$$ \Lambda(\delta) = Ae^{-k\delta} $$

## {data-background-iframe="20190226/skew_plot.html"}

## {data-background-iframe="20190226/spread_plot.html"}

## Optimisation problem

- Optimal bid and ask quotes
  - Market maker spread controls flow vs round-trip profit
  - Market maker skew controls their inventory
  
- Market maker optimises CARA utility on terminal wealth with risk aversion
  parameter $\gamma$

- Explicit solutions are not known
  - Exact solution is described as a system of ODEs
  - Approximate closed-form solution for infinite horizon exists

## Approximate solution

- Optimal spread is constant

$$ S^\mathrm{ask}_t - S^\mathrm{bid}_t
= \frac{2}{\gamma} \log\left(1 + \frac{\gamma}{k}\right)
+ \sqrt{\frac{\sigma^2\gamma}{2kA}
  \left(1 + \frac{\gamma}{k}\right)^{1+\frac{k}{\gamma}}} $$

- Optimal skew is linear

$$ \frac{S^\mathrm{ask}_t + S^\mathrm{bid}}{2} - S_t
= -q_{t-}\sqrt{\frac{\sigma^2\gamma}{2kA}
  \left(1 + \frac{\gamma}{k}\right)^{1+\frac{k}{\gamma}}} $$

## Extension to multi-asset market making

- The reference price is now a multi-dimensional Brownian motion with covariance
  matrix $\Sigma$

- Each asset has its own order arrival parameters and order size $\kappa^i$

- Solutions are analogous to the single-asset case

## Approximate solution

- Optimal spread is again constant

$$ S^{i,\mathrm{ask}}_t - S^{i,\mathrm{bid}}_t = \frac{2}{\gamma\kappa^i}
  \log\left(1+\frac{\gamma\kappa^i}{k^{i}}\right)
  + \sqrt{\frac{\gamma}{2}}\Gamma^{ii}\kappa^i $$

- Optimal skew is again linear

$$ \frac{S^{i,\mathrm{ask}}_t + S^{i,\mathrm{bid}}_t}{2} - S^i_t
= -\sqrt{\frac{\gamma}{2}}\Gamma^{i\bullet} q_{t-}, $$

## 

where
$$ \Gamma = D^{-\frac 1 2}(D^{1/2}\Sigma D^{1/2})^{1/2} D^{-\frac 1 2} $$
$$ D = \text{diag}(A^1 C_\gamma^1 k^1 \Delta^1 ,
           \ldots, A^d C_\gamma^d k^d \Delta^d), $$
$$ C_\gamma^i = \left(1+\frac{\gamma\Delta^i}{k^{i}}
    \right)^{-\left(1+\frac{k^{i}}{\gamma\Delta^i}\right)} $$

## Incorporating option dynamics

- For an underlying with dynamics

$$ \begin{align*}
dS_t & = \mu_t dt + \sigma_t dW_t \\
dV_t & = \alpha_t dt + \nu_t dZ_t, \quad
d[W, Z]_t = \rho dt
\end{align*} $$

- The small time asymptotics gives

$$ \Sigma =
\begin{bmatrix} \sigma_0\Delta_0 & \nu_0\mathcal{V}_0 \end{bmatrix}
\begin{bmatrix} 1    & \rho \\
                \rho & 1 \end{bmatrix}
\begin{bmatrix} \sigma_0\Delta_0^\top \\ \nu_0\mathcal{V}_0^\top \end{bmatrix}
+ \eta $$

# Conclusion

## Conclusions

- Role of stochastic volatility
  - Connects time scales in option prices

- Options market making model
  - Encompasses stochastic volatility
  - Tractable thanks to small time asymptotics
  - Multiple strikes and maturities
  - Passive hedging

## Thank you!

- Find this presentation and its source code at

<https://github.com/dougmvieira/presentations>

## References {.scrollable}
