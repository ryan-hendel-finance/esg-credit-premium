# Carbon premium in EUR corporate credit

Does the euro corporate bond market charge a higher spread to carbon intensive
issuers, and does that premium widen with maturity?

The economic intuition is straightforward. 
Transition risk materialises over ten to twenty years, not over three. 
If the market prices it at all, the effect
should be visible on long dated bonds and close to absent on short ones. A flat
term structure of the carbon premium would mean something specific: that the
market is not yet pricing transition risk, whatever issuers report.

## Why I built this

I spent a year in the ALM and investment risk team of a French institutional
investor, working on a EUR 2.5 billion portfolio. Part of that year was spent on
quantitative work around ESG risk and the integration of extra financial criteria
into the allocation, mainly on the long dated corporate bond bucket. That work
stayed internal. This repository is the public, reproducible version of the same
question, built from scratch on open data.

## The methodological point

A raw correlation between credit spread and carbon intensity proves nothing.
Carbon intensive issuers also tend to be lower rated, more leveraged and more
cyclical. Regressing spread on carbon alone measures credit quality while
believing it measures climate.

The project therefore runs four specifications:

1. Naive : spread on carbon alone, shown deliberately as a counterexample.
2. Controlled : adding rating, leverage, maturity and sector fixed effects.
3. Split by maturity : the same controlled model estimated separately below
   and above ten years.
4. Interaction : carbon interacted with maturity, which answers the question
   directly: the coefficient measures how much the carbon effect grows per
   additional year of maturity.

Standard errors are clustered by issuer, because several bonds from the same
issuer share the same credit characteristics and their residuals are not
independent.

Credit spreads are computed against the ECB AAA euro area zero coupon curve,
interpolated at each bond's residual maturity. Without that correction, comparing
a three year and a twenty year bond measures the slope of the yield curve rather
than credit risk.

(Very important) : Carbon intensity enters in logs. The distribution is heavily skewed, for example a cement
producer emits roughly a hundred times more per unit of revenue than a software
company and without the transformation a handful of issuers would drive the
whole estimate.

## Repository layout

main.py                   pipeline, runs end to end
src/ecb_curve.py          ECB Data Portal API, yield curve loading and interpolation
src/donnees.py            bond and issuer data, real mode and simulation mode
src/analyse.py            the four regression specifications
src/graphiques.py         three charts
data/                     CSV templates to fill with real data
output/                   charts and result tables

## Running it

bash
pip install -r requirements.txt

python main.py                    # simulated sample, no data needed
python main.py --reel             # reads data/obligations.csv and data/emetteurs.csv
python main.py --reel --date 2026-06-30


Simulation mode exists so the pipeline can be verified without data, and so the
methodology can be presented on its own. It encodes the hypothesis being tested,
which lets me check that the method detects the effect when the effect is there.

IMPORTANT : Results produced in simulation mode are not market results.

## Getting the data

The bond side is the hard part; issuer-level bond prices are rarely available for free to individual investors, unlike for companies that subscribe to professional financial data providers.

- Universe : the ECB publishes the ISIN level holdings of its corporate
  purchase programme, which gives a clean set of euro investment grade issuers.
  
- Yields : Boerse Frankfurt and Boerse Stuttgart display prices and yields
  per ISIN in open access, scrapeable in Python. A Bloomberg Terminal, if you
  have access, does the same in a few minutes through the API.
  
- Risk free curve : ECB Data Portal, dataset `YC`, free API, no key required.
  I have already implemented in `src/ecb_curve.py`.
  
- Carbon : 'issuers' own sustainability reports, mandatory under CSRD. Scope 1
  and 2 emissions divided by revenue. Building the metric yourself is more
  rigorous than taking a vendor score whose methodology you cannot inspect.
  
-  Variables Controls : ratings and leverage from investor presentations and annual
  reports.

Start small. Twenty issuers, three bonds each, one observation date. 
Fifty well matched bonds beat a thousand badly matched ones, and the message is the same.

## Limitations, stated upfront

- One observation date, so the results are a cross section, not a trend.
- Liquidity is not controlled for, and less liquid bonds carry a premium that has
  nothing to do with climate.
- Issuers with both green and conventional bonds outstanding would allow a
  cleaner identification through same issuer pairs. That is the natural
  extension.
- Sector fixed effects absorb part of the carbon signal, since carbon intensity
  is largely a sector characteristic.
  For this reason, the estimate is therefore conservative.

## Charts

`01_nuage_spread_maturite.png` — raw spreads by maturity, coloured by carbon
intensity.

`02_residus_carbone.png` — the one that carries the message: residual spread
after removing rating, leverage, maturity and sector, plotted against carbon,
split short versus long maturities.

`03_prime_par_tranche.png` — the estimated carbon premium by maturity bucket with
95 percent confidence intervals.

Thank you for reading.

by Ryan Hendel — [linkedin.com/in/ryan-hendel](https://www.linkedin.com/in/ryan-hendel/)
