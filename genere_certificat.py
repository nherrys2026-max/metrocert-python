#!/usr/bin/env python3
"""Génère certificat-exemple.pdf à partir d'un relevé CSV (nécessite reportlab).
Usage : python genere_certificat.py releves_ok.csv certificat-exemple.pdf
Toutes les données d'identification sont fictives.
"""
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from verifie_releves import lire

MENTION = "Prototype pédagogique GET 409 — données fictives"
INK, STEEL, OK, LINE = (colors.HexColor(c) for c in ("#1a2330", "#4a6178", "#1f7a4d", "#c9d1d9"))
INCERTITUDE = 0.15  # °C, k = 2 — valeur fictive


def fmt(x, signe=False):
    return format(x, "+.2f" if signe else ".2f").replace(".", ",")


def pied(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(colors.HexColor("#b4540a"))
    canvas.drawCentredString(A4[0] / 2, 12 * mm, MENTION)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(STEEL)
    canvas.drawCentredString(A4[0] / 2, 8 * mm, "Certificat N° SN-2026-0001 — page 1/1")
    canvas.restoreState()


def tableau(donnees, largeurs, entete=True):
    t = Table(donnees, colWidths=largeurs)
    style = [("FONT", (0, 0), (-1, -1), "Helvetica", 9), ("TEXTCOLOR", (0, 0), (-1, -1), INK),
             ("GRID", (0, 0), (-1, -1), 0.5, LINE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
             ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
    if entete:
        style += [("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f6"))]
    t.setStyle(TableStyle(style))
    return t


def main(csv_path, pdf_path):
    lignes = lire(csv_path)
    ok = all(l["conforme"] for l in lignes)
    emt = lignes[0]["emt"]
    unite = lignes[0]["unite"]
    s = getSampleStyleSheet()
    titre = ParagraphStyle("t", parent=s["Title"], fontName="Helvetica-Bold", fontSize=20, textColor=INK, alignment=0)
    h2 = ParagraphStyle("h", parent=s["Heading2"], fontName="Helvetica-Bold", fontSize=11, textColor=STEEL, spaceBefore=10, spaceAfter=4)
    txt = ParagraphStyle("p", parent=s["Normal"], fontName="Helvetica", fontSize=9, textColor=INK, leading=12)

    doc = SimpleDocTemplate(pdf_path, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=15 * mm, bottomMargin=20 * mm,
                            title="Certificat d'étalonnage — exemple fictif", author="Laboratoire fictif")
    L = 174 * mm
    h = [
        Paragraph("<b>Laboratoire d'étalonnage Teranga Métrologie</b> (fictif)<br/>12 avenue des Instruments, Dakar, Sénégal (adresse fictive)", txt),
        Paragraph("N° unique<br/><b>SN-2026-0001</b>", ParagraphStyle("r", parent=txt, alignment=2)),
    ]
    story = [tableau([h], [120 * mm, 54 * mm], entete=False), Spacer(1, 8),
             Paragraph("Certificat d'étalonnage", titre),
             Paragraph(MENTION, ParagraphStyle("m", parent=txt, textColor=colors.HexColor("#b4540a"), fontName="Helvetica-Bold")),
             Paragraph("Identification", h2),
             tableau([["Client", "Société Exemple SARL, Dakar (fictif)"],
                      ["Instrument", "Thermomètre numérique à sonde, marque Fictia, modèle T-100, n° de série TH-0042"],
                      ["Date d'étalonnage", "6 octobre 2026"],
                      ["Date d'émission", "6 octobre 2026"]], [40 * mm, 134 * mm], entete=False),
             Paragraph("Méthode", h2),
             Paragraph("Étalonnage par comparaison à un thermomètre étalon dans un bain thermostaté, 5 points de mesure "
                       "(procédure interne fictive PE-TEMP-01). Erreur = lecture - référence ; "
                       f"règle de décision : conforme si la valeur absolue de l'erreur est inférieure ou égale à l'EMT ({fmt(emt)} {unite}), limite incluse.", txt),
             Paragraph("Résultats", h2)]
    rows = [[f"Référence ({unite})", f"Lecture ({unite})", f"Erreur ({unite})", f"EMT ({unite})", "Verdict"]]
    for l in lignes:
        rows.append([fmt(l["reference"]), fmt(l["lecture"]), fmt(l["erreur"], True), fmt(l["emt"]),
                     "Conforme" if l["conforme"] else "Non conforme"])
    story += [tableau(rows, [38 * mm, 34 * mm, 34 * mm, 32 * mm, 36 * mm]), Spacer(1, 6),
              Paragraph(f"<b>Incertitude élargie : U = ± {fmt(INCERTITUDE)} {unite}</b> (k = 2, niveau de confiance d'environ 95 %) — valeur fictive.", txt),
              Spacer(1, 4),
              Paragraph(f"<b>Conclusion : {'CONFORME' if ok else 'NON CONFORME'}</b> pour l'ensemble des points.",
                        ParagraphStyle("c", parent=txt, fontSize=11, textColor=OK if ok else colors.HexColor("#b3261e"))),
              Paragraph("Traçabilité métrologique", h2),
              Paragraph("Les résultats sont raccordés au Système international d'unités (SI) par l'intermédiaire du thermomètre étalon "
                        "n° ET-0007 (fictif), étalonné par un laboratoire national de métrologie fictif, certificat n° LNM-2026-118 (fictif).", txt),
              Paragraph("Conditions ambiantes", h2),
              Paragraph("Lieu : laboratoire, Dakar. Température ambiante 23 °C ± 2 °C ; humidité relative 55 % ± 10 % (valeurs fictives).", txt),
              Spacer(1, 14),
              Paragraph("Signature", h2),
              tableau([["Responsable technique : Mame Diarra Sow (fictive)", "Signature et cachet"],
                       ["Fait à Dakar, le 6 octobre 2026", "\n\n\n"]], [87 * mm, 87 * mm])]
    doc.build(story, onFirstPage=pied)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
