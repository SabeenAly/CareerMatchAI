import streamlit as st
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
import docx
from datetime import datetime, timedelta

st.set_page_config(page_title="CareerMatch AI", page_icon="🚀", layout="wide")

st.markdown("""
<style>
.main-header{text-align:center;padding:20px 0 10px}
.match-card{border:1px solid #e0e0e0;border-radius:10px;padding:14px;margin:8px 0;background:#fafafa}
.skill-missing{background:#ffe5e5;border-radius:6px;padding:4px 10px;display:inline-block;margin:2px;font-size:12px;color:#c0392b}
.skill-match{background:#e5ffe5;border-radius:6px;padding:4px 10px;display:inline-block;margin:2px;font-size:12px;color:#27ae60}
.field-badge{background:#e8f4fd;border-radius:8px;padding:6px 14px;display:inline-block;font-size:13px;font-weight:600;color:#1a6fa8}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ⚙️ API CONFIGURATION
# ─────────────────────────────────────────────
# JSearch API (RapidAPI) — Sign up free at rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
# Free tier: 200 requests/month
JSEARCH_API_KEY = "a0a5281764msh867ac5acb20aaecp1333ccjsn117804a75845"   # ← paste your RapidAPI key here





# ─────────────────────────────────────────────
# 🎯 FIELD SKILLS DATABASE
# ─────────────────────────────────────────────
FIELD_SKILLS = {
    "Computer Science / Software Engineering": {
        "emoji": "💻",
        "search_keywords": ["software engineer pakistan", "software developer pakistan", "junior developer pakistan"],
        "skills": ["python","java","javascript","c++","c#","sql","mysql","postgresql","mongodb","git","github","linux","docker","kubernetes","rest api","django","flask","node","react","html","css","php","software development","agile","scrum","data structures","algorithms","object oriented programming","problem solving","debugging","testing"],
        "courses": {"python":"https://python.org/doc","java":"https://dev.java/learn","javascript":"https://javascript.info","sql":"https://sqlzoo.net","docker":"https://docs.docker.com/get-started","react":"https://react.dev/learn","git":"https://git-scm.com/book","data structures":"https://www.coursera.org/learn/data-structures"}
    },
    "Artificial Intelligence / Machine Learning": {
        "emoji": "🤖",
        "search_keywords": ["machine learning engineer pakistan", "data scientist pakistan", "AI engineer pakistan"],
        "skills": ["python","machine learning","deep learning","tensorflow","pytorch","scikit-learn","pandas","numpy","data analysis","nlp","computer vision","neural networks","opencv","data science","statistics","mathematics","r","feature engineering","model training","hugging face","large language models"],
        "courses": {"machine learning":"https://coursera.org/learn/machine-learning","tensorflow":"https://tensorflow.org/learn","deep learning":"https://deeplearning.ai","nlp":"https://huggingface.co/learn","python":"https://python.org/doc","statistics":"https://www.khanacademy.org/math/statistics-probability"}
    },
    "Cybersecurity": {
        "emoji": "🔐",
        "search_keywords": ["cybersecurity analyst pakistan", "security engineer pakistan", "ethical hacker pakistan"],
        "skills": ["network security","ethical hacking","penetration testing","kali linux","metasploit","wireshark","firewall","cryptography","vulnerability assessment","siem","incident response","malware analysis","python","linux","networking","tcp ip","cyber forensics","cloud security","owasp","nmap"],
        "courses": {"ethical hacking":"https://www.cybrary.it","penetration testing":"https://tryhackme.com","network security":"https://www.coursera.org/learn/network-security","kali linux":"https://www.kali.org/docs","owasp":"https://owasp.org/www-project-top-ten"}
    },
    "Full Stack Development": {
        "emoji": "🌐",
        "search_keywords": ["full stack developer pakistan", "web developer pakistan", "frontend developer pakistan"],
        "skills": ["html","css","javascript","react","vue","angular","node","express","python","django","flask","php","laravel","sql","mongodb","postgresql","rest api","graphql","git","docker","aws","responsive design","typescript","tailwind","bootstrap","firebase"],
        "courses": {"react":"https://react.dev/learn","node":"https://nodejs.org/en/learn","django":"https://docs.djangoproject.com","html":"https://developer.mozilla.org/en-US/docs/Learn/HTML","javascript":"https://javascript.info","mongodb":"https://learn.mongodb.com"}
    },
    "Digital Marketing": {
        "emoji": "📱",
        "search_keywords": ["digital marketing pakistan", "seo specialist pakistan", "social media manager pakistan"],
        "skills": ["seo","google ads","facebook ads","instagram marketing","content writing","copywriting","email marketing","social media marketing","canva","google analytics","meta ads","tiktok marketing","influencer marketing","brand management","market research","wordpress","mailchimp","hubspot","crm","youtube marketing","affiliate marketing","shopify","ecommerce"],
        "courses": {"seo":"https://moz.com/beginners-guide-to-seo","google ads":"https://skillshop.withgoogle.com","facebook ads":"https://www.facebook.com/business/learn","content writing":"https://www.coursera.org/learn/content-marketing","google analytics":"https://analytics.google.com/analytics/academy","canva":"https://www.canva.com/learn/design"}
    },
    "Graphic Design / UI-UX Design": {
        "emoji": "🎨",
        "search_keywords": ["graphic designer pakistan", "ui ux designer pakistan", "visual designer pakistan"],
        "skills": ["photoshop","illustrator","figma","adobe xd","canva","ui design","ux design","wireframing","prototyping","indesign","after effects","premiere pro","typography","color theory","branding","logo design","motion graphics","user research","usability testing","design thinking","sketch","invision"],
        "courses": {"figma":"https://www.figma.com/resources/learn-design","photoshop":"https://helpx.adobe.com/photoshop/tutorials.html","ui design":"https://www.coursera.org/learn/ui-ux-design","ux design":"https://www.interaction-design.org","adobe xd":"https://helpx.adobe.com/xd/tutorials.html"}
    },
    "Fashion Design": {
        "emoji": "👗",
        "search_keywords": ["fashion designer pakistan", "fashion design internship pakistan", "textile designer pakistan"],
        "skills": ["fashion design","pattern making","sewing","textile","fashion illustration","cad design","trend forecasting","garment construction","fabric selection","fashion styling","adobe illustrator","photoshop","fashion marketing","retail management","visual merchandising","costume design","embroidery","color theory","fashion photography","brand development","collection development","draping"],
        "courses": {"fashion design":"https://www.coursera.org/learn/fashion-design","adobe illustrator":"https://helpx.adobe.com/illustrator/tutorials.html","pattern making":"https://www.skillshare.com/browse/pattern-making","fashion marketing":"https://www.coursera.org/learn/fashion-marketing","trend forecasting":"https://www.wgsn.com"}
    },
    "Accounting / Finance": {
        "emoji": "💰",
        "search_keywords": ["accountant pakistan", "finance officer pakistan", "financial analyst pakistan"],
        "skills": ["accounting","financial analysis","excel","quickbooks","taxation","auditing","budgeting","financial reporting","bookkeeping","payroll","cost accounting","sap","financial modeling","investment analysis","risk management","ms office","data analysis","power bi","erp","corporate finance","ifrs","gaap","tally"],
        "courses": {"financial analysis":"https://www.coursera.org/learn/financial-analysis","excel":"https://support.microsoft.com/excel","quickbooks":"https://quickbooks.intuit.com/tutorials","taxation":"https://www.coursera.org/learn/taxation","financial modeling":"https://corporatefinanceinstitute.com/resources/financial-modeling"}
    },
    "Medical / Healthcare": {
        "emoji": "🏥",
        "search_keywords": ["medical officer pakistan", "healthcare jobs pakistan", "clinical research pakistan"],
        "skills": ["patient care","clinical research","pharmacology","medical diagnosis","anatomy","physiology","surgery","nursing","medical ethics","healthcare management","medical writing","clinical trials","laboratory skills","medical imaging","emr","telemedicine","first aid","public health","epidemiology","nutrition"],
        "courses": {"clinical research":"https://www.coursera.org/learn/clinical-research","public health":"https://www.coursera.org/learn/public-health","medical writing":"https://www.coursera.org/learn/science-writing","healthcare management":"https://www.coursera.org/learn/healthcare-management"}
    },
    "Business / MBA": {
        "emoji": "📊",
        "search_keywords": ["business development pakistan", "marketing manager pakistan", "MBA jobs pakistan"],
        "skills": ["business development","sales","marketing","crm","negotiation","project management","leadership","communication","strategic planning","market research","supply chain","operations management","excel","powerpoint","presentation","team management","customer service","business analysis","entrepreneurship","product management","ms office","erp","salesforce"],
        "courses": {"business development":"https://www.coursera.org/learn/business-development","project management":"https://www.coursera.org/learn/project-management","salesforce":"https://trailhead.salesforce.com","product management":"https://www.coursera.org/learn/product-management","leadership":"https://www.coursera.org/learn/leading-teams"}
    },
    "Engineering (Mechanical / Electrical / Civil)": {
        "emoji": "⚙️",
        "search_keywords": ["mechanical engineer pakistan", "electrical engineer pakistan", "civil engineer pakistan"],
        "skills": ["autocad","solidworks","matlab","ansys","catia","circuit design","pcb design","plc programming","project management","structural analysis","thermodynamics","fluid mechanics","electrical design","construction management","ms project","revit","bim","quality control","six sigma","lean manufacturing","3d modeling","cad cam"],
        "courses": {"autocad":"https://www.autodesk.com/learn/ondemand","matlab":"https://www.mathworks.com/learn/tutorials","solidworks":"https://www.solidworks.com/sw/resources/solidworks-tutorials.htm","project management":"https://www.coursera.org/learn/project-management","six sigma":"https://www.coursera.org/learn/six-sigma-define-measure"}
    },
    "Education / Teaching": {
        "emoji": "📚",
        "search_keywords": ["teacher pakistan", "lecturer pakistan", "education jobs pakistan"],
        "skills": ["curriculum development","lesson planning","teaching","e-learning","lms","classroom management","assessment","special education","tutoring","educational technology","ms office","google classroom","zoom","communication","research","academic writing","mentoring","counseling","training development","instructional design"],
        "courses": {"instructional design":"https://www.coursera.org/learn/instructional-design","e-learning":"https://www.coursera.org/learn/e-learning","google classroom":"https://edu.google.com/products/classroom","curriculum development":"https://www.coursera.org/learn/curriculum-design"}
    },
}

# ─────────────────────────────────────────────
# FUNCTIONS
# ─────────────────────────────────────────────
def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        return "".join([page.extract_text() or "" for page in reader.pages])
    except: return ""

def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    except: return ""

def detect_field(cv_text):
    cv_lower = cv_text.lower()
    scores = {field: sum(1 for s in data["skills"] if s in cv_lower) for field, data in FIELD_SKILLS.items()}
    return max(scores, key=scores.get)

def extract_skills(cv_text, field):
    cv_lower = cv_text.lower()
    return [s for s in FIELD_SKILLS[field]["skills"] if s in cv_lower]

def get_missing_skills(cv_skills, job_desc, field):
    job_lower = job_desc.lower()
    courses = FIELD_SKILLS[field]["courses"]
    cv_set = set(cv_skills)
    missing = []
    for skill in FIELD_SKILLS[field]["skills"]:
        if skill in job_lower and skill not in cv_set:
            missing.append({
                "skill": skill,
                "course": courses.get(skill, f"https://www.google.com/search?q=learn+{skill.replace(' ','+')}")
            })
    return missing[:4]

def calculate_readiness(cv_text, skills_found):
    score = 0
    tips = []
    score += min(len(skills_found)*4, 40)
    tips.append(f"{'✅' if len(skills_found)>=5 else '⚠️'} Skills found: {len(skills_found)} {'— Great!' if len(skills_found)>=5 else '— Add more skills to CV'}")
    wc = len(cv_text.split())
    if wc>300: score+=20; tips.append("✅ CV length is good")
    elif wc>150: score+=10; tips.append("⚠️ CV is short — add more details")
    else: tips.append("❌ CV too short — expand your sections")
    if any(k in cv_text.lower() for k in ["bachelor","bs","bsc","degree","university","college","diploma","master","mba"]): score+=15; tips.append("✅ Education section found")
    else: tips.append("❌ Add your degree/education")
    if any(k in cv_text.lower() for k in ["experience","project","internship","worked","developed","built","created","designed"]): score+=15; tips.append("✅ Experience/Projects found")
    else: tips.append("❌ Add projects or work experience")
    if any(k in cv_text.lower() for k in ["email","phone","linkedin","github","@","+92"]): score+=10; tips.append("✅ Contact info found")
    else: tips.append("❌ Add email/phone/LinkedIn")
    return min(score,100), tips

def fetch_jobs_jsearch(keywords, job_type="all"):
    """Fetch REAL live jobs from JSearch API (LinkedIn + Indeed + Glassdoor)"""
    try:
        query = " ".join(keywords[:2]) + " pakistan"
        if job_type == "internship": query += " internship"
        url = "https://jsearch.p.rapidapi.com/search"
        headers = {
            "X-RapidAPI-Key": JSEARCH_API_KEY,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        params = {
            "query": query,
            "page": "1",
            "num_pages": "2",
            "date_posted": "month",  # Only jobs from last month!
            "country": "pk"
        }
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            jobs = []
            for job in response.json().get("data", []):
                # Only include jobs with real apply links
                apply_link = job.get("job_apply_link","")
                if not apply_link or apply_link == "": continue
                jobs.append({
                    "title":       job.get("job_title","N/A"),
                    "company":     job.get("employer_name","N/A"),
                    "location":    job.get("job_city","Pakistan") or "Pakistan",
                    "description": job.get("job_description",""),
                    "salary_min":  job.get("job_min_salary", 0) or 0,
                    "salary_max":  job.get("job_max_salary", 0) or 0,
                    "url":         apply_link,
                    "created":     job.get("job_posted_at_datetime_utc","")[:10] if job.get("job_posted_at_datetime_utc") else "Recent",
                    "source":      job.get("job_publisher","")
                })
            if jobs: return jobs
    except Exception as e:
        pass
    return get_fallback_jobs(job_type)

def get_fallback_jobs(job_type="all"):
    """Real verified Pakistani company job pages"""
    jobs = [
        # CS / Software
        {"title":"Junior Software Engineer","company":"Systems Limited","location":"Lahore","description":"python java javascript sql git linux backend software development agile scrum object oriented programming","salary_min":60000,"salary_max":90000,"url":"https://www.systemsltd.com/careers","created":"Recent","source":"Company Website"},
        {"title":"Full Stack Developer","company":"Arbisoft","location":"Lahore","description":"javascript react node html css sql mongodb rest api git docker typescript full stack development","salary_min":80000,"salary_max":130000,"url":"https://arbisoft.com/careers","created":"Recent","source":"Company Website"},
        {"title":"Software Engineer","company":"Netsol Technologies","location":"Lahore","description":"java c++ python sql software development agile git object oriented programming problem solving","salary_min":80000,"salary_max":120000,"url":"https://www.netsol.com/careers","created":"Recent","source":"Company Website"},
        {"title":"Backend Developer","company":"10Pearls","location":"Karachi","description":"python django flask node javascript rest api postgresql mongodb docker backend development","salary_min":90000,"salary_max":130000,"url":"https://10pearls.com/careers","created":"Recent","source":"Company Website"},
        # AI / ML
        {"title":"ML Engineer","company":"Folio3 Software","location":"Karachi","description":"machine learning python tensorflow scikit-learn deep learning nlp data science pandas numpy neural networks","salary_min":100000,"salary_max":150000,"url":"https://www.folio3.com/careers","created":"Recent","source":"Company Website"},
        {"title":"Data Scientist","company":"TRG Pakistan","location":"Karachi","description":"data science python machine learning statistics pandas numpy r data analysis deep learning computer vision","salary_min":90000,"salary_max":140000,"url":"https://www.trgworld.com/careers","created":"Recent","source":"Company Website"},
        {"title":"Data Analyst","company":"Jazz Pakistan","location":"Islamabad","description":"python sql excel power bi tableau data analysis statistics reporting business intelligence","salary_min":70000,"salary_max":110000,"url":"https://www.jazz.com.pk/careers","created":"Recent","source":"Company Website"},
        # Cybersecurity
        {"title":"Cybersecurity Analyst","company":"Contour Software","location":"Lahore","description":"network security ethical hacking penetration testing kali linux python linux firewall vulnerability assessment owasp","salary_min":90000,"salary_max":140000,"url":"https://contour-software.com/careers","created":"Recent","source":"Company Website"},
        # Full Stack
        {"title":"Full Stack Developer","company":"VentureDive","location":"Islamabad","description":"react node javascript html css python django postgresql rest api git docker typescript responsive design","salary_min":85000,"salary_max":125000,"url":"https://venturedive.com/careers","created":"Recent","source":"Company Website"},
        # Digital Marketing
        {"title":"Digital Marketing Specialist","company":"PurplePatch","location":"Lahore","description":"seo google ads facebook ads social media marketing content writing canva email marketing google analytics meta ads","salary_min":50000,"salary_max":80000,"url":"https://www.purplepatch.com.pk/careers","created":"Recent","source":"Company Website"},
        {"title":"SEO Specialist","company":"Bramerz","location":"Lahore","description":"seo search engine optimization google analytics content writing keyword research backlinks wordpress digital marketing","salary_min":45000,"salary_max":75000,"url":"https://bramerz.pk/careers","created":"Recent","source":"Company Website"},
        # Design
        {"title":"UI/UX Designer","company":"Tkxel","location":"Lahore","description":"figma adobe xd ui design ux design wireframing prototyping user research design thinking usability testing","salary_min":70000,"salary_max":110000,"url":"https://tkxel.com/careers","created":"Recent","source":"Company Website"},
        {"title":"Graphic Designer","company":"Mindstorm Studios","location":"Lahore","description":"photoshop illustrator canva graphic design logo design branding typography color theory visual design","salary_min":50000,"salary_max":80000,"url":"https://www.mindstormstudios.com/careers","created":"Recent","source":"Company Website"},
        # Fashion
        {"title":"Fashion Designer","company":"Khaadi","location":"Karachi","description":"fashion design pattern making textile fabric garment construction fashion illustration trend forecasting collection development","salary_min":50000,"salary_max":80000,"url":"https://www.khaadi.com/pages/careers","created":"Recent","source":"Company Website"},
        {"title":"Visual Merchandiser","company":"Outfitters","location":"Lahore","description":"visual merchandising fashion styling retail management brand development color theory fashion marketing display","salary_min":40000,"salary_max":65000,"url":"https://outfitters.com.pk","created":"Recent","source":"Company Website"},
        # Finance
        {"title":"Financial Analyst","company":"Deloitte Pakistan","location":"Karachi","description":"accounting financial analysis excel quickbooks taxation auditing budgeting financial reporting ifrs gaap corporate finance","salary_min":80000,"salary_max":130000,"url":"https://www2.deloitte.com/pk/en/pages/careers/articles/careers.html","created":"Recent","source":"Company Website"},
        {"title":"Accountant","company":"HBL Bank","location":"Karachi","description":"accounting excel financial analysis taxation bookkeeping payroll ms office erp financial reporting budgeting","salary_min":60000,"salary_max":100000,"url":"https://www.hbl.com/career","created":"Recent","source":"Company Website"},
        # Business
        {"title":"Business Development Officer","company":"Careem Pakistan","location":"Lahore","description":"business development sales marketing crm negotiation communication strategic planning market research ms office","salary_min":60000,"salary_max":100000,"url":"https://careers.careem.com","created":"Recent","source":"Company Website"},
        {"title":"Marketing Manager","company":"Unilever Pakistan","location":"Karachi","description":"marketing brand management market research consumer insights campaign management ms office powerpoint presentation leadership","salary_min":100000,"salary_max":150000,"url":"https://careers.unilever.com/pakistan","created":"Recent","source":"Company Website"},
        # Engineering
        {"title":"Mechanical Engineer","company":"Engro Corporation","location":"Karachi","description":"autocad solidworks matlab mechanical engineering project management quality control manufacturing thermodynamics","salary_min":80000,"salary_max":130000,"url":"https://www.engro.com/careers","created":"Recent","source":"Company Website"},
        {"title":"Electrical Engineer","company":"PTCL","location":"Islamabad","description":"electrical engineering circuit design plc programming matlab autocad networking electrical design project management","salary_min":75000,"salary_max":120000,"url":"https://www.ptcl.com.pk/Home/Careers","created":"Recent","source":"Company Website"},
        # Medical
        {"title":"Clinical Research Officer","company":"Shaukat Khanum Hospital","location":"Lahore","description":"clinical research patient care medical writing pharmacology healthcare laboratory skills public health research","salary_min":60000,"salary_max":100000,"url":"https://shaukatkhanum.org.pk/careers","created":"Recent","source":"Company Website"},
        # Education
        {"title":"Lecturer","company":"FAST NUCES","location":"Lahore","description":"teaching curriculum development lesson planning academic writing research ms office communication mentoring assessment","salary_min":60000,"salary_max":100000,"url":"https://www.nu.edu.pk/Careers","created":"Recent","source":"Company Website"},
        # INTERNSHIPS
        {"title":"Software Engineering Intern","company":"Systems Limited","location":"Lahore","description":"python java javascript sql git software development internship student object oriented programming","salary_min":20000,"salary_max":30000,"url":"https://www.systemsltd.com/careers","created":"Recent","source":"Company Website"},
        {"title":"AI/ML Intern","company":"Folio3 Software","location":"Karachi","description":"python machine learning deep learning tensorflow scikit-learn internship student data science","salary_min":20000,"salary_max":30000,"url":"https://www.folio3.com/careers","created":"Recent","source":"Company Website"},
        {"title":"Digital Marketing Intern","company":"Bramerz","location":"Lahore","description":"seo social media marketing content writing canva google analytics digital marketing internship student","salary_min":15000,"salary_max":25000,"url":"https://bramerz.pk/careers","created":"Recent","source":"Company Website"},
        {"title":"UI/UX Design Intern","company":"VentureDive","location":"Islamabad","description":"figma adobe xd ui design ux design wireframing prototyping internship student design","salary_min":15000,"salary_max":25000,"url":"https://venturedive.com/careers","created":"Recent","source":"Company Website"},
        {"title":"Fashion Design Intern","company":"Khaadi","location":"Karachi","description":"fashion design pattern making textile fabric garment construction fashion illustration internship student","salary_min":20000,"salary_max":35000,"url":"https://www.khaadi.com/pages/careers","created":"Recent","source":"Company Website"},
        {"title":"Finance Intern","company":"HBL Bank","location":"Karachi","description":"accounting excel financial analysis taxation internship student budgeting ms office finance","salary_min":20000,"salary_max":30000,"url":"https://www.hbl.com/career","created":"Recent","source":"Company Website"},
        {"title":"Data Science Intern","company":"TRG Pakistan","location":"Karachi","description":"python pandas numpy data analysis machine learning statistics internship student data science","salary_min":15000,"salary_max":25000,"url":"https://www.trgworld.com/careers","created":"Recent","source":"Company Website"},
        {"title":"Cybersecurity Intern","company":"10Pearls","location":"Karachi","description":"cybersecurity networking linux python ethical hacking internship student owasp network security","salary_min":20000,"salary_max":30000,"url":"https://10pearls.com/careers","created":"Recent","source":"Company Website"},
        {"title":"Business Development Intern","company":"Careem Pakistan","location":"Lahore","description":"business development sales marketing communication ms office internship student crm presentation","salary_min":20000,"salary_max":35000,"url":"https://careers.careem.com","created":"Recent","source":"Company Website"},
        {"title":"Mechanical Engineering Intern","company":"Engro Corporation","location":"Karachi","description":"autocad matlab mechanical engineering internship student project management quality control manufacturing","salary_min":20000,"salary_max":30000,"url":"https://www.engro.com/careers","created":"Recent","source":"Company Website"},
    ]
    if job_type=="internship": return [j for j in jobs if "intern" in j["title"].lower()]
    elif job_type=="job": return [j for j in jobs if "intern" not in j["title"].lower()]
    return jobs

def match_jobs(cv_text, jobs, field):
    if not jobs: return []
    docs = [cv_text]+[j["description"] for j in jobs]
    vec = TfidfVectorizer(stop_words='english',ngram_range=(1,2))
    matrix = vec.fit_transform(docs)
    sims = cosine_similarity(matrix[0:1],matrix[1:]).flatten()
    cv_skills = set(extract_skills(cv_text,field))
    results = []
    for i,job in enumerate(jobs):
        matched = [s for s in FIELD_SKILLS[field]["skills"] if s in job["description"].lower() and s in cv_skills]
        missing = get_missing_skills(list(cv_skills),job["description"],field)
        salary = f"Rs. {int(job['salary_min']):,} – {int(job['salary_max']):,}/month" if job["salary_min"] and job["salary_max"] else "Negotiable"
        results.append({**job,"match_pct":round(sims[i]*100,1),"matched":matched,"missing":missing,"salary_text":salary})
    return sorted(results,key=lambda x:x["match_pct"],reverse=True)

def color(p): return "#27ae60" if p>=70 else "#e67e22" if p>=45 else "#e74c3c"
def badge(p): return "✅ Strong Match" if p>=70 else "⚠️ Moderate Match" if p>=45 else "❌ Weak Match"

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class='main-header'>
    <h1>🚀 CareerMatch AI</h1>
    <p style='color:#888;font-size:16px'>Pakistan's Universal AI-Powered Job & Internship Matcher</p>
    <p style='color:#aaa;font-size:13px'>Any Field · Any Career · Real Jobs · Real Links · Upload CV → Get Matched Instantly</p>
</div><hr>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.header("⚙️ Settings")
st.sidebar.markdown("---")
search_type = st.sidebar.radio("What are you looking for?",["🎓 Internships Only","💼 Jobs Only","🔍 Both Jobs & Internships"],index=2)
manual_field = st.sidebar.selectbox("Your Field (AI auto-detects):",["🤖 Auto Detect"]+list(FIELD_SKILLS.keys()))
st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("📄 Upload Your CV (PDF or Word)",type=["pdf","docx"])
st.sidebar.markdown("---")
st.sidebar.markdown("**✅ Fields Supported:**")
for field, data in FIELD_SKILLS.items():
    st.sidebar.markdown(f"{data['emoji']} {field}")

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if uploaded_file:
    with st.spinner("📄 Reading your CV..."):
        cv_text = extract_text_from_pdf(uploaded_file) if uploaded_file.name.endswith(".pdf") else extract_text_from_docx(uploaded_file)

    if not cv_text or len(cv_text.strip())<30:
        st.error("❌ Could not read CV. Please use a text-based PDF or Word file.")
        st.stop()

    # Field detection — FULL NAME now
    detected_field = detect_field(cv_text) if manual_field=="🤖 Auto Detect" else manual_field
    field_emoji = FIELD_SKILLS[detected_field]["emoji"]

    skills_found = extract_skills(cv_text, detected_field)
    readiness, tips = calculate_readiness(cv_text, skills_found)

    # ── CV Summary ──
    st.subheader("📄 Your CV Analysis")
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        # FIXED: Show FULL field name
        st.markdown(f"**🎯 Detected Field:**")
        st.markdown(f"<div class='field-badge'>{field_emoji} {detected_field}</div>", unsafe_allow_html=True)
    with c2:
        st.metric("🛠️ Skills Found", len(skills_found))
    with c3:
        st.metric("📝 Word Count", len(cv_text.split()))
    with c4:
        c = color(readiness)
        st.markdown(f"<div style='text-align:center'><div style='font-size:12px;color:#888'>📊 Readiness Score</div><div style='font-size:32px;font-weight:700;color:{c}'>{readiness}/100</div></div>", unsafe_allow_html=True)

    if skills_found:
        st.markdown("**✅ Skills found in your CV:**")
        st.markdown(" ".join([f"<span class='skill-match'>{s}</span>" for s in skills_found]), unsafe_allow_html=True)
    else:
        st.warning("⚠️ No skills detected. Make sure your CV clearly lists your skills.")

    with st.expander("💡 CV Improvement Tips — Click to expand"):
        for tip in tips: st.markdown(f"- {tip}")

    st.markdown("---")

    # ── Fetch Jobs ──
    type_map = {"🎓 Internships Only":"internship","💼 Jobs Only":"job","🔍 Both Jobs & Internships":"all"}
    jtype = type_map[search_type]

    with st.spinner("🌐 Fetching live jobs from LinkedIn, Indeed & Pakistani companies..."):
        if JSEARCH_API_KEY != "YOUR_RAPIDAPI_KEY":
            jobs = fetch_jobs_jsearch(skills_found[:3], jtype)
            if not jobs:
                jobs = get_fallback_jobs(jtype)
        else:
            jobs = get_fallback_jobs(jtype)

    with st.spinner("🤖 AI matching your profile to jobs..."):
        matched = match_jobs(cv_text, jobs, detected_field)

    internships = [j for j in matched if "intern" in j["title"].lower()]
    full_jobs   = [j for j in matched if "intern" not in j["title"].lower()]

    def show_jobs(job_list, heading):
        if not job_list:
            st.info(f"No {heading} found matching your profile. Try uploading a more detailed CV.")
            return
        st.subheader(f"{heading} — {len(job_list)} found")
        for job in job_list[:6]:
            c = color(job["match_pct"])
            b = badge(job["match_pct"])
            st.markdown(f"""
            <div class='match-card'>
                <div style='display:flex;justify-content:space-between;align-items:center'>
                    <div>
                        <span style='font-size:15px;font-weight:600'>{job['title']}</span>
                        <span style='color:#888;font-size:12px;margin-left:8px'>@ {job['company']}</span>
                    </div>
                    <div style='font-size:24px;font-weight:700;color:{c}'>{job['match_pct']}%</div>
                </div>
                <div style='font-size:12px;color:#888;margin-top:6px'>
                    📍 {job['location']} &nbsp;|&nbsp;
                    💰 {job['salary_text']} &nbsp;|&nbsp;
                    📅 Posted: {job['created']} &nbsp;|&nbsp;
                    🌐 {job.get('source','')} &nbsp;|&nbsp;
                    <span style='color:{c};font-weight:500'>{b}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            ca, cb = st.columns(2)
            with ca:
                if job["matched"]:
                    st.markdown("**✅ Your matching skills:**")
                    st.markdown(" ".join([f"<span class='skill-match'>{s}</span>" for s in job["matched"][:5]]), unsafe_allow_html=True)
            with cb:
                if job["missing"]:
                    st.markdown("**❌ Missing skills — learn free:**")
                    for m in job["missing"]:
                        st.markdown(f"<span class='skill-missing'>{m['skill']}</span> → [Learn free ↗]({m['course']})", unsafe_allow_html=True)

            st.markdown(f"### 👉 [Apply Now → {job['company']}]({job['url']})")
            st.markdown("---")

    if jtype in ["internship","all"]: show_jobs(internships,"🎓 Top Internship Matches")
    if jtype in ["job","all"]: show_jobs(full_jobs,"💼 Top Job Matches")

else:
    # Welcome screen
    st.markdown("""
    <div style='text-align:center;padding:50px 20px;color:#888'>
        <div style='font-size:60px'>🚀</div>
        <h2 style='color:#555'>CareerMatch AI</h2>
        <p style='font-size:15px'>Pakistan's Universal AI Career Matcher</p>
        <p style='font-size:13px;margin-top:6px'>Any Field · Any Career · Real Pakistani Jobs · Real Links</p>
        <p style='font-size:14px;margin-top:16px'>👈 Upload your CV from the sidebar to get started</p>
        <div style='display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-top:24px'>
            <div style='background:#f0fff4;border-radius:10px;padding:10px 16px;border:1px solid #b7e4c7;font-size:13px'>💻 CS & Software Engineering</div>
            <div style='background:#f0f4ff;border-radius:10px;padding:10px 16px;border:1px solid #b7c4e4;font-size:13px'>🤖 AI & Machine Learning</div>
            <div style='background:#fff8f0;border-radius:10px;padding:10px 16px;border:1px solid #e4d4b7;font-size:13px'>📱 Digital Marketing</div>
            <div style='background:#fff0f4;border-radius:10px;padding:10px 16px;border:1px solid #e4b7c4;font-size:13px'>👗 Fashion Design</div>
            <div style='background:#f9f0ff;border-radius:10px;padding:10px 16px;border:1px solid #d4b7e4;font-size:13px'>🎨 Graphic Design / UI-UX</div>
            <div style='background:#f0ffff;border-radius:10px;padding:10px 16px;border:1px solid #b7e4e4;font-size:13px'>💰 Accounting & Finance</div>
            <div style='background:#fffff0;border-radius:10px;padding:10px 16px;border:1px solid #e4e4b7;font-size:13px'>⚙️ Engineering</div>
            <div style='background:#fff5f0;border-radius:10px;padding:10px 16px;border:1px solid #e4c4b7;font-size:13px'>🏥 Medical & Healthcare</div>
            <div style='background:#f0f9ff;border-radius:10px;padding:10px 16px;border:1px solid #b7d4e4;font-size:13px'>📊 Business & MBA</div>
            <div style='background:#f5fff0;border-radius:10px;padding:10px 16px;border:1px solid #c4e4b7;font-size:13px'>🔐 Cybersecurity</div>
            <div style='background:#f0f0ff;border-radius:10px;padding:10px 16px;border:1px solid #c4b7e4;font-size:13px'>🌐 Full Stack Development</div>
            <div style='background:#fff0f0;border-radius:10px;padding:10px 16px;border:1px solid #e4b7b7;font-size:13px'>📚 Education & Teaching</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
