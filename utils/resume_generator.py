from fpdf import FPDF

def generate_updated_resume(original_resume_text, missing_keywords, profile_summary, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=12)

    pdf.multi_cell(0, 10, f"Original Resume:\n{original_resume_text}\n")
    pdf.ln(10)
    pdf.set_font("DejaVu", style="B", size=12)
    pdf.cell(0, 10, "Suggested Improvements:")
    pdf.ln(10)
    pdf.set_font("DejaVu", size=12)
    pdf.multi_cell(0, 10, f"Missing Keywords: {', '.join(missing_keywords)}")
    pdf.multi_cell(0, 10, f"Profile Summary:\n{profile_summary}")

    pdf.output(filename)
    return filename
