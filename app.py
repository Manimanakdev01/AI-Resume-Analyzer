import streamlit as st
import PyPDF2
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import re
from collections import Counter
from io import StringIO
import json

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Resume Analyzer Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root variables ── */
:root {
    --bg:        #0d0f14;
    --surface:   #161923;
    --border:    #252a36;
    --accent:    #4f8ef7;
    --accent2:   #a78bfa;
    --success:   #34d399;
    --warn:      #fbbf24;
    --danger:    #f87171;
    --text:      #e2e8f0;
    --muted:     #64748b;
}

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background-color: var(--bg) !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: var(--surface);
    border: 2px dashed var(--border);
    border-radius: 12px;
    padding: 1rem;
}
[data-testid="stFileUploader"]:hover { border-color: var(--accent); }

/* ── Metric cards ── */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    text-align: center;
    transition: transform .2s, border-color .2s;
}
.metric-card:hover { transform: translateY(-3px); border-color: var(--accent); }
.metric-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2.4rem;
    line-height: 1;
    margin-bottom: .3rem;
}
.metric-label { font-size: .78rem; color: var(--muted); letter-spacing: .06em; text-transform: uppercase; }

/* ── Section headers ── */
.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.3rem;
    letter-spacing: .02em;
    margin: 1.6rem 0 .8rem;
    padding-bottom: .4rem;
    border-bottom: 1px solid var(--border);
}

/* ── Skill chips ── */
.chip-wrap { display: flex; flex-wrap: wrap; gap: .45rem; margin: .5rem 0 1rem; }
.chip {
    display: inline-block;
    padding: .28rem .8rem;
    border-radius: 999px;
    font-size: .78rem;
    font-weight: 500;
    letter-spacing: .03em;
}
.chip-found  { background: rgba(52,211,153,.15); color: #34d399; border: 1px solid rgba(52,211,153,.3); }
.chip-miss   { background: rgba(248,113,113,.12); color: #f87171; border: 1px solid rgba(248,113,113,.25); }
.chip-tool   { background: rgba(79,142,247,.12);  color: #4f8ef7; border: 1px solid rgba(79,142,247,.25); }
.chip-soft   { background: rgba(167,139,250,.12); color: #a78bfa; border: 1px solid rgba(167,139,250,.25); }

/* ── Score ring label ── */
.score-label {
    font-family: 'DM Serif Display', serif;
    font-size: 1.1rem;
    text-align: center;
    margin-top: -.5rem;
    margin-bottom: 1rem;
    color: var(--muted);
}

/* ── Text area & inputs ── */
textarea, input[type="text"] {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
textarea:focus, input[type="text"]:focus { border-color: var(--accent) !important; }

/* ── Buttons ── */
.stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: .04em !important;
    padding: .5rem 1.4rem !important;
    transition: opacity .2s !important;
}
.stButton > button:hover { opacity: .85 !important; }

/* ── Tabs ── */
.stTabs [role="tablist"] { border-bottom: 1px solid var(--border); }
.stTabs [role="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    font-weight: 500;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}

/* ── Progress bars ── */
.stProgress > div > div { background: var(--accent) !important; }

/* ── Expander ── */
details { background: var(--surface); border: 1px solid var(--border) !important; border-radius: 10px; }
summary { color: var(--text) !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Hero header ── */
.hero {
    background: linear-gradient(135deg, #161923 0%, #1a1f2e 50%, #161923 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(79,142,247,.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    margin: 0 0 .3rem;
    background: linear-gradient(90deg, #e2e8f0, #4f8ef7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub { color: var(--muted); font-size: .92rem; margin: 0; }
</style>
""", unsafe_allow_html=True)


# ── Skill definitions ──────────────────────────────────────────────────────────
SKILL_CATEGORIES = {
    "Programming Languages": [
        "python", "javascript", "java", "c++", "c#", "typescript", "go", "rust",
        "kotlin", "swift", "php", "ruby", "scala", "r", "matlab", "bash",
    ],
    "Web & Frameworks": [
        "react", "angular", "vue", "django", "flask", "fastapi", "node.js",
        "express", "spring", "laravel", "rails", "next.js", "nuxt", "svelte",
        "html", "css", "tailwind", "bootstrap",
    ],
    "Data & ML": [
        "machine learning", "deep learning", "nlp", "computer vision",
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
        "opencv", "xgboost", "spark", "hadoop", "tableau", "power bi",
        "data analysis", "statistics", "data visualization",
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
        "jenkins", "github actions", "ci/cd", "linux", "nginx", "redis",
        "microservices", "devops",
    ],
    "Databases": [
        "sql", "mysql", "postgresql", "mongodb", "sqlite", "oracle",
        "elasticsearch", "cassandra", "dynamodb", "firebase",
    ],
    "Soft Skills": [
        "leadership", "communication", "teamwork", "problem solving",
        "project management", "agile", "scrum", "collaboration",
        "critical thinking", "adaptability", "time management",
    ],
}

ALL_SKILLS_FLAT = {skill for skills in SKILL_CATEGORIES.values() for skill in skills}


# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_file) -> str:
    reader = PyPDF2.PdfReader(pdf_file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_text_from_txt(txt_file) -> str:
    return txt_file.read().decode("utf-8", errors="ignore")


def analyze_skills(text: str, custom_skills: list[str] | None = None):
    low = text.lower()
    results = {}
    for cat, skills in SKILL_CATEGORIES.items():
        results[cat] = {"found": [], "missing": []}
        for s in skills:
            (results[cat]["found"] if s in low else results[cat]["missing"]).append(s)

    if custom_skills:
        results["Custom Skills"] = {"found": [], "missing": []}
        for s in custom_skills:
            s = s.strip().lower()
            if s:
                (results["Custom Skills"]["found"] if s in low else results["Custom Skills"]["missing"]).append(s)

    total_found = sum(len(v["found"]) for v in results.values())
    total = sum(len(v["found"]) + len(v["missing"]) for v in results.values())
    score = round(total_found / total * 100, 1) if total else 0
    return results, score, total_found, total


def jd_match(resume_text: str, jd_text: str):
    jd_low = jd_text.lower()
    resume_low = resume_text.lower()
    jd_keywords = set(re.findall(r'\b[a-z][a-z+#.]{2,}\b', jd_low))
    stopwords = {"the","and","for","with","are","that","have","this","from","your",
                 "will","you","our","can","has","but","not","all","been","their",
                 "more","they","also","when","than","into","each","other"}
    jd_keywords -= stopwords
    matched = {k for k in jd_keywords if k in resume_low}
    score = round(len(matched) / len(jd_keywords) * 100, 1) if jd_keywords else 0
    missing = sorted(jd_keywords - matched)
    return score, sorted(matched), missing[:40]


def word_frequency(text: str, top_n: int = 20):
    words = re.findall(r'\b[a-z][a-z]{3,}\b', text.lower())
    stopwords = {"with","that","have","this","from","your","will","they","been",
                 "their","more","also","when","than","into","each","other","which",
                 "were","about","these","those","there","where","while","after",
                 "before","should","would","could","using","used","work","skills",
                 "experience","years","team","able","well"}
    words = [w for w in words if w not in stopwords]
    return Counter(words).most_common(top_n)


def score_color(score: float) -> str:
    if score >= 75: return "#34d399"
    if score >= 45: return "#fbbf24"
    return "#f87171"


def gauge_chart(score: float, title: str = "Match Score"):
    color = score_color(score)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%", "font": {"size": 36, "color": color, "family": "DM Serif Display"}},
        title={"text": title, "font": {"size": 14, "color": "#64748b", "family": "DM Sans"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#252a36", "tickfont": {"color": "#64748b"}},
            "bar": {"color": color, "thickness": .25},
            "bgcolor": "#161923",
            "bordercolor": "#252a36",
            "steps": [
                {"range": [0, 45],  "color": "rgba(248,113,113,.08)"},
                {"range": [45, 75], "color": "rgba(251,191,36,.08)"},
                {"range": [75, 100],"color": "rgba(52,211,153,.08)"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": .75, "value": score},
        },
    ))
    fig.update_layout(
        height=240, margin=dict(t=30, b=0, l=20, r=20),
        paper_bgcolor="#0d0f14", font_color="#e2e8f0",
    )
    return fig


def bar_chart_categories(results: dict):
    cats, pcts = [], []
    for cat, data in results.items():
        total = len(data["found"]) + len(data["missing"])
        if total:
            cats.append(cat)
            pcts.append(round(len(data["found"]) / total * 100, 1))

    colors = [score_color(p) for p in pcts]
    fig = go.Figure(go.Bar(
        x=pcts, y=cats, orientation="h",
        marker_color=colors, marker_line_width=0,
        text=[f"{p}%" for p in pcts], textposition="outside",
        textfont=dict(color="#e2e8f0", size=12),
    ))
    fig.update_layout(
        height=max(240, len(cats) * 48),
        margin=dict(t=10, b=10, l=10, r=60),
        paper_bgcolor="#0d0f14", plot_bgcolor="#0d0f14",
        xaxis=dict(range=[0, 115], showgrid=False, visible=False),
        yaxis=dict(tickfont=dict(color="#e2e8f0", size=12), showgrid=False),
        bargap=.4,
    )
    return fig


def word_freq_chart(freq: list):
    words, counts = zip(*freq) if freq else ([], [])
    fig = px.bar(
        x=list(counts), y=list(words), orientation="h",
        color=list(counts), color_continuous_scale=["#4f8ef7","#a78bfa"],
    )
    fig.update_layout(
        height=420, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="#0d0f14", plot_bgcolor="#0d0f14",
        showlegend=False, coloraxis_showscale=False,
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(tickfont=dict(color="#e2e8f0", size=11), showgrid=False, autorange="reversed"),
    )
    return fig


def chips_html(items: list, cls: str) -> str:
    if not items:
        return "<span style='color:#64748b;font-size:.85rem'>None found</span>"
    return '<div class="chip-wrap">' + "".join(f'<span class="chip {cls}">{i}</span>' for i in items) + "</div>"


def generate_report(resume_text, results, overall_score, jd_score=None) -> str:
    lines = ["# Resume Analysis Report\n"]
    lines.append(f"**Overall Skill Score:** {overall_score}%")
    if jd_score is not None:
        lines.append(f"**JD Match Score:** {jd_score}%\n")
    lines.append("\n## Skills by Category\n")
    for cat, data in results.items():
        lines.append(f"### {cat}")
        lines.append(f"- Found: {', '.join(data['found']) or 'None'}")
        lines.append(f"- Missing: {', '.join(data['missing']) or 'None'}\n")
    return "\n".join(lines)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")

    custom_skills_input = st.text_area(
        "Add custom skills (one per line)",
        placeholder="e.g.\nGraphQL\nFigma\nDBT",
        height=120,
    )
    custom_skills = [s.strip().lower() for s in custom_skills_input.split("\n") if s.strip()]

    st.markdown("---")
    st.markdown("### 📋 Job Description Match")
    jd_text = st.text_area(
        "Paste a job description",
        placeholder="Paste the full JD here to see how well your resume matches…",
        height=200,
    )

    st.markdown("---")
    st.markdown("### 📖 About")
    st.markdown("""
    **Resume Analyzer Pro** evaluates your resume across 6 skill categories,
    calculates match scores, and surfaces keyword gaps — helping you tailor
    your resume for any role.
    """)


# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">📄 Resume Analyzer Pro</div>
  <p class="hero-sub">Upload your resume and instantly see skill coverage, category breakdown, keyword density, and job description match.</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload your resume", type=["pdf", "txt"],
    help="Supported formats: PDF, TXT",
    label_visibility="collapsed",
)

if not uploaded_file:
    st.markdown("""
    <div style="text-align:center;padding:3rem;color:#64748b;">
        <div style="font-size:3rem;margin-bottom:.8rem">📂</div>
        <div style="font-size:1rem">Drop your resume above to get started</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Extract text ──────────────────────────────────────────────────────────────
with st.spinner("Reading your resume…"):
    if uploaded_file.name.endswith(".pdf"):
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = extract_text_from_txt(uploaded_file)

if not resume_text.strip():
    st.error("⚠️ Could not extract text from this file. Try a different PDF or a plain-text version.")
    st.stop()

# ── Analysis ──────────────────────────────────────────────────────────────────
results, overall_score, total_found, total_skills = analyze_skills(resume_text, custom_skills)
jd_score, jd_matched, jd_missing = (jd_match(resume_text, jd_text) if jd_text.strip() else (None, [], []))
freq = word_frequency(resume_text)

# ── KPI row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
kpi_data = [
    (k1, f"{overall_score}%", "Skill Coverage",  score_color(overall_score)),
    (k2, str(total_found),    "Skills Found",     "#4f8ef7"),
    (k3, str(total_skills - total_found), "Skills to Add", "#f87171"),
    (k4, f"{jd_score}%" if jd_score is not None else "—", "JD Match", score_color(jd_score) if jd_score else "#64748b"),
]
for col, val, label, color in kpi_data:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:{color}">{val}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🧩 Skills Detail", "📝 JD Match", "📖 Raw Text"])

# ─── Tab 1: Overview ─────────────────────────────────────────────────────────
with tab1:
    col_a, col_b = st.columns([1, 1.8])

    with col_a:
        st.markdown('<div class="section-title">Overall Score</div>', unsafe_allow_html=True)
        st.plotly_chart(gauge_chart(overall_score, "Skill Coverage"), use_container_width=True)
        grade = "Excellent 🏆" if overall_score >= 75 else "Good 👍" if overall_score >= 45 else "Needs Work 🔧"
        st.markdown(f'<div class="score-label">{grade}</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="section-title">Coverage by Category</div>', unsafe_allow_html=True)
        st.plotly_chart(bar_chart_categories(results), use_container_width=True)

    st.markdown('<div class="section-title">Top Keywords in Your Resume</div>', unsafe_allow_html=True)
    st.plotly_chart(word_freq_chart(freq), use_container_width=True)


# ─── Tab 2: Skills Detail ─────────────────────────────────────────────────────
with tab2:
    for cat, data in results.items():
        found, missing = data["found"], data["missing"]
        total_cat = len(found) + len(missing)
        pct = round(len(found) / total_cat * 100) if total_cat else 0
        chip_class = "chip-soft" if cat == "Soft Skills" else "chip-tool" if "Cloud" in cat or "DevOps" in cat else "chip-found"

        with st.expander(f"{cat}   ·   {len(found)}/{total_cat}  ({pct}%)", expanded=pct < 50):
            st.progress(pct / 100)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**✅ Found**")
                st.markdown(chips_html(found, chip_class), unsafe_allow_html=True)
            with c2:
                st.markdown("**❌ Missing**")
                st.markdown(chips_html(missing, "chip-miss"), unsafe_allow_html=True)


# ─── Tab 3: JD Match ──────────────────────────────────────────────────────────
with tab3:
    if not jd_text.strip():
        st.info("💡 Paste a job description in the **sidebar** to see how your resume compares.", icon="ℹ️")
    else:
        c1, c2 = st.columns([1, 1.8])
        with c1:
            st.plotly_chart(gauge_chart(jd_score, "JD Match"), use_container_width=True)

        with c2:
            st.markdown('<div class="section-title">Keywords Matched</div>', unsafe_allow_html=True)
            st.markdown(chips_html(sorted(jd_matched)[:40], "chip-found"), unsafe_allow_html=True)

        st.markdown('<div class="section-title">Missing JD Keywords — Add These to Your Resume</div>', unsafe_allow_html=True)
        st.markdown(chips_html(jd_missing, "chip-miss"), unsafe_allow_html=True)


# ─── Tab 4: Raw Text ──────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title">Extracted Resume Text</div>', unsafe_allow_html=True)
    word_count = len(resume_text.split())
    st.markdown(f"<span style='color:#64748b;font-size:.85rem'>{word_count} words extracted</span>", unsafe_allow_html=True)
    st.text_area("", resume_text, height=400, label_visibility="collapsed")


# ── Download report ───────────────────────────────────────────────────────────
st.markdown("---")
report_md = generate_report(resume_text, results, overall_score, jd_score)
st.download_button(
    label="⬇️  Download Full Report (.md)",
    data=report_md,
    file_name="resume_analysis_report.md",
    mime="text/markdown",
)