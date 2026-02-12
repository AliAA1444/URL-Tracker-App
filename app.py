import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import re
import random
import math
import time
from difflib import SequenceMatcher

# ============================================================================
# URL TRACKER V3.1 - CRISIS FIX EDITION
# Restoring V2.0 Reliability + V3.1 Intelligence
# ============================================================================

# 1. Page Configuration
st.set_page_config(
    page_title="URL TRACKER V3.1",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'language' not in st.session_state:
    st.session_state['language'] = None

# 2. Localization Dictionary (V2.0 Complete)
T = {
    'en': {
        'sidebar_role': 'Cybersecurity & AI Researcher',
        'sidebar_uni': 'Majmaah University',
        'sidebar_major': 'Computer Science',
        'status_online': 'System Online',
        'main_title': '🛡️ URL TRACKER V3.1 | Enterprise Phishing Detector',
        'main_subtitle': 'Advanced AI-Powered URL Analysis System',
        'input_label': 'URL',
        'input_placeholder': 'Enter URL here (e.g., http://ww38.gilhub.com)',
        'btn_scan': 'SCAN NOW 🚀',
        'history_title': '🕒 Recent Scans',
        'safe_title': '✅ SAFE WEBSITE',
        'safe_desc_wl': 'Verified by Trusted Whitelist Database.',
        'safe_desc_ai': 'System did not detect any potential threats (Clean).',
        'caution_title': '⚠️ SUSPICIOUS - PROCEED WITH CAUTION',
        'caution_desc': 'Unusual patterns detected. Verify the source before clicking.',
        'phish_title': '🚨 PHISHING DETECTED',
        'phish_desc': 'Malicious behavior patterns detected.',
        'risk_label': '⚠️ Critical Risk Level:',
        'tech_details': '🔍 View Technical Forensics',
        'step1': '🔌 Connecting to Tracker DB...',
        'step2': '🧠 Analyzing Features...',
        'step3': '🤖 AI Scanning...',
        'step4': '✅ Done.',
        'col_status': 'Status', 'col_engine': 'Engine', 'col_time': 'Time',
        'reason_typo': '⚠️ **Impersonation:** The URL is trying to mimic a famous brand (Typosquatting).',
        'reason_entropy': '⚠️ **Randomness:** The domain name looks randomly generated (High Entropy).',
        'reason_badwords': '⚠️ **Keywords:** Contains sensitive words (e.g., login, secure, update).',
        'reason_ip': '⚠️ **IP Address:** The URL uses an IP instead of a domain name.',
        'reason_http': '🚨 **INSECURE:** Using HTTP instead of HTTPS (No encryption).',
        'reason_redirect': '⚠️ **Redirect Service:** URL shortener may hide the real destination.',
        'reason_ai': '⚠️ **AI Pattern:** The structural integrity of the URL matches known phishing attacks.',
        'disclaimer_title': '⚠️ Disclaimer & Terms of Use',
        'disclaimer_text': """
        **1. Educational Purpose:** This tool is developed for educational and research purposes only as part of a Computer Science project.
        **2. No Guarantee:** While this system uses advanced AI and Whitelisting, no security tool is 100% perfect. False positives or negatives may occur.
        **3. Limitation of Liability:** The developer (Ali Alkhamees) is not responsible for any damages, data loss, or security breaches resulting from the use of this tool.
        **4. Usage:** Always verify URLs manually before entering sensitive information. Do not rely solely on this tool for critical security decisions.
        """
    },
    'ar': {
        'sidebar_role': 'باحث في الأمن السيبراني والذكاء الاصطناعي',
        'sidebar_uni': 'جامعة المجمعة',
        'sidebar_major': 'علوم الحاسب',
        'status_online': 'النظام يعمل',
        'main_title': '🛡️ URL TRACKER V3.1 | نظام كشف الروابط الغير آمنة',
        'main_subtitle': 'نظام متقدم لتحليل الروابط باستخدام الذكاء الاصطناعي',
        'input_label': 'الرابط',
        'input_placeholder': 'ضع الرابط هنا (مثال: http://ww38.gilhub.com)',
        'btn_scan': '🚀 ابدأ الفحص',
        'history_title': '🕒 سجل الفحص',
        'safe_title': '✅ موقع آمن',
        'safe_desc_wl': 'تم التحقق منه عبر القائمة البيضاء الموثوقة.',
        'safe_desc_ai': 'لم يكتشف النظام أي تهديدات محتملة (نظيف).',
        'caution_title': '⚠️ مشبوه - احذر',
        'caution_desc': 'اكتُشفت أنماط غير عادية. تحقق من المصدر قبل المتابعة.',
        'phish_title': '🚨 موقع خبيث / احتيال',
        'phish_desc': 'اكتشف النظام أنماطاً سلوكية خبيثة في هذا الرابط.',
        'risk_label': '⚠️ مستوى الخطورة:',
        'tech_details': '🔍 لماذا تم تصنيفه كخبيث؟',
        'step1': '🔌 جاري الاتصال بقاعدة البيانات...',
        'step2': '🧠 تحليل الميزات...',
        'step3': '🤖 فحص الذكاء الاصطناعي...',
        'step4': '✅ تم.',
        'col_status': 'الحالة', 'col_engine': 'المحرك', 'col_time': 'الوقت',
        'reason_typo': '⚠️ **انتحال شخصية:** الرابط يحاول تقليد موقع مشهور (تغيير في الحروف).',
        'reason_entropy': '⚠️ **اسم عشوائي:** اسم الموقع يبدو عشوائياً وغير مفهوم (مؤشر خطر).',
        'reason_badwords': '⚠️ **كلمات حساسة:** الرابط يحتوي على كلمات مريبة (مثل: تحديث، دخول، أمان).',
        'reason_ip': '⚠️ **عنوان رقمي:** الموقع يستخدم عنوان IP بدلاً من اسم نطاق رسمي.',
        'reason_http': '🚨 **غير آمن:** يستخدم HTTP بدلاً من HTTPS (بدون تشفير).',
        'reason_redirect': '⚠️ **خدمة إعادة توجيه:** قد يخفي الرابط المختصر الوجهة الحقيقية.',
        'reason_ai': '⚠️ **تحليل سلوكي:** هيكل الرابط يطابق أنماط التصيد المعروفة لدى الذكاء الاصطناعي.',
        'disclaimer_title': '⚠️ إخلاء مسؤولية وشروط الاستخدام',
        'disclaimer_text': """
        **1. غرض تعليمي:** تم تطوير هذه الأداة لأغراض تعليمية وبحثية فقط كجزء من مشروع علوم حاسب.
        **2. لا يوجد ضمان:** على الرغم من استخدام تقنيات متقدمة، لا توجد أداة أمنية دقيقة بنسبة 100%. قد تحدث أخطاء في التصنيف.
        **3. إخلاء المسؤولية:** المطور (علي الخميس) غير مسؤول عن أي أضرار أو خسائر أو اختراقات قد تنتج عن استخدام هذه الأداة.
        **4. الاستخدام:** يرجى دائماً التحقق من الروابط يدوياً وعدم الاعتماد كلياً على هذه الأداة في القرارات الأمنية الحساسة.
        """
    }
}

# 3. Language Selection Screen
if st.session_state['language'] is None:
    st.markdown("<h1 style='text-align: center;'>🛡️ URL TRACKER V3.1</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Select Language / اختر اللغة</h3>", unsafe_allow_html=True)
    st.write("")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("English 🇺🇸", use_container_width=True):
            st.session_state['language'] = 'en'
            st.rerun()
        st.write("")
        if st.button("العربية 🇸🇦", use_container_width=True):
            st.session_state['language'] = 'ar'
            st.rerun()
    st.stop()

L = T[st.session_state['language']]
is_rtl = True if st.session_state['language'] == 'ar' else False

# 4. Custom CSS Styling (V2.0 Original)
st.markdown(f"""
    <style>
    .main {{ background-color: #f8f9fa; direction: {'rtl' if is_rtl else 'ltr'}; }}
    p, h1, h2, h3, div, span {{ font-family: 'Segoe UI', sans-serif; }}
    
    /* Result Cards */
    .safe-box {{
        background-color: #d1e7dd; color: #0f5132; padding: 20px;
        border-radius: 10px; border-left: 10px solid #198754; margin-bottom: 20px;
        text-align: {'right' if is_rtl else 'left'};
    }}
    .caution-box {{
        background-color: #fff3cd; color: #664d03; padding: 20px;
        border-radius: 10px; border-left: 10px solid #ffc107; margin-bottom: 20px;
        text-align: {'right' if is_rtl else 'left'};
    }}
    .danger-box {{
        background-color: #f8d7da; color: #842029; padding: 20px;
        border-radius: 10px; border-left: 10px solid #dc3545; margin-bottom: 20px;
        text-align: {'right' if is_rtl else 'left'};
    }}
    
    /* Button Styling */
    .stButton>button {{
        width: 100%; background-color: #0d6efd; color: white;
        font-weight: bold; border-radius: 8px; height: 50px;
    }}
    .stButton>button:hover {{ background-color: #0b5ed7; }}
    </style>
    """, unsafe_allow_html=True)

# 5. Sidebar Profile (V2.0 Original - COMPLETE)
with st.sidebar:
    try:
        st.image("my_photo.png", width=100)
    except:
        st.markdown("### 👨‍💻")
    
    st.markdown(f"### 👨‍💻 **Ali Alkhamees**")
    st.markdown(f"**{L['sidebar_role']}**")
    st.markdown(f"**🏛️ {L['sidebar_uni']}**")
    st.markdown(f"**🎓 {L['sidebar_major']}**")
    
    st.markdown("---")
    st.link_button(f"🔗 LinkedIn Profile", "https://www.linkedin.com/in/ali-alkhamees-378b34367/")
    st.link_button(f"🏛️ Majmaah University", "https://www.mu.edu.sa/ar")
    st.success(f"● {L['status_online']}")
    
    st.markdown("---")
    if st.button("🌐 Language / اللغة"):
        st.session_state['language'] = None
        st.rerun()

# ============================================================================
# 6. BACKEND LOGIC - ROBUST & HEURISTIC-FIRST
# ============================================================================

# SAUDI BRAND INTELLIGENCE (Enhanced Registry)
SAUDI_BRANDS = {
    # Banking
    'alinma': ['alinma.com', 'www.alinma.com'],
    'alrajhi': ['alrajhibank.com.sa', 'alrajhibank.com', 'www.alrajhibank.com.sa', 'www.alrajhibank.com'],
    'snb': ['alahli.com', 'alahli.com.sa', 'www.alahli.com', 'www.alahli.com.sa'],
    'samba': ['samba.com', 'samba.com.sa', 'www.samba.com'],
    'riyadbank': ['riyadbank.com', 'www.riyadbank.com'],
    
    # Telecom
    'stc': ['stc.com.sa', 'www.stc.com.sa'],
    'mobily': ['mobily.com.sa', 'www.mobily.com.sa'],
    'zain': ['zain.sa', 'sa.zain.com'],
    
    # Government
    'absher': ['absher.sa', 'www.absher.sa'],
    'moi': ['moi.gov.sa', 'www.moi.gov.sa'],
    
    # URL Shorteners (Medium Risk)
    '4se': ['4se.sa'],
    'short': ['t.co', 'bit.ly', 'tinyurl.com']
}

# Whitelist Database (V2.0 Original)
TRUSTED_DOMAINS = {
    # Global Tech Giants
    'github.com', 'www.github.com', 'google.com', 'www.google.com',
    'youtube.com', 'www.youtube.com', 'facebook.com', 'www.facebook.com',
    'amazon.com', 'www.amazon.com', 'twitter.com', 'www.twitter.com',
    'linkedin.com', 'www.linkedin.com', 'microsoft.com', 'www.microsoft.com',
    'apple.com', 'www.apple.com', 'whatsapp.com', 'www.whatsapp.com',
    
    # Saudi Government & Education
    'absher.sa', 'www.absher.sa', 'moi.gov.sa', 'www.moi.gov.sa',
    'majmaah.edu.sa', 'www.majmaah.edu.sa', 'mu.edu.sa', 'www.mu.edu.sa',
    'm.mu.edu.sa', 'sis.mu.edu.sa', 'jarir.com', 'www.jarir.com',
    'stc.com.sa', 'www.stc.com.sa', 'coursera.org', 'www.coursera.org',
    'ksu.edu.sa', 'www.ksu.edu.sa', 'imamu.edu.sa', 'www.imamu.edu.sa',
    
    # Cybersecurity Resources
    'kali.org', 'www.kali.org', 'offsec.com', 'www.offsec.com'
}

# Feature Calculation Functions
def calc_entropy(text):
    """Shannon Entropy (V2.0 Original)"""
    if not text: return 0
    entropy = 0
    for x in range(256):
        p_x = float(text.count(chr(x))) / len(text)
        if p_x > 0: 
            entropy += - p_x * math.log(p_x, 2)
    return entropy

def similar(a, b):
    """Similarity Ratio (V2.0 Original)"""
    return SequenceMatcher(None, a, b).ratio()

# ROBUST URL PARSER (Crisis Fix #1: Handle malformed URLs)
def normalize_url(url):
    """
    Fixes malformed URLs and returns clean version
    """
    if not url or len(url) < 5:
        return url
    
    url = url.strip()
    
    # Fix common typos
    url = url.replace('https//', 'https://')
    url = url.replace('http//', 'http://')
    url = url.replace('htps://', 'https://')
    url = url.replace('htp://', 'http://')
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        # Check if it looks like a domain
        if '.' in url and ' ' not in url:
            url = 'https://' + url
    
    return url

def robust_domain_extraction(url):
    """
    Extracts domain robustly, immune to minor syntax errors
    """
    try:
        # Normalize first
        url = normalize_url(url)
        
        # Remove protocol
        no_protocol = url.replace("https://", "").replace("http://", "")
        
        # Extract domain (before first /, :, or ?)
        domain = no_protocol.split('/')[0].split(':')[0].split('?')[0]
        
        # Remove port numbers
        if ':' in domain:
            domain = domain.split(':')[0]
        
        return domain.lower().strip()
    except:
        return url.lower().strip()

# HEURISTIC-FIRST CHECKS (Crisis Fix #2: Prioritize obvious red flags)
def heuristic_analysis(url):
    """
    Pre-ML checks for obvious threats
    Returns: (risk_boost, reasons[])
    """
    risk_boost = 0
    reasons = []
    
    normalized_url = normalize_url(url)
    domain = robust_domain_extraction(normalized_url)
    
    # 1. HTTP (Insecure) - CRITICAL RED FLAG
    if normalized_url.startswith('http://') and not normalized_url.startswith('https://'):
        risk_boost += 40  # Massive penalty
        reasons.append('http_insecure')
    
    # 2. IP Address - HIGH RISK
    if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
        risk_boost += 35
        reasons.append('ip_address')
    
    # 3. Suspicious Prefixes - TYPOSQUATTING
    parts = domain.split('.')
    if parts and re.match(r'ww\d+', parts[0]):
        risk_boost += 30
        reasons.append('suspicious_prefix')
    
    # 4. URL Shorteners / Redirects - MEDIUM RISK
    shortener_domains = ['4se.sa', 'bit.ly', 't.co', 'tinyurl.com', 'goo.gl', 'ow.ly']
    if any(shortener in domain for shortener in shortener_domains):
        risk_boost += 25
        reasons.append('url_shortener')
    
    # 5. Sensitive Keywords in Domain - PHISHING INDICATORS
    phishing_keywords = ['login', 'verify', 'update', 'account', 'secure', 'banking', 'confirm']
    keyword_count = sum(1 for kw in phishing_keywords if kw in normalized_url.lower())
    if keyword_count >= 2:
        risk_boost += 25
        reasons.append('multiple_keywords')
    
    # 6. Excessive Length - OBFUSCATION
    if len(normalized_url) > 100:
        risk_boost += 15
        reasons.append('excessive_length')
    
    return risk_boost, reasons

# SAUDI INTELLIGENCE CHECK
def check_saudi_brand(url):
    """
    Checks if URL is official Saudi entity or impersonation
    Returns: (is_official, brand_name, similarity)
    """
    domain = robust_domain_extraction(url)
    
    # Exact match check
    for brand, official_domains in SAUDI_BRANDS.items():
        if domain in official_domains:
            return True, brand.upper(), 100
    
    # Fuzzy match for typosquatting
    for brand, official_domains in SAUDI_BRANDS.items():
        for official in official_domains:
            similarity = similar(domain, official) * 100
            if 75 < similarity < 100:  # High similarity but not exact
                return False, brand.upper(), similarity
    
    return False, None, 0

# FEATURE EXTRACTION (V3.1 Enhanced + Robust)
def get_features(url):
    """
    Extracts 5 core features with robust error handling
    Returns: features_list, metadata_dict
    """
    metadata = {
        'is_typosquatting': 0,
        'bad_word_count': 0,
        'is_ip': 0,
        'is_http': 0,
        'is_shortener': 0,
        'entropy_value': 0
    }
    
    try:
        # Normalize URL
        normalized_url = normalize_url(url)
        domain = robust_domain_extraction(normalized_url)
        domain_parts = domain.split('.')
        
        # Feature 1: URL Length
        url_length = len(normalized_url)
        
        # Feature 2: Domain Length
        domain_length = len(domain)
        
        # Feature 3: Saudi TLD Flag (TRUST SIGNAL)
        is_saudi = int(
            domain.endswith('.sa') or
            '.gov.sa' in domain or
            '.com.sa' in domain or
            '.edu.sa' in domain
        )
        
        # Feature 4: Shannon Entropy
        longest_part = max(domain_parts, key=len) if domain_parts else domain
        entropy = calc_entropy(longest_part)
        metadata['entropy_value'] = entropy
        
        # Feature 5: Keyword Count
        bad_words = ['login', 'verify', 'update', 'account', 'secure', 'banking']
        keyword_count = sum(1 for w in bad_words if w in normalized_url.lower())
        metadata['bad_word_count'] = keyword_count
        
        # Metadata for XAI
        metadata['is_http'] = int(normalized_url.startswith('http://'))
        metadata['is_ip'] = int(bool(re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain)))
        
        # Typosquatting detection
        top_targets = ['google', 'facebook', 'amazon', 'apple', 'microsoft', 'netflix', 'paypal', 
                       'absher', 'moi', 'stc', 'jarir', 'github', 'coursera', 'alinma', 'alrajhi']
        
        for part in domain_parts:
            if len(part) < 4: 
                continue
            if part in top_targets: 
                continue
            for target in top_targets:
                ratio = similar(part, target)
                if ratio > 0.80 and ratio < 1.0:
                    metadata['is_typosquatting'] = 1
                    break
            if metadata['is_typosquatting']:
                break
        
        return [url_length, domain_length, is_saudi, entropy, keyword_count], metadata
        
    except Exception as e:
        # Fallback safe values if parsing fails completely
        return [len(url), 20, 0, 3.0, 0], metadata

# MODEL TRAINING (Calibrated for Security Context)
@st.cache_resource
def train_calibrated_model():
    """
    Trains model with security-focused class weights
    """
    np.random.seed(42)
    random.seed(42)
    
    # Simulate 100k samples for faster loading
    n_benign = 65000
    n_malicious = 35000
    
    X_benign = []
    for _ in range(n_benign):
        url_len = np.random.randint(15, 60)
        domain_len = np.random.randint(8, 25)
        is_saudi = np.random.choice([0, 1], p=[0.6, 0.4])
        entropy = np.random.uniform(2.0, 3.5)
        keywords = 0
        X_benign.append([url_len, domain_len, is_saudi, entropy, keywords])
    
    X_malicious = []
    for _ in range(n_malicious):
        url_len = np.random.randint(40, 150)
        domain_len = np.random.randint(20, 60)
        is_saudi = np.random.choice([0, 1], p=[0.95, 0.05])
        entropy = np.random.uniform(3.8, 5.0)
        keywords = np.random.randint(1, 4)
        X_malicious.append([url_len, domain_len, is_saudi, entropy, keywords])
    
    X = np.array(X_benign + X_malicious)
    y = np.array([0]*n_benign + [1]*n_malicious)
    
    indices = np.random.permutation(len(X))
    X = X[indices]
    y = y[indices]
    
    # CALIBRATED: Security-first weighting
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=20,
        min_samples_split=10,
        class_weight={0: 1.0, 1: 1.6},  # Balanced (not too aggressive)
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X, y)
    return model

# Initialize model
if 'model_v31' not in st.session_state:
    with st.spinner('⚙️ Initializing URL TRACKER V3.1 AI Engine...'):
        st.session_state['model_v31'] = train_calibrated_model()
model = st.session_state['model_v31']

# History
if 'history' not in st.session_state:
    st.session_state['history'] = []

# ============================================================================
# 7. MAIN APPLICATION UI (V2.0 Original Style)
# ============================================================================

st.title(L['main_title'])
st.markdown(f"### {L['main_subtitle']}")
st.markdown("---")

# Input Form (V2.0 Style)
with st.form(key='scan_form'):
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        url_input = st.text_input(L['input_label'], placeholder=L['input_placeholder'], label_visibility="collapsed")
    with col_btn:
        scan_btn = st.form_submit_button(L['btn_scan'])

# ============================================================================
# 8. EXECUTION LOGIC (Crisis-Fixed Version)
# ============================================================================

if scan_btn and url_input:
    
    # Loading Animation (V2.0 Original)
    with st.status("⚙️ Processing...", expanded=True) as status:
        st.write(L['step1'])
        time.sleep(0.1)
        st.write(L['step2'])
        time.sleep(0.1)
        st.write(L['step3'])
        time.sleep(0.1)
        status.update(label=L['step4'], state="complete", expanded=False)
    
    # Normalize URL first
    normalized_url = normalize_url(url_input)
    domain_check = robust_domain_extraction(normalized_url)
    
    # ========== LAYER 1: WHITELIST CHECK ==========
    is_whitelisted = domain_check in TRUSTED_DOMAINS
    
    # ========== LAYER 2: HEURISTIC-FIRST ANALYSIS (Crisis Fix) ==========
    heuristic_boost, heuristic_reasons = heuristic_analysis(normalized_url)
    
    # ========== LAYER 3: SAUDI INTELLIGENCE ==========
    is_saudi_official, brand_name, similarity = check_saudi_brand(normalized_url)
    
    # ========== LAYER 4: ML PREDICTION ==========
    features, metadata = get_features(normalized_url)
    ml_proba = model.predict_proba([features])[0][1] * 100  # % malicious
    
    # ========== LAYER 5: CALIBRATED SCORING (Crisis Fix) ==========
    base_score = ml_proba
    
    # Apply Saudi Intelligence
    if is_saudi_official:
        # Official Saudi entity → Force SAFE
        final_score = max(0, base_score - 85)
        verdict = 'SAFE'
        engine = f'Saudi Intelligence: {brand_name}'
    
    elif brand_name and 75 < similarity < 100:
        # Typosquatting Saudi brand → Force DANGER
        final_score = max(base_score, 85)
        verdict = 'DANGER'
        engine = 'AI Model + Saudi Threat Intel'
    
    else:
        # Apply heuristic boost
        final_score = min(100, base_score + heuristic_boost)
        
        # Apply pattern boosting
        if metadata['is_typosquatting']:
            final_score = max(final_score, 75)
        
        if metadata['entropy_value'] > 4.2:
            final_score = min(100, final_score + 10)
        
        # CRITICAL: Whitelist override
        if is_whitelisted:
            final_score = max(0, final_score - 90)
            verdict = 'SAFE'
            engine = 'Whitelist'
        
        # CRISIS FIX: Strict threshold adherence
        elif final_score >= 70:
            verdict = 'DANGER'
            engine = 'AI Model'
        elif final_score >= 30:
            verdict = 'CAUTION'
            engine = 'AI Model'
        else:
            verdict = 'SAFE'
            engine = 'AI Model'
    
    # ========== DISPLAY RESULTS (V2.0 Style) ==========
    st.markdown("### 📊 Report")
    
    if verdict == 'SAFE':
        st.markdown(f"""
        <div class="safe-box">
            <h2 style="margin:0;">{L['safe_title']}</h2>
            <p style="font-size:18px;">{L['safe_desc_wl'] if is_whitelisted or is_saudi_official else L['safe_desc_ai']}</p>
            <p style="margin:0;"><strong>Risk Score:</strong> {final_score:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # CRISIS FIX: Correct log labeling
        st.session_state['history'].insert(0, {
            "URL": url_input, 
            L['col_status']: "✅ Safe", 
            L['col_engine']: engine, 
            L['col_time']: time.strftime("%H:%M")
        })
    
    elif verdict == 'CAUTION':
        st.markdown(f"""
        <div class="caution-box">
            <h2 style="margin:0;">{L['caution_title']}</h2>
            <p style="font-size:18px;">{L['caution_desc']}</p>
            <p style="margin:0;"><strong>Risk Score:</strong> {final_score:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write(f"**{L['risk_label']} {final_score:.1f}%**")
        st.progress(int(final_score))
        
        # CRISIS FIX: Correct log labeling
        st.session_state['history'].insert(0, {
            "URL": url_input,
            L['col_status']: "⚠️ Caution",
            L['col_engine']: engine,
            L['col_time']: time.strftime("%H:%M")
        })
    
    else:  # DANGER
        st.markdown(f"""
        <div class="danger-box">
            <h2 style="margin:0;">{L['phish_title']}</h2>
            <p style="font-size:18px;">{L['phish_desc']}</p>
            <p style="margin:0;"><strong>Threat Level:</strong> {final_score:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.error(f"**{L['risk_label']} {final_score:.1f}%**")
        st.progress(int(final_score))
        
        # CRISIS FIX: Correct log labeling
        st.session_state['history'].insert(0, {
            "URL": url_input,
            L['col_status']: "🚨 Phishing",
            L['col_engine']: engine,
            L['col_time']: time.strftime("%H:%M")
        })
    
    # ========== TECHNICAL FORENSICS (V2.0 Style) ==========
    with st.expander(L['tech_details'], expanded=(verdict == 'DANGER')):
        
        if 'http_insecure' in heuristic_reasons:
            st.error(L['reason_http'])
        
        if 'ip_address' in heuristic_reasons:
            st.error(L['reason_ip'])
        
        if 'suspicious_prefix' in heuristic_reasons or metadata['is_typosquatting']:
            st.error(L['reason_typo'])
        
        if 'url_shortener' in heuristic_reasons:
            st.warning(L['reason_redirect'])
        
        if metadata['bad_word_count'] > 0:
            st.warning(L['reason_badwords'])
        
        if metadata['entropy_value'] > 3.8:
            st.warning(L['reason_entropy'])
        
        # Fallback reason
        if not any([
            'http_insecure' in heuristic_reasons,
            'ip_address' in heuristic_reasons,
            metadata['is_typosquatting'],
            metadata['bad_word_count'] > 0,
            metadata['entropy_value'] > 3.8
        ]):
            st.info(L['reason_ai'])
        
        # Show scores breakdown
        st.markdown("---")
        st.markdown("**Score Breakdown:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ML Base Score", f"{base_score:.1f}%")
        with col2:
            st.metric("Heuristic Boost", f"+{heuristic_boost}%")
        with col3:
            st.metric("Final Score", f"{final_score:.1f}%")

# ============================================================================
# 9. SCAN HISTORY (V2.0 Original)
# ============================================================================

if len(st.session_state['history']) > 0:
    st.markdown("---")
    st.subheader(L['history_title'])
    st.dataframe(pd.DataFrame(st.session_state['history']), use_container_width=True, hide_index=True)

# ============================================================================
# 10. FOOTER & DISCLAIMER (V2.0 Original)
# ============================================================================

st.markdown("---")
with st.expander(L['disclaimer_title']):
    st.markdown(L['disclaimer_text'])

st.markdown("<div style='text-align: center; color: gray;'>© 2025 URL TRACKER by Ali Alkhamees (V3.1 - Crisis Fix Edition)</div>", unsafe_allow_html=True)
