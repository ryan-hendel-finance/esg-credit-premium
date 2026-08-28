"""
Prime carbone sur le credit corporate euro : le marche price-t-il le risque
de transition, et le price-t-il davantage sur les maturites longues ?

Execution :

    python main.py                  echantillon simule, aucune donnee requise
    python main.py --reel           lit data/obligations.csv et data/emetteurs.csv
    python main.py --reel --date 2026-06-30

Le mode simule sert a verifier la chaine de traitement et a presenter la
methodologie. Les conclusions ne valent que sur donnees reelles.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import analyse  # noqa: E402
import donnees as module_donnees  # noqa: E402
import ecb_curve  # noqa: E402
import graphiques  # noqa: E402

pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 20)


def calculer_spreads(obligations: pd.DataFrame, date_obs: str) -> pd.DataFrame:
    """
    Convertit des rendements en spreads de credit.

    Le spread est la difference entre le rendement de l'obligation et le taux
    zero coupon souverain de meme maturite, interpole sur la courbe BCE.
    C'est la seule facon de comparer une obligation a trois ans et une
    obligation a vingt ans : sans cette correction, on mesure la pente de la
    courbe des taux et non le risque de credit.
    """
    try:
        courbe = ecb_curve.charger_courbe_ecb(date_obs)
        print(f"Courbe BCE chargee au {date_obs}, {len(courbe)} points de maturite.")
    except Exception as erreur:
        print(f"API BCE indisponible ({type(erreur).__name__}), utilisation de la courbe de secours.")
        courbe = ecb_curve.courbe_de_secours()

    taux_sans_risque = ecb_curve.interpoler_courbe(courbe, obligations["maturite_annees"].values)
    obligations = obligations.copy()
    obligations["taux_sans_risque_pct"] = taux_sans_risque
    obligations["spread_bp"] = (obligations["rendement_pct"] - taux_sans_risque) * 100.0

    negatifs = (obligations["spread_bp"] < 0).sum()
    if negatifs:
        print(f"Avertissement : {negatifs} spreads negatifs, a verifier avant interpretation.")

    return obligations


def executer(mode_reel: bool, date_obs: str) -> None:
    print("=" * 78)
    print("PRIME CARBONE SUR LE CREDIT CORPORATE EURO")
    print("=" * 78)

    if mode_reel:
        print("\nMode donnees reelles.")
        brut = module_donnees.charger_donnees_reelles()
        brut = calculer_spreads(brut, date_obs)
    else:
        print("\nMode simulation. Aucune donnee de marche utilisee.")
        brut = module_donnees.generer_donnees_simulees()

    jeu = module_donnees.preparer(brut)

    print(f"\nEchantillon : {len(jeu)} obligations, {jeu['emetteur'].nunique()} emetteurs, "
          f"{jeu['secteur'].nunique()} secteurs.")
    print(f"Maturite mediane : {jeu['maturite_annees'].median():.1f} ans. "
          f"Spread median : {jeu['spread_bp'].median():.0f} bp.")

    print("\nRepartition par secteur")
    resume_secteur = (
        jeu.groupby("secteur")
        .agg(obligations=("isin", "count"),
             spread_median_bp=("spread_bp", "median"),
             carbone_median=("intensite_carbone", "median"))
        .round(1)
        .sort_values("carbone_median", ascending=False)
    )
    print(resume_secteur.to_string())

    if len(jeu) < 30 or jeu["emetteur"].nunique() < 8:
        print("\nEchantillon insuffisant pour estimer les regressions.")
        print("Il faut au minimum une trentaine d'obligations et huit emetteurs")
        print("repartis sur plusieurs secteurs pour que les controles aient un sens.")
        print("Les fichiers de data/ sont des modeles a completer.")
        return

    print("\n" + "-" * 78)
    print("RESULTATS DES REGRESSIONS")
    print("-" * 78)
    synthese = analyse.table_synthese(jeu)
    print(synthese.to_string(index=False))

    interaction = analyse.regression_interaction(jeu)
    terme = "log_carbone:maturite_annees"
    if terme in interaction.params.index:
        pente = float(interaction.params[terme])
        p_valeur = float(interaction.pvalues[terme])
        print("\nLecture du terme d'interaction")
        print(f"  Chaque annee de maturite supplementaire ajoute {pente:.2f} bp a l'effet")
        print(f"  d'une unite de log carbone sur le spread. p-valeur : {p_valeur:.4f}.")
        if p_valeur < 0.05 and pente > 0:
            print("  Conclusion : la prime carbone se renforce avec la maturite.")
        elif p_valeur >= 0.05:
            print("  Conclusion : aucun effet de maturite statistiquement distinguable de zero.")
        else:
            print("  Conclusion : effet de maturite negatif, resultat contre-intuitif a investiguer.")

    print("\nProduction des graphiques")
    for chemin in (
        graphiques.nuage_spread_maturite(jeu),
        graphiques.residus_contre_carbone(jeu),
        graphiques.prime_par_tranche(jeu),
    ):
        print(f"  {chemin.name}")

    sortie = Path(__file__).resolve().parent / "output" / "echantillon.csv"
    jeu.to_csv(sortie, index=False)
    synthese.to_csv(Path(__file__).resolve().parent / "output" / "resultats_regressions.csv", index=False)
    print(f"  echantillon.csv et resultats_regressions.csv ecrits dans output/")


if __name__ == "__main__":
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--reel", action="store_true",
                         help="utilise data/obligations.csv et data/emetteurs.csv")
    parseur.add_argument("--date", default="2026-06-30",
                         help="date d'observation de la courbe BCE, format AAAA-MM-JJ")
    arguments = parseur.parse_args()
    executer(arguments.reel, arguments.date)
