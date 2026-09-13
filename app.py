from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import re

from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="🤖",
    layout="wide"
)


# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

st.markdown("""
<style>

.main-title {
    font-size: 40px;
    font-weight: bold;
    text-align: center;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    margin-bottom: 30px;
}

.skill {
    display: inline-block;
    padding: 6px 12px;
    margin: 4px;
    border-radius: 15px;
    background-color: #e8f5e9;
}

.missing {
    display: inline-block;
    padding: 6px 12px;
    margin: 4px;
    border-radius: 15px;
    background-color: #ffebee;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">🤖 AI Resume Screening & Job Recommendation System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">NLP + Machine Learning + Skill Gap Analysis</div>',
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# LOAD JOB DATA
# ---------------------------------------------------------

@st.cache_data
def load_jobs():

    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parent
        JOBS_FILE = BASE_DIR / "data" / "jobs.csv"
         df = pd.read_csv(JOBS_FILE)
         df["skills"] = 
    df["skills"].fillna("")
         df["description"] = 
    df["description"].fillna("")

    return df


jobs = load_jobs()


# ---------------------------------------------------------
# EXTRACT TEXT FROM PDF
# ---------------------------------------------------------

def extract_pdf_text(uploaded_file):

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# ---------------------------------------------------------
# CLEAN TEXT
# ---------------------------------------------------------

def clean_text(text):

    text = text.lower()

    text = re.sub(r"[^a-zA-Z0-9+#.\- ]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text


# ---------------------------------------------------------
# SKILL DATABASE
# ---------------------------------------------------------

SKILLS = [

    "python",
    "java",
    "c++",
    "sql",
    "javascript",
    "html",
    "css",
    "react",
    "node.js",
    "git",
    "django",
    "flask",
    "api",
    "machine learning",
    "deep learning",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "nlp",
    "pandas",
    "numpy",
    "statistics",
    "excel",
    "power bi",
    "data structures",
    "data analysis",
    "computer vision",
    "opencv",
    "cloud computing",
    "aws",
    "azure",
    "docker",
    "linux"
]


# ---------------------------------------------------------
# EXTRACT SKILLS
# ---------------------------------------------------------

def extract_skills(text):

    text = clean_text(text)

    found_skills = []

    for skill in SKILLS:

        pattern = r"\b" + re.escape(skill.lower()) + r"\b"

        if re.search(pattern, text):

            found_skills.append(skill)

    return sorted(list(set(found_skills)))


# ---------------------------------------------------------
# CALCULATE JOB MATCH
# ---------------------------------------------------------

def calculate_similarity(resume_text, job_text):

    documents = [
        clean_text(resume_text),
        clean_text(job_text)
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        matrix[0:1],
        matrix[1:2]
    )[0][0]

    return similarity


# ---------------------------------------------------------
# JOB RECOMMENDATION
# ---------------------------------------------------------

def recommend_jobs(resume_text):

    results = []

    resume_skills = extract_skills(resume_text)

    for _, job in jobs.iterrows():

        job_text = (
            job["job_title"]
            + " "
            + job["skills"]
            + " "
            + job["description"]
        )

        similarity = calculate_similarity(
            resume_text,
            job_text
        )

        job_skills = [
            s.strip().lower()
            for s in job["skills"].split(",")
        ]

        matched = list(
            set(resume_skills) &
            set(job_skills)
        )

        missing = list(
            set(job_skills) -
            set(resume_skills)
        )

        if len(job_skills) > 0:

            skill_score = (
                len(matched) /
                len(job_skills)
            )

        else:

            skill_score = 0

        final_score = (
            0.6 * similarity +
            0.4 * skill_score
        ) * 100

        results.append({

            "Job Role": job["job_title"],

            "Match Score": round(
                final_score,
                2
            ),

            "Matched Skills": ", ".join(
                matched
            ),

            "Missing Skills": ", ".join(
                missing
            )

        })

    result_df = pd.DataFrame(results)

    result_df = result_df.sort_values(
        by="Match Score",
        ascending=False
    )

    return result_df, resume_skills


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title("📌 Project Information")

st.sidebar.write(
    """
This system uses:

• Natural Language Processing  
• TF-IDF Vectorization  
• Cosine Similarity  
• Skill Extraction  
• Job Recommendation  
• Skill Gap Analysis
"""
)

st.sidebar.info(
    "Upload a PDF resume to start."
)


# ---------------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------------

uploaded_file = st.file_uploader(
    "📄 Upload your Resume (PDF)",
    type=["pdf"]
)


# ---------------------------------------------------------
# PROCESS RESUME
# ---------------------------------------------------------

if uploaded_file is not None:

    with st.spinner("Analyzing resume..."):

        resume_text = extract_pdf_text(
            uploaded_file
        )

    if len(resume_text.strip()) == 0:

        st.error(
            "Could not extract text from this PDF."
        )

    else:

        st.success(
            "Resume successfully analyzed!"
        )

        # -------------------------------------------------
        # EXTRACT SKILLS
        # -------------------------------------------------

        result_df, resume_skills = recommend_jobs(
            resume_text
        )

        st.header("🧠 Extracted Skills")

        if resume_skills:

            skill_html = ""

            for skill in resume_skills:

                skill_html += (
                    f'<span class="skill">'
                    f'{skill}'
                    f'</span>'
                )

            st.markdown(
                skill_html,
                unsafe_allow_html=True
            )

        else:

            st.warning(
                "No predefined skills were detected."
            )


        # -------------------------------------------------
        # TOP JOB
        # -------------------------------------------------

        st.header("🎯 Best Job Recommendation")

        best_job = result_df.iloc[0]

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Recommended Role",
                best_job["Job Role"]
            )

        with col2:

            st.metric(
                "Match Score",
                f'{best_job["Match Score"]}%'
            )

        with col3:

            if best_job["Match Score"] >= 75:

                status = "Excellent"

            elif best_job["Match Score"] >= 50:

                status = "Good"

            else:

                status = "Needs Improvement"

            st.metric(
                "Profile Status",
                status
            )


        # -------------------------------------------------
        # ALL RECOMMENDATIONS
        # -------------------------------------------------

        st.header("💼 Job Recommendations")

        display_df = result_df[
            [
                "Job Role",
                "Match Score",
                "Matched Skills",
                "Missing Skills"
            ]
        ]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


        # -------------------------------------------------
        # SKILL GAP
        # -------------------------------------------------

        st.header("📚 Skill Gap Analysis")

        top_job = jobs[
            jobs["job_title"] ==
            best_job["Job Role"]
        ].iloc[0]

        required_skills = [

            s.strip().lower()

            for s in top_job["skills"].split(",")

        ]

        user_skills = [

            s.lower()

            for s in resume_skills

        ]

        missing_skills = list(
            set(required_skills) -
            set(user_skills)
        )

        if missing_skills:

            st.warning(
                "Skills you should improve:"
            )

            missing_html = ""

            for skill in missing_skills:

                missing_html += (
                    f'<span class="missing">'
                    f'{skill}'
                    f'</span>'
                )

            st.markdown(
                missing_html,
                unsafe_allow_html=True
            )

        else:

            st.success(
                "🎉 You have all the major skills "
                "required for this role!"
            )


        # -------------------------------------------------
        # MATCHED SKILLS
        # -------------------------------------------------

        st.header("✅ Matching Skills")

        matched_skills = list(
            set(required_skills) &
            set(user_skills)
        )

        if matched_skills:

            st.write(
                ", ".join(matched_skills)
            )

        else:

            st.write(
                "No matching skills found."
            )


        # -------------------------------------------------
        # RESUME PREVIEW
        # -------------------------------------------------

        with st.expander(
            "📄 View Extracted Resume Text"
        ):

            st.text_area(
                "Resume Content",
                resume_text,
                height=300
            )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown("---")

st.caption(
    "B.Tech AI & ML Major Project | "
    "AI Resume Screening & Job Recommendation System"
)
