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

# =========================================================
# 1. PAGE CONFIGURATION | إعدادات الصفحة (V2.0 الأصلية)
# =========================================================
st.set_page_config(
    page_title="URL TRACKER V3.2",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تهيئة الجلسة
if 'language' not in st.session_state: st.session_state['language'] = None
if 'history' not in st.session_state: st.session_state['history'] = []

# =========================================================
# 2. LOCALIZATION | قاموس اللغات (V2.0 + تصحيحات)
# =========================================================
T = {
    'en': {
        'sidebar_role': 'Cybersecurity & AI Researcher',
        'sidebar_uni': 'Majmaah University',
        'sidebar_major': 'Computer Science',
        'status_online': 'System Online | Guardrails Active',
        'main_title': '🛡️ URL TRACKER V3.2 | Enterprise AI',
        'main_subtitle': 'Heuristic-Augmented Phishing Intelligence',
        'input_label': 'Analyze URL',
        'input_placeholder': 'Enter URL (e.g., https://www.alinma.com)',
        'btn_scan': 'SCAN NOW 🚀',
        'history_title': '🕒 Recent Scans',
        'safe_title': '✅ SAFE WEBSITE',
        'caution_title': '⚠️ CAUTION REQUIRED',
        'phish_title': '🚨 PHISHING DETECTED',
        'risk_label': 'Final Risk Score:',
        'tech_details': '🔍 Forensic Analysis',
        'col_status': 'Status', 'col_risk': 'Score', 'col_time': 'Time',
        'disclaimer_title': '⚠️ Terms of Use',
        'disclaimer_text': "**1. Educational Purpose:** Part of a CS project. **2. No Guarantee:** AI results are probabilistic. **3. Liability:** Ali Alkhamees is not responsible for damages."
    },
    'ar': {
        'sidebar_role': 'باحث في الأمن السيبراني والذكاء الاصطناعي',
        'sidebar_uni': 'جامعة المجمعة',
        'sidebar_major': 'علوم الحاسب',
        'status_online': 'النظام يعمل | تم تفعيل الحماية القصوى',
        'main_title': '🛡️ URL TRACKER V3.2 | نظام كشف التصيد',
        'main_subtitle': 'ذكاء اصطناعي معزز بقواعد أمنية صارمة',
        'input_label': 'حلل الرابط الآن',
        'input_placeholder': 'ضع الرابط هنا (مثال: https://www.alinma.com)',
        'btn_scan': '🚀 ابدأ الفحص',
        'history_title': '🕒 سجل الفحص',
        'safe_title': '✅ موقع آمن وموثوق',
        'caution_title': '⚠️ منطقة شك (انتباه)',
        'phish_title': '🚨 تم كشف محاولة تصيد',
        'risk_label': 'تقييم المخاطر النهائي:',
        'tech_details': '🔍 التحليل الجنائي الرقمي',
        'col_status': 'الحالة', 'col_risk': 'درجة الخطر', 'col_time': 'الوقت',
        'disclaimer_title': '⚠️ إخلاء مسؤولية وشروط الاستخدام',
        'disclaimer_text': "**1. غرض تعليمي:** أداة بحثية لمشروع علوم حاسب. **2. لا يوجد ضمان:** لا توجد أداة دقيقة بنسبة 100%. **3. المسؤولية:** المطور علي الخميس غير مسؤول عن أي أضرار."
    }
}

# =========================================================
# 3. LANGUAGE SELECTION | شاشة اختيار اللغة
# =========================================================
if st.session_state['language'] is None:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🛡️ URL TRACKER</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("English 🇺🇸", use_container_width=True): st.session_state['language'] = 'en'; st.rerun()
        st.write("")
        if st.button("العربية 🇸🇦", use_container_width=True): st.session_state['language'] = 'ar'; st.rerun()
    st.stop()

L = T[st.session_state['language']]
is_rtl = st.session_state['language'] == 'ar'

# =========================================================
# 4. DESIGN & CSS | التصميم (استعادة جمال V2.0)
# =========================================================
st.markdown(f"""
    <style>
    .main {{ background-color: #f8f9fa; direction: {'rtl' if is_rtl else 'ltr'}; }}
    .result-card {{ padding: 25px; border-radius: 15px; margin-bottom: 20px; border-left: 10px solid; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
    .safe {{ background: #d1e7dd; color: #0f5132; border-color: #198754; }}
    .caution {{ background: #fff3cd; color: #856404; border-color: #ffc107; }}
    .danger {{ background: #f8d7da; color: #842029; border-color: #dc3545; }}
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# 5. CORE ENGINE LOGIC | منطق المحرك المعاير
# =========================================================
@st.cache_resource
def load_v3_model():
    try: return joblib.load('url_tracker_v3_model.pkl')
    except: return None

model = load_v3_model()

def normalize_url(url):
    """تصحيح الأخطاء الهيكلية في الرابط قبل الفحص"""
    url = url.strip().lower()
    url = url.replace('https//', 'https://').replace('http//', 'http://')
    if not url.startswith(('http://', 'https://')): url = 'https://' + url
    return url

def get_calibrated_score(url):
    clean_url = normalize_url(url)
    ext = tldextract.extract(clean_url)
    domain = ext.domain
    full_domain = f"{domain}.{ext.suffix}"
    
    # 1. القاعدة الذهبية: المواقع السعودية الرسمية (أمان مطلق)
    sa_trust = ['alinma.com', 'stc.com.sa', 'absher.sa', 'moi.gov.sa', 'mu.edu.sa', 'moe.gov.sa']
    if full_domain in sa_trust: return 0.05, "Verified Saudi Infrastructure"
    
    # 2. القاعدة الصارمة: البروتوكول غير الآمن (خطر فوري)
    risk_boost = 0.0
    if url.startswith("http://"): risk_boost += 0.40
    
    # 3. القاعدة الصارمة: انتحال الهوية (Gilhub)
    if SequenceMatcher(None, domain, "github").ratio() > 0.8 and domain != "github":
        return 0.88, "Brand Impersonation (GitHub Clone)"

    # 4. استخراج الميزات للذكاء الاصطناعي
    def calc_entropy(text):
        if not text: return 0
        probs = [float(text.count(c)) / len(text) for c in set(text)]
        return -sum(p * math.log(p, 2) for p in probs) # معادلة شانون: $H(S) = -\sum p_i \log_2(p_i)$
        
    feat = [len(clean_url), len(domain), 1 if ext.suffix in ['sa', 'com.sa'] else 0, calc_entropy(domain), 0]
    
    # التنبؤ ودمج القواعد
    ml_prob = model.predict_proba([feat])[0][1] if model else 0.5
    final_risk = min(0.99, ml_prob + risk_boost)
    
    return final_risk, "Hybrid Neural + Heuristic Analysis"

# =========================================================
# 6. SIDEBAR | القائمة الجانبية (V2.0 كاملة)
# =========================================================
with st.sidebar:
    st.image("my_photo.png", width=100)
    st.markdown(f"### **Ali Alkhamees**")
    st.markdown(f"*{L['sidebar_role']}*")
    st.info(f"🏛️ {L['sidebar_uni']}\n🎓 {L['sidebar_major']}")
    st.markdown("---")
    st.link_button("🔗 LinkedIn Profile", "https://www.linkedin.com/in/ali-alkhamees-378b34367/")
    st.link_button("🏛️ Majmaah University", "https://www.mu.edu.sa/ar")
    st.success(f"● {L['status_online']}")
    if st.sidebar.button("🌐 Language / اللغة"):
        st.session_state['language'] = 'ar' if st.session_state['language'] == 'en' else 'en'
        st.rerun()

# =========================================================
# 7. MAIN UI & EXECUTION | الواجهة والتشغيل
# =========================================================
st.title(L['main_title'])
st.markdown(f"### {L['main_subtitle']}")

with st.form("scan_form"):
    u_input = st.text_input(L['input_label'], placeholder=L['input_placeholder'])
    submit = st.form_submit_button(L['btn_scan'])

if submit and u_input:
    with st.spinner('📡 Scanning infrastructure...'):
        risk, note = get_calibrated_score(u_input)
        risk_pct = risk * 100
        time.sleep(0.4)

    # تحديد الزون والوسام (حل مصيبة السجل)
    if risk < 0.30:
        st.markdown(f'<div class="result-card safe"><h2>{L["safe_title"]}</h2><p>{note}</p></div>', unsafe_allow_html=True)
        status_label = "✅ Safe"
    elif risk < 0.70:
        st.markdown(f'<div class="result-card caution"><h2>{L["caution_title"]}</h2><p>{L["caution_desc"]}</p></div>', unsafe_allow_html=True)
        status_label = "⚠️ Caution"
    else:
        st.markdown(f'<div class="result-card danger"><h2>{L["phish_title"]}</h2><p>{note if "Clone" in note else L["phish_desc"]}</p></div>', unsafe_allow_html=True)
        status_label = "🚨 Danger"

    st.write(f"**{L['risk_label']} {risk_pct:.1f}%**")
    st.progress(risk)

    # تحديث السجل (الآن السجل سيحترم حالة الأمان)
    st.session_state['history'].insert(0, {
        "URL": u_input, 
        L['col_status']: status_label, 
        L['col_risk']: f"{risk_pct:.1f}%", 
        L['col_time']: time.strftime("%H:%M")
    })

# =========================================================
# 8. HISTORY & FOOTER | السجل والتذييل
# =========================================================
if st.session_state['history']:
    st.markdown("---")
    st.subheader(L['history_title'])
    st.table(pd.DataFrame(st.session_state['history']).head(10))

st.markdown("---")
with st.expander(L['disclaimer_title']):
    st.markdown(L['disclaimer_text'])
st.markdown("<div style='text-align: center; color: gray;'>© 2026 URL TRACKER Stable V3.2 by Ali Alkhamees</div>", unsafe_allow_html=True)
