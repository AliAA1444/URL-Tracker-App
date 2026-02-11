import streamlit as st
import pandas as pd
import numpy as np
import joblib
import tldextract
import re
import math
import time
from difflib import SequenceMatcher

# 1. إعدادات الصفحة (V2.0 الأصلية)
st.set_page_config(page_title="URL TRACKER V3.2", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

if 'language' not in st.session_state: st.session_state['language'] = None
if 'history' not in st.session_state: st.session_state['history'] = []

# 2. القاموس الكامل والمصحح (تم إصلاح الـ KeyError)
T = {
    'en': {
        'sidebar_role': 'Cybersecurity & AI Researcher',
        'sidebar_uni': 'Majmaah University',
        'sidebar_major': 'Computer Science',
        'status_online': 'System Online | Guardrails Active',
        'main_title': '🛡️ URL TRACKER V3.2',
        'main_subtitle': 'Enterprise Phishing Intelligence (Calibrated)',
        'input_label': 'Analyze URL',
        'input_placeholder': 'Enter URL (e.g., https://www.alinma.com)',
        'btn_scan': 'SCAN NOW 🚀',
        'history_title': '🕒 Recent Scans',
        'safe_title': '✅ SAFE WEBSITE',
        'caution_title': '⚠️ CAUTION REQUIRED',
        'phish_title': '🚨 PHISHING DETECTED',
        'safe_desc': 'Verified or highly trusted infrastructure.',
        'caution_desc': 'Mixed signals detected. Exercise caution.',
        'phish_desc': 'Malicious fingerprint matched known attacks.',
        'risk_label': 'Risk Level:',
        'tech_details': '🔍 Forensic Analysis',
        'col_status': 'Status', 'col_risk': 'Score', 'col_time': 'Time',
        'disclaimer_title': '⚠️ Terms of Use',
        'disclaimer_text': "1. Educational project. 2. No 100% guarantee. 3. Use at your own risk."
    },
    'ar': {
        'sidebar_role': 'باحث في الأمن السيبراني والذكاء الاصطناعي',
        'sidebar_uni': 'جامعة المجمعة',
        'sidebar_major': 'علوم الحاسب',
        'status_online': 'النظام يعمل | تم تفعيل الحماية',
        'main_title': '🛡️ URL TRACKER V3.2',
        'main_subtitle': 'نظام استخبارات الروابط (معاير للسوق السعودي)',
        'input_label': 'حلل الرابط الآن',
        'input_placeholder': 'ضع الرابط هنا (مثال: https://www.alinma.com)',
        'btn_scan': '🚀 ابدأ الفحص',
        'history_title': '🕒 سجل الفحص',
        'safe_title': '✅ موقع آمن وموثوق',
        'caution_title': '⚠️ منطقة شك (انتباه)',
        'phish_title': '🚨 تم كشف محاولة تصيد',
        'safe_desc': 'تم التحقق من النطاق كبنية موثوقة.',
        'caution_desc': 'إشارات مختلطة، يرجى الحذر والتحقق.',
        'phish_desc': 'تم العثور على أنماط مطابقة لعمليات الاحتيال.',
        'risk_label': 'تقييم المخاطر:',
        'tech_details': '🔍 التحليل الجنائي الرقمي',
        'col_status': 'الحالة', 'col_risk': 'درجة الخطر', 'col_time': 'الوقت',
        'disclaimer_title': '⚠️ شروط الاستخدام',
        'disclaimer_text': "1. غرض تعليمي. 2. لا توجد أداة دقيقة 100%. 3. المطور غير مسؤول عن الأضرار."
    }
}

# 3. شاشة اختيار اللغة
if st.session_state['language'] is None:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🛡️ URL TRACKER</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("English 🇺🇸", use_container_width=True): st.session_state['language'] = 'en'; st.rerun()
        st.write("")
        if st.button("العربية 🇸🇦", use_container_width=True): st.session_state['language'] = 'ar'; st.rerun()
    st.stop()

L = T[st.session_state['language']]

# 4. محرك التحليل والمنطق (Hybrid Logic)
@st.cache_resource
def load_v3_model():
    try: return joblib.load('url_tracker_v3_model.pkl')
    except: return None

model = load_v3_model()

def normalize_url(url):
    url = url.strip().lower()
    url = url.replace('https//', 'https://').replace('http//', 'http://')
    if not url.startswith(('http://', 'https://')): url = 'https://' + url
    return url

def analyze_engine(url):
    clean_url = normalize_url(url)
    ext = tldextract.extract(clean_url)
    full_domain = f"{ext.domain}.{ext.suffix}"
    
    # 1. طبقة السمعة (حل مشكلة الإنماء)
    sa_trust = ['alinma.com', 'stc.com.sa', 'absher.sa', 'moi.gov.sa', 'mu.edu.sa', 'google.com', 'kaggle.com', 'claude.ai']
    if full_domain in sa_trust: return 0.05, "Verified Trusted Infrastructure"
    
    # 2. طبقة الحماية (حل مشكلة Gilhub)
    if SequenceMatcher(None, ext.domain, "github").ratio() > 0.8 and ext.domain != "github":
        return 0.88, "Typosquatting (GitHub Clone)"
    
    # 3. طبقة الذكاء الاصطناعي (5 ميزات)
    def entropy(text):
        if not text: return 0
        probs = [float(text.count(c)) / len(text) for c in set(text)]
        return -sum(p * math.log(p, 2) for p in probs)
        
    feat = [len(clean_url), len(ext.domain), 1 if ext.suffix in ['sa', 'com.sa'] else 0, entropy(ext.domain), 0]
    
    # 4. دمج النتائج مع العقوبة لـ http
    base_risk = model.predict_proba([feat])[0][1] if model else 0.5
    if url.startswith("http://"): base_risk = min(0.99, base_risk + 0.40)
    
    return base_risk, "AI Neural Scan"

# 5. الواجهة الرئيسية
st.markdown(f"<style>.result-card {{ padding: 20px; border-radius: 12px; border-left: 10px solid; margin-bottom: 20px; }} .safe {{ background: #d1e7dd; color: #0f5132; border-color: #198754; }} .caution {{ background: #fff3cd; color: #856404; border-color: #ffc107; }} .danger {{ background: #f8d7da; color: #842029; border-color: #dc3545; }}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.image("my_photo.png", width=100)
    st.markdown(f"### **Ali Alkhamees**\n*{L['sidebar_role']}*")
    st.info(f"🏛️ {L['sidebar_uni']}\n🎓 {L['sidebar_major']}")
    st.success(f"● {L['status_online']}")
    if st.button("🌐 Language / اللغة"):
        st.session_state['language'] = 'ar' if st.session_state['language'] == 'en' else 'en'; st.rerun()

st.title(L['main_title'])
st.markdown(f"**{L['main_subtitle']}**")

with st.form("scan"):
    u_input = st.text_input(L['input_label'], placeholder=L['input_placeholder'])
    submit = st.form_submit_button(L['btn_scan'])

if submit and u_input:
    with st.spinner("Analyzing..."):
        risk, note = analyze_engine(u_input)
        risk_pct = risk * 100
        
    if risk < 0.30:
        st.markdown(f'<div class="result-card safe"><h2>{L["safe_title"]}</h2><p>{L["safe_desc"]}</p><p><i>{note}</i></p></div>', unsafe_allow_html=True)
        status_label = "✅ Safe"
    elif risk < 0.70:
        st.markdown(f'<div class="result-card caution"><h2>{L["caution_title"]}</h2><p>{L["caution_desc"]}</p><p><i>{note}</i></p></div>', unsafe_allow_html=True)
        status_label = "⚠️ Caution"
    else:
        st.markdown(f'<div class="result-card danger"><h2>{L["phish_title"]}</h2><p>{L["phish_desc"]}</p><p><i>{note}</i></p></div>', unsafe_allow_html=True)
        status_label = "🚨 Phish"

    st.write(f"**{L['risk_label']} {risk_pct:.1f}%**")
    st.progress(risk)

    st.session_state['history'].insert(0, {"URL": u_input, L['col_status']: status_label, L['col_risk']: f"{risk_pct:.1f}%", L['col_time']: time.strftime("%H:%M")})

if st.session_state['history']:
    st.subheader(L['history_title'])
    st.table(pd.DataFrame(st.session_state['history']).head(10))
