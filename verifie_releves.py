#!/usr/bin/env python3
"""Vérifie un relevé d'étalonnage (CSV point-virgule : reference;lecture;unite;emt).

Même règle que lib/calcul.js :
  erreur = lecture - reference (arrondie à 6 décimales)
  conforme si |erreur| <= emt (limite incluse, tolérance 1e-9)
Code de sortie : 0 si tout est conforme, 1 sinon, 2 si le fichier est illisible.
"""
import csv
import sys

COLONNES = ("reference", "lecture", "unite", "emt")


def nombre(texte):
    return float(texte.strip().replace(",", "."))


def erreur(lecture, reference):
    return round(lecture - reference, 6)


def conforme(err, emt):
    return abs(err) <= emt + 1e-9


def lire(chemin):
    with open(chemin, newline="", encoding="utf-8-sig") as f:
        lecteur = csv.DictReader(f, delimiter=";")
        manquantes = [c for c in COLONNES if c not in (lecteur.fieldnames or [])]
        if manquantes:
            raise ValueError("colonnes manquantes : " + ", ".join(manquantes))
        lignes = []
        for n, r in enumerate(lecteur, start=2):
            try:
                ref, lec, emt = nombre(r["reference"]), nombre(r["lecture"]), nombre(r["emt"])
            except (ValueError, AttributeError):
                raise ValueError(f"ligne {n} : valeur numérique invalide")
            err = erreur(lec, ref)
            lignes.append({"reference": ref, "lecture": lec, "unite": r["unite"].strip(),
                           "emt": emt, "erreur": err, "conforme": conforme(err, emt)})
        return lignes


def main(argv):
    if len(argv) != 2:
        print("Usage : python verifie_releves.py releves.csv", file=sys.stderr)
        return 2
    try:
        lignes = lire(argv[1])
    except (OSError, ValueError) as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 2
    if not lignes:
        print("Erreur : aucun point de mesure", file=sys.stderr)
        return 2

    print(f"{'Référence':>10} {'Lecture':>10} {'Unité':<6} {'Erreur':>10} {'EMT':>8}  Verdict")
    for l in lignes:
        verdict = "conforme" if l["conforme"] else "NON CONFORME"
        print(f"{l['reference']:>10.3f} {l['lecture']:>10.3f} {l['unite']:<6} "
              f"{l['erreur']:>+10.3f} {l['emt']:>8.3f}  {verdict}")
    ok = all(l["conforme"] for l in lignes)
    print(f"\nVerdict global : {'CONFORME' if ok else 'NON CONFORME'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
