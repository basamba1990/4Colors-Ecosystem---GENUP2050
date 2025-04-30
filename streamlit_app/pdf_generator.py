from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

def generate_pdf(content: str, thumbnail_path: str, analysis: dict) -> str:
    """Génère un PDF professionnel"""
    filename = "pitch_optimise.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # En-tête avec logo
    if thumbnail_path:
        img = ImageReader(thumbnail_path)
        c.drawImage(img, 50, 750, width=80, height=80)
    
    # Titre
    c.setFont("Helvetica-Bold", 18)
    c.drawString(150, 780, "Pitch Optimisé - 4Colors")
    
    # Contenu principal
    style = styles["BodyText"]
    p = Paragraph(content.replace('\n', '<br/>'), style)
    p.wrapOn(c, 400, 600)
    p.drawOn(c, 50, 650)
    
    # Analyse
    c.setFont("Helvetica", 10)
    c.drawString(50, 200, f"Score global : {analysis.get('score', 'N/A')}/10")
    c.drawString(50, 180, f"Recommandations : {analysis.get('recommendations', '')[:100]}...")
    
    c.save()
    return filename
