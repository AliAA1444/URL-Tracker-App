import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import re
import random
import math
import time
from difflib import SequenceMatcher

# 1. Page Configuration | إعدادات الصفحة
st.set_page_config(
    page_title="URL TRACKER",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for language | تهيئة متغير اللغة
if 'language' not in st.session_state:
    st.session_state['language'] = None

# 2. Localization Dictionary | قاموس الترجمة
T = {
    'en': {
        'sidebar_role': 'Cybersecurity & AI Researcher',
        'sidebar_uni': 'Majmaah University',
        'sidebar_major': 'Computer Science',
        'status_online': 'System Online',
        'main_title': '🛡️ URL TRACKER | Enterprise Phishing Detector (Beta)',
        'main_subtitle': 'Advanced AI-Powered URL Analysis System',
        'input_label': 'URL',
        'input_placeholder': 'Enter URL here (e.g., http://ww38.gilhub.com)',
        'btn_scan': 'SCAN NOW 🚀',
        'history_title': '🕒 Recent Scans',
        'safe_title': '✅ SAFE WEBSITE',
        'safe_desc_wl': 'Verified by Trusted Whitelist Database.',
        'safe_desc_ai': 'System did not detect any potential threats (Clean).',
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
        'main_title': '🛡️ URL TRACKER | نظام كشف الروابط الغير آمنة (تجريبي)',
        'main_subtitle': 'نظام هجين لتحليل الروابط باستخدام الذكاء الاصطناعي',
        'input_label': 'الرابط',
        'input_placeholder': 'ضع الرابط هنا (مثال: http://ww38.gilhub.com)',
        'btn_scan': '🚀 ابدأ الفحص',
        'history_title': '🕒 سجل الفحص',
        'safe_title': '✅ موقع آمن',
        'safe_desc_wl': 'تم التحقق منه عبر القائمة البيضاء الموثوقة.',
        'safe_desc_ai': 'لم يكتشف النظام أي تهديدات محتملة (نظيف).',
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

# 3. Language Selection Screen | شاشة اختيار اللغة
if st.session_state['language'] is None:
    st.markdown("<h1 style='text-align: center;'>🛡️ URL TRACKER</h1>", unsafe_allow_html=True)
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

# 4. Custom CSS Styling | تخصيص المظهر
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

# 5. Sidebar Profile | القائمة الجانبية
with st.sidebar:
    st.image("my_photo.png", width=100)
    
    st.markdown(f"### 👨‍💻 **Ali Alkhamees**")
    st.markdown(f"**{L['sidebar_role']}**")
    st.markdown(f"**🏛️ {L['sidebar_uni']}**")
    st.markdown(f"**🎓 {L['sidebar_major']}**")
    
    #st.link_button(f"🔗 Majmaah University", "https://www.mu.edu.sa/ar")

    st.markdown("---")
    st.link_button(f"🔗 LinkedIn Profile", "https://www.linkedin.com/in/ali-alkhamees-378b34367/")
    st.link_button(f"🏛️ Majmaah University", "https://www.mu.edu.sa/ar")
    st.success(f"● {L['status_online']}")
    
    st.markdown("---")
    if st.button("🌐 Language / اللغة"):
        st.session_state['language'] = None
        st.rerun()

# 6. Backend Logic & Algorithms..  ..الخوارزميات والمنطق

#Whitelist Database: Manual insertion for trusted domains to prevent False Positives.
# قاعدة بيانات القائمة البيضاء: لضمان عدم حظر المواقع الرسمية
TRUSTED_DOMAINS = {
    #Global Tech Giants
    'github.com', 'www.github.com', 'google.com', 'www.google.com',
    'youtube.com', 'www.youtube.com', 'facebook.com', 'www.facebook.com',
    'amazon.com', 'www.amazon.com', 'twitter.com', 'www.twitter.com',
    'linkedin.com', 'www.linkedin.com', 'microsoft.com', 'www.microsoft.com',
    'apple.com', 'www.apple.com', 'whatsapp.com', 'www.whatsapp.com',
    
    #Saudi Government & Education
    'absher.sa', 'www.absher.sa', 'moi.gov.sa', 'www.moi.gov.sa',
    'majmaah.edu.sa', 'www.majmaah.edu.sa', 'mu.edu.sa', 'www.mu.edu.sa',
    'm.mu.edu.sa', 'sis.mu.edu.sa', 'jarir.com', 'www.jarir.com',
    'stc.com.sa', 'www.stc.com.sa', 'coursera.org', 'www.coursera.org',
    'ksu.edu.sa', 'www.ksu.edu.sa', 'imamu.edu.sa', 'www.imamu.edu.sa',
    
    #Cybersecurity Resources
    'kali.org', 'www.kali.org', 'offsec.com', 'www.offsec.com'
}

#Feature 1: Shannon Entropy (Measure of Randomness)
# تستخدم لكشف النطاقات المولدة عشوائياً
def calc_entropy(text):
    if not text: return 0
    entropy = 0
    for x in range(256):
        p_x = float(text.count(chr(x))) / len(text)
        if p_x > 0: entropy += - p_x * math.log(p_x, 2)
    return entropy

# Feature 2: Levenshtein Distance (Similarity Ratio)
# تستخدم لكشف التلاعب بالأسماء (Typosquatting)
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Feature Extraction Function | دالة استخراج الميزات
def get_features(url):
    my_list = []
    try:
        # URL Cleaning and Domain Parsing
        no_protocol = url.replace("https://", "").replace("http://", "")
        clean_domain = no_protocol.split('/')[0].split(':')[0].split('?')[0]
        domain_parts = clean_domain.split('.')
    except:
        clean_domain = url
        domain_parts = [url]

    # 1. Structural Features
    my_list.append(len(url))
    my_list.append(clean_domain.count('.'))
    my_list.append(1 if '@' in url else 0)
    
    # 2. Mathematical Entropy
    longest_part = max(domain_parts, key=len) if domain_parts else clean_domain
    my_list.append(calc_entropy(longest_part))
    
    # 3. Suspicious Patterns (IP, Hyphens)
    my_list.append(1 if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url) else 0)
    my_list.append(1 if '-' in clean_domain else 0)
    
    # 4. Sensitive Keywords Check
    bad_words = ['login', 'verify', 'update', 'account', 'secure', 'banking']
    found_bad = 0
    for w in bad_words:
        if w in url.lower(): found_bad += 1
    my_list.append(found_bad)

    # 5. Advanced Typosquatting Detection Logic
    # Checking against top targeted brands worldwide
    top_targets = ['google', 'facebook', 'amazon', 'apple', 'microsoft', 'netflix', 'paypal', 'absher', 'moi', 'stc', 'jarir', 'github', 'coursera']
    is_typosquatting = 0
    for part in domain_parts:
        if len(part) < 4: continue 
        if part in top_targets: continue
        for target in top_targets:
            ratio = similar(part, target)
            # Threshold: > 80% similarity implies impersonation
            if ratio > 0.80 and ratio < 1.0:
                is_typosquatting = 1
                break
        if is_typosquatting: break
    my_list.append(is_typosquatting)
    
    # 6. Subdomain Anomalies (e.g., ww38, web-login)
    is_sus_prefix = 0
    if re.match(r'ww\d+', domain_parts[0]) or domain_parts[0] in ['web', 'login', 'secure']:
         is_sus_prefix = 1
    my_list.append(is_sus_prefix)

    return my_list, is_typosquatting, found_bad, my_list[4]


#7.Model Training (Synthetic Data Generation)
@st.cache_resource
def train_model_logic():
    #Data Simulation: Creating a balanced dataset for training
    # توليد بيانات محاكاة متوازنة لتدريب النموذج
    safe_urls = []
    phishing_urls = []
    brands = ['google', 'amazon', 'github', 'jarir', 'absher']
    
    #Generating 2500 Safe URLs
    for i in range(2500):
        dom = random.choice(brands)
        safe_urls.append(f"https://www.{dom}.com")
        safe_urls.append(f"https://www.{dom}.com/product/{random.randint(1000,9999)}")
    
    #Generating 2500 Phishing URLs (Simulation of attacks)
    for i in range(2500):
        dom = random.choice(brands)
        #Simulate Typosquatting (e.g., g00gle)
        fake = list(dom)
        fake[random.randint(0, len(fake)-1)] = random.choice(['l', '1', 'e', 'a'])
        fake_dom = "".join(fake)
        #Simulate Subdomain attacks
        prefix = random.choice(['ww1', 'ww38', 'www1', 'web'])
        phishing_urls.append(f"http://{prefix}.{fake_dom}.com")
        phishing_urls.append(f"http://www.{fake_dom}.com")
        
    all_urls = safe_urls + phishing_urls
    all_labels = [0]*len(safe_urls) + [1]*len(phishing_urls)
    
    #Shuffling Data
    combined = list(zip(all_urls, all_labels))
    random.shuffle(combined)
    
    #Training Random Forest Model
    X = np.array([get_features(u)[0] for u, l in combined])
    y = np.array([l for u, l in combined])
    
    model = RandomForestClassifier(n_estimators=60)
    model.fit(X, y)
    return model

#Initialize Model on Startup
if 'model' not in st.session_state:
    with st.spinner('⚙️ Initializing URL TRACKER AI Engine...'):
        st.session_state['model'] = train_model_logic()
model = st.session_state['model']

#History Session State
if 'history' not in st.session_state:
    st.session_state['history'] = []

# 8. Main Application UI | واجهة التطبيق الرئيسية
st.title(L['main_title'])
st.markdown(f"### {L['main_subtitle']}")
st.markdown("---")

#Input Form
with st.form(key='scan_form'):
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        url_input = st.text_input(L['input_label'], placeholder=L['input_placeholder'], label_visibility="collapsed")
    with col_btn:
        scan_btn = st.form_submit_button(L['btn_scan'])

# 9. Execution Logic | منطق التشغيل
if scan_btn and url_input:
    
    #Loading Animation
    with st.status("⚙️ Processing...", expanded=True) as status:
        st.write(L['step1'])
        time.sleep(0.1)
        st.write(L['step2'])
        time.sleep(0.1)
        st.write(L['step3'])
        time.sleep(0.1)
        status.update(label=L['step4'], state="complete", expanded=False)
    
    #Domain Parsing for Whitelist Check
    domain_check = url_input
    try:
        domain_check = url_input.replace("https://", "").replace("http://", "").split('/')[0].split(':')[0].lower()
    except: pass
    
    #Step 1: Check Whitelist
    is_whitelisted = False
    for trusted in TRUSTED_DOMAINS:
        if domain_check == trusted or domain_check.endswith("." + trusted):
            is_whitelisted = True
            break
    
    st.markdown("### 📊 Report")
    
    #Display Results
    if is_whitelisted:
        #SAFE - WHITELIST
        st.markdown(f"""
        <div class="safe-box">
            <h2 style="margin:0;">{L['safe_title']}</h2>
            <p style="font-size:18px;">{L['safe_desc_wl']}</p>
        </div>
        """, unsafe_allow_html=True)
        st.session_state['history'].insert(0, {"URL": url_input, L['col_status']: "✅ Safe", L['col_engine']: "Whitelist", L['col_time']: time.strftime("%H:%M")})
        
    else:
        #Step 2: Check AI Model
        features, typo_detected, bad_words_count, is_ip = get_features(url_input)
        prediction = model.predict([features])[0]
        prob = model.predict_proba([features])[0][1]
        
        if prediction == 1:
            #DANGEROUS - AI DETECTED
            st.markdown(f"""
            <div class="danger-box">
                <h2 style="margin:0;">{L['phish_title']}</h2>
                <p style="font-size:18px;">{L['phish_desc']}</p>
                <p style="margin:0;"><strong>AI Confidence:</strong> {prob*100:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write(f"**{L['risk_label']} {prob*100:.1f}%**")
            st.progress(int(prob*100))
            
            #Display Technical Reasons
            with st.expander(L['tech_details'], expanded=True):
                if typo_detected:
                    st.error(L['reason_typo'])
                if bad_words_count > 0:
                    st.warning(L['reason_badwords'])
                if features[3] > 3.8: 
                    st.warning(L['reason_entropy'])
                if is_ip:
                    st.warning(L['reason_ip'])
                # Fallback Reason
                if not typo_detected and bad_words_count == 0 and features[3] <= 3.8:
                    st.info(L['reason_ai'])

            st.session_state['history'].insert(0, {"URL": url_input, L['col_status']: "🚨 Phishing", L['col_engine']: "AI Model", L['col_time']: time.strftime("%H:%M")})

        else:
            #SAFE - AI CLEARED
            st.markdown(f"""
            <div class="safe-box">
                <h2 style="margin:0;">{L['safe_title']}</h2>
                <p style="font-size:18px;">{L['safe_desc_ai']}</p>
            </div>
            """, unsafe_allow_html=True)
            st.session_state['history'].insert(0, {"URL": url_input, L['col_status']: "✅ Safe", L['col_engine']: "AI Model", L['col_time']: time.strftime("%H:%M")})

# 10. Scan History | سجل الفحص
if len(st.session_state['history']) > 0:
    st.markdown("---")
    st.subheader(L['history_title'])
    st.dataframe(pd.DataFrame(st.session_state['history']), use_container_width=True, hide_index=True)

# 11. Footer & Disclaimer | التذييل وإخلاء المسؤولية
st.markdown("---")
#Expander for Legal Disclaimer
with st.expander(L['disclaimer_title']):
    st.markdown(L['disclaimer_text'])

st.markdown("<div style='text-align: center; color: gray;'>© 2025 URL TRACKER by Ali Alkhamees (V2.0 - Beta)</div>", unsafe_allow_html=True)