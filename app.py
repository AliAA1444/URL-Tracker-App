import streamlit as st
import pandas as pd
import numpy as np
import joblib
import tldextract
import re
import math
import time
import plotly.graph_objects as go
from difflib import SequenceMatcher
from urllib.parse import urlparse

# 1. Page Configuration | إعدادات الصفحة الفاخرة (V2.0)
st.set_page_config(
    page_title="URL TRACKER V3.2",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تهيئة متغيرات الجلسة
if 'language' not in st.session_state: st.session_state['language'] = None
if 'history' not in st.session_state: st.session_state['history'] = []

# 2. Localization Dictionary | قاموس الترجمة الكامل (V2.0)
T = {
    'en': {
        'sidebar_role': 'Cybersecurity & AI Researcher',
        'sidebar_uni': 'Majmaah University',
        'sidebar_major': 'Computer Science',
        'status_online': 'V3.2 Enterprise Active',
        'main_title': '🛡️ URL TRACKER V3.2',
        'main_subtitle': 'Enterprise Phishing Intelligence (Saudi Calibrated)',
        'input_label': 'Analyze URL',
        'input_placeholder': 'Enter URL (e.g., https://www.alinma.com)',
        'btn_scan': 'DEEP SCAN 🚀',
        'history_title': '🕒 Recent Scans',
        'safe_title': '✅ SAFE & TRUSTED',
        'caution_title': '⚠️ CAUTION REQUIRED',
        'phish_title': '🚨 PHISHING DETECTED',
        'risk_label': 'Threat Level:',
        'tech_details': '🔍 Forensic Breakdown',
        'xai_title': '📊 Explainable AI (XAI)',
        'step1': '🔌 Accessing Intel DB...',
        'step2': '🧠 Feature Extraction...',
        'step3': '🤖 AI Analysis...',
        'step4': '✅ Analysis Complete.',
        'col_status': 'Status', 'col_engine': 'Risk %', 'col_time': 'Time'
    },
    'ar': {
        'sidebar_role': 'باحث في الأمن السيبراني والذكاء الاصطناعي',
        'sidebar_uni': 'جامعة المجمعة',
        'sidebar_major': 'علوم الحاسب',
        'status_online': 'النظام V3.2 نشط',
        'main_title': '🛡️ URL TRACKER V3.2',
        'main_subtitle': 'نظام استخبارات الروابط (معاير للسوق السعودي)',
        'input_label': 'حلل الرابط الآن',
        'input_placeholder': 'ضع الرابط هنا (مثال: https://www.alinma.com)',
        'btn_scan': 'فحص عميق 🚀',
        'history_title': '🕒 سجل الفحص',
        'safe_title': '✅ موقع آمن وموثوق',
        'caution_title': '⚠️ منطقة شك (انتباه)',
        'phish_title': '🚨 تم كشف محاولة تصيد',
        'risk_label': 'مستوى التهديد:',
        'tech_details': '🔍 التحليل الجنائي الرقمي',
        'xai_title': '📊 شرح قرار الذكاء الاصطناعي',
        'step1': '🔌 الاتصال بقاعدة البيانات...',
        'step2': '🧠 استخراج السمات...',
        'step3': '🤖 فحص الذكاء الاصطناعي...',
        'step4': '✅ تم الفحص.',
        'col_status': 'الحالة', 'col_engine': 'درجة الخطر', 'col_time': 'الوقت'
    }
}

# 3. Language Selection | شاشة اختيار اللغة (V2.0)
if st.session_state['language'] is None:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🛡️ URL TRACKER V3.2</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("English 🇺🇸", use_container_width=True):
            st.session_state['language'] = 'en'; st.rerun()
        st.write("")
        if st.button("العربية 🇸🇦", use_container_width=True):
            st.session_state['language'] = 'ar'; st.rerun()
    st.stop()

L = T[st.session_state['language']]
is_rtl = st.session_state['language'] == 'ar'

# 4. Custom CSS | التصميم المطور (SOC Style)
st.markdown(f"""
    <style>
    .main {{ background-color: #f8f9fa; direction: {'rtl' if is_rtl else 'ltr'}; }}
    .result-card {{ padding: 25px; border-radius: 15px; margin-bottom: 20px; border-left: 10px solid; }}
    .safe {{ background: #d1e7dd; color: #0f5132; border-color: #198754; }}
    .caution {{ background: #fff3cd; color: #856404; border-color: #ffc107; }}
    .danger {{ background: #f8d7da; color: #842029; border-color: #dc3545; }}
    .stButton>button {{ border-radius: 10px; height: 50px; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# 5. Model Loading & Reputation Engine
@st.cache_resource
def load_v3_engine():
    return joblib.load('url_tracker_v3_model.pkl')

model = load_v3_engine()

# بنك المعلومات السعودي للعلامات التجارية
SAUDI_INTEL = {
    "alinma": ["alinma.com", "www.alinma.com"],
    "stc": ["stc.com.sa", "stc.com"],
    "absher": ["absher.sa", "absher.gov.sa"],
    "alrajhi": ["alrajhibank.com.sa", "alrajhibank.com"]
}

def hybrid_calibration(url, raw_prob):
    ext = tldextract.extract(url)
    domain = ext.domain.lower()
    suffix = ext.suffix.lower()
    full_domain = f"{domain}.{suffix}"
    
    adjusted_score = raw_prob
    
    # 1. تصحيح بنك الإنماء والمواقع الرسمية (Fix False Positive)
    for brand, officials in SAUDI_INTEL.items():
        if full_domain in officials:
            return 0.05, f"Verified {brand.upper()} Official Domain"
            
    # 2. تصحيح Gilhub وانتحال الشخصية (Fix False Negative)
    # نقارن الموقع الحالي بـ Github المشهور
    if SequenceMatcher(None, domain, "github").ratio() > 0.8 and domain != "github":
        adjusted_score = max(adjusted_score, 0.85)
        return adjusted_score, "Typosquatting detected (Mimicking GitHub)"

    # 3. الروابط المختصرة (Fix Caution Bias)
    if domain in ["4se", "bit", "tinyurl", "t"]:
        adjusted_score = max(adjusted_score, 0.45) # ابقها في منطقة الشك
        
    return adjusted_score, None

def extract_features_v3(url):
    ext = tldextract.extract(url)
    domain = ext.domain.lower()
    suffix = ext.suffix.lower()
    
    # الـ 5 ميزات التي تدرب عليها الموديل الخاص بك
    url_len = len(url)
    dom_len = len(domain)
    is_saudi = 1 if suffix in ['sa', 'com.sa', 'gov.sa', 'edu.sa'] else 0
    
    def calc_entropy(text):
        if not text: return 0
        probs = [float(text.count(c)) / len(text) for c in set(text)]
        return -sum(p * math.log(p, 2) for p in probs)
    
    entropy = calc_entropy(domain)
    has_sus = 1 if any(w in url.lower() for w in ['login', 'verify', 'bank', 'secure']) else 0
    
    return [url_len, dom_len, is_saudi, entropy, has_sus]

# 6. Sidebar | القائمة الجانبية (V2.0)
with st.sidebar:
    st.image("my_photo.png", width=100)
    st.markdown(f"### **Ali Alkhamees**")
    st.info(f"🏛️ {L['sidebar_uni']}\n🎓 {L['sidebar_major']}")
    st.success(f"● {L['status_online']}")
    if st.button("🌐 Switch Language / تغيير اللغة"):
        st.session_state['language'] = 'ar' if st.session_state['language'] == 'en' else 'en'
        st.rerun()

# 7. Main Application Logic
st.title(L['main_title'])
st.markdown(f"### {L['main_subtitle']}")

with st.form("analysis_form"):
    url_input = st.text_input(L['input_label'], placeholder=L['input_placeholder'])
    submit = st.form_submit_button(L['btn_scan'])

if submit and url_input:
    with st.status("🔍 Analyzing...", expanded=False) as status:
        st.write(L['step1']); time.sleep(0.2)
        st.write(L['step2']); time.sleep(0.2)
        st.write(L['step3'])
        
        # استخراج الميزات والتنبؤ
        feats = extract_features_v3(url_input)
        raw_prob = model.predict_proba([feats])[0][1]
        
        # طبقة المعايرة السعودية (الحل الجذري)
        final_risk, forensic_note = hybrid_calibration(url_input, raw_prob)
        status.update(label=L['step4'], state="complete")

    # عرض النتائج بطريقة V2.0 الجمالية
    st.markdown("---")
    if final_risk < 0.30:
        st.markdown(f'<div class="result-card safe"><h2>{L["safe_title"]}</h2><p>{forensic_note if forensic_note else L["safe_desc"]}</p></div>', unsafe_allow_html=True)
    elif final_risk < 0.70:
        st.markdown(f'<div class="result-card caution"><h2>{L["caution_title"]}</h2><p>{L["caution_desc"]}</p></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="result-card danger"><h2>{L["phish_title"]}</h2><p>{forensic_note if forensic_note else L["phish_desc"]}</p></div>', unsafe_allow_html=True)

    # 8. XAI Visuals | الرسوم البيانية التوضيحية
    st.subheader(L['xai_title'])
    c1, c2 = st.columns(2)
    with c1:
        # Gauge Chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number", value = final_risk * 100,
            title = {'text': L['risk_label']},
            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#3b82f6"},
                     'steps': [{'range': [0, 30], 'color': "green"}, {'range': [30, 70], 'color': "orange"}, {'range': [70, 100], 'color': "red"}]}
        ))
        fig.update_layout(height=300, margin=dict(l=20,r=20,t=40,b=20), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        # Radar Chart
        categories = ['Length', 'Domain', 'Saudi', 'Entropy', 'Keywords']
        radar = go.Figure()
        radar.add_trace(go.Scatterpolar(r=[feats[0]/10, feats[1], feats[2]*10, feats[3]*2, feats[4]*10], theta=categories, fill='toself'))
        radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), showlegend=False, height=300, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(radar, use_container_width=True)

    # إضافة للسجل
    st.session_state['history'].insert(0, {"URL": url_input, L['col_status']: "✅ Safe" if final_risk < 0.3 else "🚨 Phish", L['col_engine']: f"{final_risk*100:.1f}%", L['col_time']: time.strftime("%H:%M")})

# 9. Scan History Table | جدول السجل (V2.0)
if st.session_state['history']:
    st.markdown("---")
    st.subheader(L['history_title'])
    st.dataframe(pd.DataFrame(st.session_state['history']), use_container_width=True, hide_index=True)

# 10. Footer | التذييل
st.markdown("<div style='text-align: center; color: gray; margin-top: 50px;'>© 2025 URL TRACKER Enterprise V3.2 by Ali Alkhamees</div>", unsafe_allow_html=True)
