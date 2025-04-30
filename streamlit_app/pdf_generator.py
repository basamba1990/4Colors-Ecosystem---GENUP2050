from fpdf import FPDF

def generate_pitch_pdf(summary, filename="pitch_summary.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, summary)
    pdf.output(filename)
    return filename
