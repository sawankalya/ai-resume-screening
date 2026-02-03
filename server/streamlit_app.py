import streamlit as st
import requests
import json

st.set_page_config(page_title="AI Resume Screening", layout="centered")

st.title("AI Resume Screening System")
st.write("Upload resumes and evaluate candidates against a job description.")

API_URL = "http://localhost:8000/upload_resume"

# -------- JOB DETAILS --------
jobTitle = st.text_input("Job Title")
jobDescription = st.text_area("Job Description")

degree = st.text_input("Required Degree (e.g. B.Tech, M.Sc)")
major = st.text_input("Required Major (e.g. Computer Science)")
experience = st.text_input("Required Experience (e.g. 2 years)")

# -------- SKILLS INPUT --------
skills = st.text_input("Required Technical Skills (comma separated)")
softSkills = st.text_input("Required Soft Skills (comma separated)")

# -------- FILE UPLOAD --------
uploaded_files = st.file_uploader(
    "Upload Resume PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

# -------- SUBMIT --------
if st.button("Analyze Resume(s)"):

    if not all([jobTitle, jobDescription, degree, major, experience, skills, softSkills]) or not uploaded_files:
        st.error("❌ Please fill all fields and upload at least one resume.")
        st.stop()

    # Convert skills to JSON strings (VERY IMPORTANT)
    skills_json = json.dumps([s.strip() for s in skills.split(",")])
    soft_skills_json = json.dumps([s.strip() for s in softSkills.split(",")])

    # Prepare files payload
    files = [
        ("files", (file.name, file.getvalue(), "application/pdf"))
        for file in uploaded_files
    ]

    data = {
        "jobTitle": jobTitle,
        "jobDescription": jobDescription,
        "degree": degree,
        "major": major,
        "experience": experience,
        "skills": skills_json,
        "softSkills": soft_skills_json,
    }

    with st.spinner("Analyzing resumes..."):
        response = requests.post(API_URL, data=data, files=files)

    if response.status_code != 200:
        st.error(f"Backend Error ❌\n{response.text}")
        st.stop()

    result = response.json()

    st.success("✅ Analysis Complete")

    # -------- RESULTS --------
    for filename, details in result["results"].items():
        st.subheader(f"📄 {filename}")

        if "error" in details:
            st.error(details["error"])
            continue

        st.metric("Final Score", round(details["final_score"] * 100, 2))

        st.write("**Cosine Similarity:**", round(details["cosine_similarity_score"], 3))
        st.write("**Skills Score:**", details["skills_score"])
        st.write("**Degree Score:**", details["degree_score"])
        st.write("**Education Score:**", details["education_score"])
        st.write("**Experience Score:**", details["exp_score"])

        st.write("**Extracted Information:**")
        st.json(details["info"])
