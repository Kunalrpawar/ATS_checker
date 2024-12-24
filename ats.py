import streamlit as st
import google.generativeai as genai
import os
from fpdf import FPDF
from dotenv import load_dotenv
import json
import PyPDF2 as pdf

import re
import requests

WEBHOOK_URL = "https://connect.pabbly.com/workflow/sendwebhookdata/IjU3NjYwNTZmMDYzMzA0MzA1MjZlNTUzZDUxM2Ei_pc"

# Prepare webhook data dynamically
def send_webhook_data(jd, resume_text):
    data = {"Paste the Job Description": jd, "resume": resume_text}
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Webhook request failed: {e}")
        return None
    return response

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get response from Gemini
def get_gemini_response(input_text):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_text)
    return response.text

# Function to extract text from a PDF file
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to generate an improved resume PDF
def generate_updated_resume(original_resume_text, missing_keywords, profile_summary, filename="Updated_Resume.pdf"):
    pdf = FPDF()
    pdf.add_page()

    # Set a Unicode-capable font
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=12)

    # Original Content
    pdf.multi_cell(0, 10, f"Original Resume Content:\n{original_resume_text}\n")

    # Append improvements
    pdf.ln(10)  # Add space
    pdf.set_font("DejaVu", style="B", size=12)
    pdf.cell(0, 10, "Improvements Based on ATS:")
    pdf.ln(10)
    pdf.set_font("DejaVu", size=12)
    pdf.multi_cell(0, 10, f"Missing Keywords: {', '.join(missing_keywords)}")
    pdf.multi_cell(0, 10, f"Profile Summary Update:\n{profile_summary}")

    # Save PDF
    pdf.output(filename)
    return filename

# Prompt template
input_prompt = """
Hey, act like a skilled and experienced ATS (Application Tracking System)
with a deep understanding of the tech field, software engineering, data science,
data analytics, and big data engineering. Your task is to evaluate the resume based on
the given job description. You must consider the job market is very competitive, and you
should provide the best assistance for improving the resumes. Assign the percentage matching
based on JD and the missing keywords with high accuracy.
Resume: {text}
Description: {jd}

I want the response in one single string having the structure:
{{"JD Match": "%", "MissingKeywords": [], "Profile Summary": ""}}
"""

# Streamlit App
st.set_page_config(page_title="Smart ATS", page_icon="📄", layout="wide")
st.title("📄 Smart ATS: Improve Your Resume for Success!")
st.markdown("Enhance your resume's compatibility with job descriptions and optimize it for applicant tracking systems.")
st.markdown("Made by Kunal Pawar")

# Input sections
st.sidebar.header("Input Details")
jd = st.sidebar.text_area("📋 Paste the Job Description", placeholder="Enter the job description here...")
uploaded_file = st.sidebar.file_uploader("📂 Upload Your Resume (PDF)", type="pdf", help="Please upload your resume in PDF format.")

submit = st.sidebar.button("📝 Evaluate Resume")

# Divider
st.divider()

# Main section logic
if submit:
    if not jd:
        st.error("⚠️ Please provide a job description!")
    elif not uploaded_file:
        st.error("⚠️ Please upload a resume!")
    else:
        # Extract text from uploaded resume
        with st.spinner("Processing your resume..."):
            resume_text = input_pdf_text(uploaded_file)
            prompt = input_prompt.format(text=resume_text, jd=jd)
            response = get_gemini_response(prompt)
            
            # Send data to webhook
            send_webhook_data(jd, resume_text)
        
        # Parse and display the response
        try:
            response_data = json.loads(response)
            st.success("✅ Resume Evaluation Complete!")
            
            # Display results neatly
            st.subheader("🎯 Evaluation Results")
            st.metric("📊 JD Match", f"{response_data['JD Match']}%")
            st.markdown("**🔑 Missing Keywords:**")
            st.write(", ".join(response_data["MissingKeywords"]))
            st.markdown("**📝 Profile Summary:**")
            st.write(response_data["Profile Summary"])
            
            # Check if ATS score is poor and offer to improve
            ats_score = int(response_data['JD Match'].replace('%', ''))
            if ats_score < 70:  # Poor score threshold
                st.warning("⚠️ Your ATS score is below the recommended threshold. An improved resume is ready for download.")
                
                # Generate updated resume
                updated_resume_filename = generate_updated_resume(
                    original_resume_text=resume_text,
                    missing_keywords=response_data["MissingKeywords"],
                    profile_summary=response_data["Profile Summary"]
                )
                
                # Provide download button
                with open(updated_resume_filename, "rb") as file:
                    st.download_button(
                        label="📥 Download Updated Resume",
                        data=file,
                        file_name="Updated_Resume.pdf",
                        mime="application/pdf"
                    )
            else:
                st.success("🎉 Your resume looks good! No further improvements are needed.")
        except json.JSONDecodeError:
            st.error("❌ Failed to parse the AI response. Please try again.")

# Add footer
st.divider()
st.markdown("💡 *Powered by Google Generative AI and Streamlit*")
