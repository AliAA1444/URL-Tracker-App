import streamlit as st
import pandas as pd
import numpy as np
import joblib
import tldextract
from urllib.parse import urlparse
import math
import time

# 1. إعدادات الصفحة (نفس V2.0)
st.set_page_config(
    page_title="URL TRACKER V3.0",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تهيئة متغير اللغة
if 'language' not in st.session_state:
    st.session_state['language'] = None

# 2. قاموس الترجمة الكامل (استعادة نصوصك السابقة + إضافات V3.0)
T = {
    'en': {
        'sidebar_role': 'Cybersecurity & AI Researcher',
        'sidebar_uni': 'Majmaah University',
        'sidebar_major': 'Computer Science',
        'status_online': 'System Online',
        'main_title': '🛡️ URL TRACKER V3.0 | AI Phishing Detector',
        'main_subtitle': 'Professional Analysis Powered by 651k Real Samples',
        'input_label': 'URL',
        'input_placeholder': 'Enter URL (e.g., https://stc.com.sa)',
        'btn_scan': 'SCAN NOW 🚀',
        'history_title': '🕒 Recent Scans',
        'safe_title': '✅ SAFE WEBSITE',
        'caution_title': '⚠️ CAUTION ZONE',
        'phish_title': '🚨 PHISHING DETECTED',
        'safe_desc': 'System did not detect any potential threats.',
        'caution_desc': 'Mixed signals detected. Proceed with caution.',
        'phish_desc': 'Malicious behavior patterns detected.',
        'risk_label': '⚠️ Risk Level:',
        'tech_details': '🔍 Technical Analysis',
        'step1': '🔌 Loading AI Model...',
        'step2': '🧠 Analyzing Patterns...',
        'step3': '🤖 AI Probability Check...',
        'step4': '✅ Done.',
        'col_status': 'Status', 'col_engine': 'Engine', 'col_time': 'Time',
    },
    'ar': {
        'sidebar_role': 'باحث في الأمن السيبراني والذكاء الاصطناعي',
        'sidebar_uni': 'جامعة المجمعة',
        'sidebar_major': 'علوم الحاسب',
        'status_online': 'النظام يعمل',
        'main_title': '🛡️ URL TRACKER V3.0 | نظام كشف الاحتيال',
        'main_subtitle': 'نظام احترافي مدرب على 651 ألف رابط حقيقي',
        'input_label': 'الرابط',
        'input_placeholder': 'ضع الرابط هنا (مثال: https://stc.com.sa)',
        'btn_scan': '🚀 ابدأ الفحص',
        'history_title': '🕒 سجل الفحص',
        'safe_title': '✅ موقع آمن',
        'caution_title': '⚠️ منطقة شك',
        'phish_title': '🚨 موقع خبيث / احتيال',
        'safe_desc': 'لم يكتشف النظام أي تهديدات محتملة.',
        'caution_desc': 'اكتشف النظام إشارات مختلطة. يرجى التحقق من المصدر.',
        'phish_desc': 'اكتشف النظام أنماطاً سلوكية خبيثة في هذا الرابط.',
        'risk_label': '⚠️ مستوى الخطورة:',
        'tech_details': '🔍 التحليل التقني',
        'step1': '🔌 تحميل موديل الذكاء الاصطناعي...',
        'step2': '🧠 تحليل الميزات الهيكلية...',
        'step3': '🤖 فحص الاحتمالات...',
        'step4': '✅ تم التحليل.',
        'col_status': 'الحالة', 'col_engine': 'المحرك', 'col_time': 'الوقت',
    }
}

# 3. شاشة اختيار اللغة
if st.session_state['language'] is None:
    st.markdown("<h1 style='text-align: center;'>🛡️ URL TRACKER</h1>", unsafe_allow_html=True)
    st.write("")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("English 🇺🇸", use_container_width=True):
            st.session_state['language'] = 'en'
            st.rerun()
        if st.button("العربية 🇸🇦", use_container_width=True):
            st.session_state['language'] = 'ar'
            st.rerun()
    st.stop()

L = T[st.session_state['language']]
is_rtl = True if st.session_state['language'] == 'ar' else False

# 4. تخصيص المظهر (استعادة CSS الجميل)
st.markdown(f"""
    <style>
    .main {{ background-color: #f8f9fa; direction: {'rtl' if is_rtl else 'ltr'}; }}
    .safe-box {{
        background-color: #d1e7dd; color: #0f5132; padding: 20px;
        border-radius: 10px; border-left: 10px solid #198754; margin-bottom: 20px;
        text-align: {'right' if is_rtl else 'left'};
    }}
    .caution-box {{
        background-color: #fff3cd; color: #856404; padding: 20px;
        border-radius: 10px; border-left: 10px solid #ffc107; margin-bottom: 20px;
        text-align: {'right' if is_rtl else 'left'};
    }}
    .danger-box {{
        background-color: #f8d7da; color: #842029; padding: 20px;
        border-radius: 10px; border-left: 10px solid #dc3545; margin-bottom: 20px;
        text-align: {'right' if is_rtl else 'left'};
    }}
    </style>
    """, unsafe_allow_html=True)

# 5. القائمة الجانبية (استعادة ملفك الشخصي)
with st.sidebar:
    st.image("my_photo.png", width=100)
    st.markdown(f"### 👨‍💻 **Ali Alkhamees**")
    st.markdown(f"**{L['sidebar_role']}**\n**🏛️ {L['sidebar_uni']}**\n**🎓 {L['sidebar_major']}**")
    st.markdown("---")
    st.success(f"● {L['status_online']}")

# 6. البرمجة الخلفية (Backend)
@st.cache_resource
def load_v3_model():
    return joblib.load('url_tracker_v3_model.pkl')

model = load_v3_model()

def extract_features_v3(url):
    try:
        ext = tldextract.extract(str(url))
        domain = ext.domain.lower()
        suffix = ext.suffix.lower()
        subdomain = ext.subdomain.lower()
        
        # 1. وزن النطاق (TLD Weight) - ضروري جداً
        tld_weight = 1
        if suffix in ['gov.sa', 'edu.sa', 'mil.sa', 'gov', 'edu']: tld_weight = 5
        elif suffix in ['com.sa', 'sa', 'org.sa']: tld_weight = 3
        elif suffix in ['tk', 'ml', 'ga', 'cf', 'xyz', 'top']: tld_weight = 0
        
        # 2. طول الرابط
        url_len = len(str(url))
        
        # 3. هل هو رابط أساسي (Root)؟
        is_root = 1 if subdomain in ['', 'www'] else 0
        
        # 4. العشوائية (Entropy)
        def calc_entropy(text):
            if not text: return 0
            probs = [float(text.count(c)) / len(text) for c in set(text)]
            return -sum(p * math.log(p, 2) for p in probs)
        
        entropy = calc_entropy(domain)

        # هام جداً: الترتيب والعدد يجب أن يكون 4 ميزات كما تدرب الموديل
        return [url_len, tld_weight, is_root, entropy]
    except:
        return [0, 1, 1, 0]

# 7. واجهة التطبيق الرئيسية
st.title(L['main_title'])
st.markdown(f"### {L['main_subtitle']}")

with st.form(key='scan_form'):
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        url_input = st.text_input(L['input_label'], placeholder=L['input_placeholder'], label_visibility="collapsed")
    with col_btn:
        scan_btn = st.form_submit_button(L['btn_scan'])

if scan_btn and url_input:
    with st.status("⚙️ Analyzing...", expanded=False) as status:
        st.write(L['step1']); time.sleep(0.2)
        st.write(L['step2']); time.sleep(0.2)
        st.write(L['step3'])
        
        # استخراج الميزات (4 ميزات)
        features = extract_features_v3(url_input)
       # الفحص عبر الموديل
       st.write(f"Model expects: {model.n_features_in_} features")
st.write(f"You provided: {len(features)} features")
        prob = model.predict_proba([features])[0][1]
        status.update(label=L['step4'], state="complete")

    st.markdown("### 📊 Report")
    
    # نظام المناطق الثلاث (Thresholding)
    if prob < 0.35:
        st.markdown(f'<div class="safe-box"><h2>{L["safe_title"]}</h2><p>{L["safe_desc"]}</p><p>Confidence: {(1-prob)*100:.1f}%</p></div>', unsafe_allow_html=True)
    elif prob < 0.75:
        st.markdown(f'<div class="caution-box"><h2>{L["caution_title"]}</h2><p>{L["caution_desc"]}</p></div>', unsafe_allow_html=True)
        st.info(f"{L['risk_label']} {prob*100:.1f}%")
    else:
        st.markdown(f'<div class="danger-box"><h2>{L["phish_title"]}</h2><p>{L["phish_desc"]}</p><p>Threat Level: {prob*100:.1f}%</p></div>', unsafe_allow_html=True)

# سجل الفحص (اختياري)
if 'history' not in st.session_state: st.session_state['history'] = []

