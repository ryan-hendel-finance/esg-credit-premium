# Carbon Premium on the STOXX Europe 600: Equities vs Bonds

Does the market price carbon differently across equities and corporate bonds? And does this effect become stronger with bond maturity?

The intuition is simple.

Transition risk is a long-term risk. It is more likely to matter over ten or twenty years than over three. If the market is pricing it into corporate bonds, we should therefore see a stronger carbon effect on long-dated bonds than on short-dated ones.

On the equity side, the question is slightly different. If investors price carbon risk into stocks, more carbon-intensive companies could underperform over time and trade at lower valuation multiples.

The objective is therefore to compare the two markets: does carbon appear to be priced into both equities and credit, and is the effect stronger on the bond side where transition risk can be directly reflected through credit spreads?

If the carbon effect is close to zero on one of the two markets, that would suggest that carbon risk is not being priced in the same way across asset classes.

## Why I built this

I spent a year in the ALM and investment risk team of a French institutional investor, working on a EUR 2.5 billion portfolio.

During that year, I worked on quantitative topics around ESG risk and the integration of extra-financial criteria into the investment process, mainly for the long-dated corporate bond portfolio.

That work was done internally. I wanted to rebuild the analysis from scratch using open data and extend the question to both equities and corporate bonds.

The objective is not to build an ESG score, but to test whether carbon intensity is actually reflected in market prices and whether the effect differs across asset classes.

## The methodological point

A simple correlation between carbon intensity and market performance does not tell us much.

Carbon-intensive companies are often concentrated in specific sectors, have different levels of leverage and can have very different market characteristics from less carbon-intensive companies.

If we simply compare carbon intensity with returns, valuation multiples or credit spreads, we risk picking up sector composition or differences in company fundamentals rather than the effect of carbon risk itself.

I therefore control for the main characteristics that could drive the relationship.

For equities, I look at two measures:

1. **Three-year return**: whether more carbon-intensive companies have underperformed over the period.
2. **EV/EBITDA**: whether more carbon-intensive companies trade at lower valuation multiples.

The equity regressions control for company size, beta and sector fixed effects. Leverage is also included in the valuation regression.

For bonds, I use four specifications:

1. **Naive**: spread on carbon intensity only. This is mainly there as a baseline and a counterexample.
2. **Controlled**: adding rating, leverage, maturity and sector fixed effects.
3. **Split by maturity**: the controlled relationship examined separately for bonds below and above ten years of maturity.
4. **Interaction**: carbon intensity interacted with maturity. This is the key specification, as it directly tests whether the carbon effect increases with maturity.

Standard errors for the bond regressions are clustered by issuer. Several bonds can come from the same issuer, so treating each observation as fully independent would not be appropriate.

For the equity side, the analysis is performed at the company level, so each company represents one observation.

Credit spreads are calculated against the ECB AAA euro area zero-coupon curve, interpolated at each bond's residual maturity.

This matters because otherwise part of the difference between a three-year and a twenty-year bond would simply reflect the shape of the yield curve rather than credit risk.

Carbon intensity is log-transformed because the distribution is highly skewed. A cement producer, for example, can have an intensity around one hundred times higher than a software company. Without the transformation, a small number of issuers could have a disproportionate impact on the results.

## Repository layout

```text
carbone_stoxx.py           main pipeline, runs the analysis end to end
data/                      data files and templates
output/                    charts and regression results
```

## Running it

```bash
pip install -r requirements.txt

python carbone_stoxx.py
```

The current version includes a simulated sample so that the full pipeline can be tested without external market data.

The simulation is designed to reproduce the structure of the analysis and to verify that the methodology can detect relationships when they are present.

**Simulation results are not market results.**

## Getting the data

The equity side is relatively straightforward. The bond side is more difficult.

Issuer-level bond prices are rarely available for free to individual investors, while companies can access them through professional financial data providers.

* **Universe**: the STOXX Europe 600 provides the equity universe. Companies are classified using the GICS sector and industry-group structure.

* **Equity data**: company prices, market capitalisation, beta and valuation metrics can be collected from public market data sources such as Yahoo Finance. The same structure can later be connected to a professional data provider.

* **Bond universe**: the ECB publishes ISIN-level holdings from its corporate purchase programme. This provides a clean starting point for identifying euro investment-grade corporate bonds.

* **Bond yields**: Börse Frankfurt and Börse Stuttgart provide prices and yields by ISIN in open access. These can be collected in Python. A Bloomberg Terminal provides the same type of data through its API.

* **Risk-free curve**: ECB Data Portal, dataset `YC`. The API is free and does not require a key.

* **Carbon**: issuers' sustainability reports. Scope 1 and 2 emissions are divided by revenue to build the carbon intensity measure. I prefer building the metric directly rather than relying on a vendor score with a methodology that may not be fully transparent.

* **Controls**: ratings and leverage are collected from investor presentations and annual reports.

The GICS classification is particularly important here. Carbon intensity is strongly related to sector composition, but there can also be significant differences within the same sector.

For example, two companies classified within Utilities can have very different carbon profiles depending on their generation mix.

I would start small: twenty issuers, three bonds per issuer and one observation date.

Fifty well-matched bonds are more useful than a thousand poorly matched ones.

## Limitations

* One observation date for the bond analysis: the credit analysis is a cross-section, not a time-series analysis.
* The equity return analysis covers a three-year period, but this does not establish a causal relationship between carbon intensity and performance.
* Liquidity is not controlled for on the bond side. Less liquid bonds can trade at wider spreads for reasons unrelated to climate risk.
* Issuers with both green and conventional bonds would allow a cleaner comparison using same-issuer pairs. This is the natural next step.
* Sector fixed effects remove part of the carbon signal because carbon intensity is strongly related to the sector. The estimated effect is therefore likely to be conservative.
* The carbon measure is based on Scope 1 and 2 emissions divided by revenue. This does not capture the full range of transition-risk exposures, particularly Scope 3 emissions.
* The current simulated sample is designed to test the methodology and does not represent actual STOXX Europe 600 market data.

## Charts

`carbone_stoxx600.png` — overview of carbon intensity across GICS sectors, the dispersion within sectors, the relationship between carbon intensity and equity valuation, and the residual bond spread by maturity.

The last panel is the key one: residual credit spread after controlling for rating, leverage, maturity and sector, plotted against carbon intensity and split between short and long maturities.

Thanks for reading.

**Ryan Hendel**
