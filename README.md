# Carbon Premium in EUR Corporate Credit

Does the euro corporate bond market charge a higher spread to carbon-intensive issuers? And does this premium increase with maturity?

The intuition is simple.

Transition risk is a long-term risk. It is more likely to matter over ten or twenty years than over three. If the market is pricing it into corporate bonds, we should therefore see a stronger carbon effect on long-dated bonds than on short-dated ones.

If the carbon premium is roughly the same across maturities, that would suggest that the market is not really pricing transition risk yet, regardless of what companies report.

## Why I built this

I spent a year in the ALM and investment risk team of a French institutional investor, working on a EUR 2.5 billion portfolio.

During that year, I worked on quantitative topics around ESG risk and the integration of extra-financial criteria into the investment process, mainly for the long-dated corporate bond portfolio.

That work was done internally. I wanted to rebuild the analysis from scratch using open data and make the methodology reproducible.

## The methodological point

A simple correlation between credit spreads and carbon intensity does not tell us much.

Carbon-intensive companies are often lower-rated, more leveraged and more exposed to cyclical sectors. If we simply regress credit spreads on carbon intensity, we risk picking up differences in credit quality rather than the effect of carbon risk itself.

I therefore use four specifications:

1. **Naive**: spread on carbon intensity only. This is mainly there as a baseline and a counterexample.
2. **Controlled**: adding rating, leverage, maturity and sector fixed effects.
3. **Split by maturity**: the controlled model estimated separately for bonds below and above ten years of maturity.
4. **Interaction**: carbon intensity interacted with maturity. This is the key specification, as it directly tests whether the carbon effect increases with maturity.

Standard errors are clustered by issuer. Several bonds can come from the same issuer, so treating each observation as fully independent would not be appropriate.

Credit spreads are calculated against the ECB AAA euro area zero-coupon curve, interpolated at each bond's residual maturity.

This matters because otherwise part of the difference between a three-year and a twenty-year bond would simply reflect the shape of the yield curve rather than credit risk.

Carbon intensity is log-transformed because the distribution is highly skewed. A cement producer, for example, can have an intensity around one hundred times higher than a software company. Without the transformation, a small number of issuers could have a disproportionate impact on the results.

## Repository layout

```text
main.py                   pipeline, runs end to end
src/ecb_curve.py          ECB Data Portal API, yield curve loading and interpolation
src/donnees.py            bond and issuer data, real mode and simulation mode
src/analyse.py            the four regression specifications
src/graphiques.py         three charts
data/                     CSV templates to fill with real data
output/                   charts and result tables
```

## Running it

```bash
pip install -r requirements.txt

python main.py                    # simulated sample, no data needed
python main.py --reel             # reads data/obligations.csv and data/emetteurs.csv
python main.py --reel --date 2026-06-30
```

The simulation mode makes it possible to test the full pipeline without market data. It also provides a simple way to check that the methodology is able to detect the effect when it is present.

**Simulation results are not market results.**

## Getting the data

The bond side is the difficult part. Issuer-level bond prices are rarely available for free to individual investors, while companies can access them through professional financial data providers.

* **Universe**: the ECB publishes ISIN-level holdings from its corporate purchase programme. This provides a clean universe of euro investment-grade issuers.

* **Yields**: Börse Frankfurt and Börse Stuttgart provide prices and yields by ISIN in open access. These can be collected in Python. A Bloomberg Terminal provides the same type of data through its API.

* **Risk-free curve**: ECB Data Portal, dataset `YC`. The API is free and does not require a key. The curve loading and interpolation are implemented in `src/ecb_curve.py`.

* **Carbon**: issuers' sustainability reports. Scope 1 and 2 emissions are divided by revenue to build the carbon intensity measure. I prefer building the metric directly rather than relying on a vendor score with a methodology that may not be fully transparent.

* **Controls**: ratings and leverage are collected from investor presentations and annual reports.

I would start small: twenty issuers, three bonds per issuer and one observation date.

Fifty well-matched bonds are more useful than a thousand poorly matched ones.

## Limitations

* One observation date: the analysis is a cross-section, not a time-series analysis.
* Liquidity is not controlled for. Less liquid bonds can trade at wider spreads for reasons unrelated to climate risk.
* Issuers with both green and conventional bonds would allow a cleaner comparison using same-issuer pairs. This is the natural next step.
* Sector fixed effects remove part of the carbon signal because carbon intensity is strongly related to the sector. The estimated effect is therefore likely to be conservative.

## Charts

`01_nuage_spread_maturite.png` — raw spreads by maturity, coloured by carbon intensity.

`02_residus_carbone.png` — residual spread after controlling for rating, leverage, maturity and sector, plotted against carbon intensity and split between short and long maturities.

`03_prime_par_tranche.png` — estimated carbon premium by maturity bucket with 95% confidence intervals.

Thanks for reading.

**Ryan Hendel**
