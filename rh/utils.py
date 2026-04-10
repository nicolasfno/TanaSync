import os
from fpdf import FPDF
from django.conf import settings
from django.core.files.base import ContentFile
def create_file(name, month, year, amount):
    # Implémentation fictive pour créer un PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    # 2. Titre
    pdf.cell(190, 10, f"BULLETIN DE PAIE - {month.upper()}, {year}", ln=True, align="C")
    pdf.ln(10) # Saut de ligne

    # 3. Informations Employé (Police normale)
    pdf.set_font("Arial", "", 12)
    pdf.cell(100, 10, f"Employé : {name}", ln=True)
    pdf.cell(100, 10, f"Entreprise : Tanasync Corp", ln=True)
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # Ligne horizontale
    pdf.ln(10)

    # 4. Détails du salaire (Petit tableau simple)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(140, 10, "Désignation", border=1)
    pdf.cell(50, 10, "Montant", border=1, ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.cell(140, 10, "Salaire de base", border=1)
    pdf.cell(50, 10, f"{amount} EUR", border=1, ln=True, align="C")
    
    # 5. Total
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(140, 10, "NET À PAYER", border=0, align="R")
    pdf.cell(50, 10, f"{amount} EUR", border=1, align="C")

    # 6. Sauvegarde
    # On crée le dossier s'il n'existe pas
    folder_path = os.path.join(settings.MEDIA_ROOT, 'temp_payslips')
    os.makedirs(folder_path, exist_ok=True)
    
    filename = f"payslip_{name}_{month}.pdf"
    pdf_output = pdf.output(dest='S').encode('latin-1', 'replace')
    return ContentFile(pdf_output)