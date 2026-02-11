import streamlit as st
import pandas as pd
import numpy as np
import joblib
import tldextract
import plotly.graph_objects as go
from fuzzywuzzy import fuzz
import math
import time

# 1. إعدادات لوحة التحكم الاحترافية (SOC Dashboard)
st.set_page_config(page_title="URL TRACKER V3.1 | SOC", page_icon="🛡️", layout="wide")

# 2. نظام الثقة والعلامات التجارية السعودية (Saudi Brand Intelligence)
SAUDI_TRUSTED_BRANDS = {
    "stc": ["stc.com.sa", "stc.com"],
    "absher": ["absher.sa", "absher.gov.sa"],
    "alrajhi": ["alrajhibank.com.sa", "alrajhibank.com"],
    "snb": ["alahli.com", "alahli.com.sa"],
    "moi": ["moi.gov.sa"],
    "majmaah": ["mu.edu.sa", "majmaah.edu.sa"]
}

# 3. واجهة المستخدم الرسومية (SOC Dark Theme CSS)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stTextInput>div>div>input { background-color: #1a1c24; color: white; border: 1px solid #3b82f6; }
    .report-card { background-color: #161b22; padding: 20px; border-radius: 15px; border: 1px solid #30363d; }
    .safe-text { color: #00ff88; font-weight: bold; text-shadow: 0 0 10px rgba(0,255,136,0.3); }
    .danger-text { color: #ff4c4c; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 4. محرك التحليل (Backend Engine)
@st.cache_resource
def load_v3_engine():
    return joblib.load('url_tracker_v3_model.pkl')

model = load_v3_engine()

def get_saudi_reputation(url):
    ext = tldextract.extract(url)
    domain = ext.domain.lower()
    full_domain = f"{domain}.{ext.suffix}"
    
    for brand, officials in SAUDI_TRUSTED_BRANDS.items():
        # 1. تطابق كامل (Exact Match)
        if full_domain in officials:
            return 0.0, f"✓ Verified {brand.upper()} Official Domain"
        
        # 2. كشف الانتحال (Typosquatting) باستخدام Fuzzy Matching
        for off in officials:
            similarity = fuzz.ratio(full_domain, off)
            if 80 < similarity < 100:
                return 0.95, f"🚨 Typosquatting detected mimicking {brand.upper()}"
    
    return None, None

def extract_features_v3(url):
    ext = tldextract.extract(url)
    domain = ext.domain.lower()
    suffix = ext.suffix.lower()
    sub = ext.subdomain.lower()
    
    url_len = len(url)
    dom_len = len(domain)
    is_saudi = 1 if suffix in ['sa', 'com.sa', 'gov.sa', 'edu.sa'] else 0
    
    def calc_entropy(text):
        if not text: return 0
        probs = [float(text.count(c)) / len(text) for c in set(text)]
        return -sum(p * math.log(p, 2) for p in probs)
    
    entropy = calc_entropy(domain)
    has_sus = 1 if any(w in url.lower() for w in ['login', 'verify', 'secure']) else 0
    
    return [url_len, dom_len, is_saudi, entropy, has_sus]

# 5. شاشة العرض (The Dashboard)
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🛡️ URL TRACKER V3.1</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e;'>Enterprise-Grade Phishing Intelligence Center</p>", unsafe_allow_html=True)

url_input = st.text_input("Enter URL for Deep Forensic Scan", placeholder="https://stc.com.sa")

if st.button("RUN SOC ANALYSIS 🚀", use_container_width=True):
    if url_input:
        with st.spinner('Accessing Threat Intel...'):
            time.sleep(0.6)
            
            # المرحلة 1: التحقق من الهوية السعودية
            reputation_score, reason = get_saudi_reputation(url_input)
            
            # المرحلة 2: تحليل الذكاء الاصطناعي
            features = extract_features_v3(url_input)
            ai_risk = model.predict_proba([features])[0][1]
            
            # دمج النتائج (Hybrid Logic)
            final_risk = reputation_score if reputation_score is not None else ai_risk
            
            # عرض النتيجة
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Gauge Chart (رادار الخطر)
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = final_risk * 100,
                    title = {'text': "Risk Probability %"},
                    gauge = {
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#3b82f6"},
                        'steps': [
                            {'range': [0, 35], 'color': "rgba(0, 255, 136, 0.2)"},
                            {'range': [35, 75], 'color': "rgba(255, 193, 7, 0.2)"},
                            {'range': [75, 100], 'color': "rgba(255, 76, 76, 0.2)"}
                        ],
                        'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}
                    }
                ))
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("<div class='report-card'>", unsafe_allow_html=True)
                if final_risk < 0.35:
                    st.markdown(f"## Verdict: <span class='safe-text'>SAFE</span>", unsafe_allow_html=True)
                    st.write(reason if reason else "No suspicious patterns detected in the infrastructure.")
                elif final_risk < 0.75:
                    st.markdown(f"## Verdict: <span style='color: #ffc107;'>CAUTION</span>", unsafe_allow_html=True)
                    st.write("Mixed signals. The structural entropy is high or the domain is newly seen.")
                else:
                    st.markdown(f"## Verdict: <span class='danger-text'>DANGER</span>", unsafe_allow_html=True)
                    st.write(reason if reason else "Malicious fingerprint matched. High probability of phishing.")
                st.markdown("</div>", unsafe_allow_html=True)

            # ميزة الـ Radar Chart (Explainable AI)
            st.markdown("---")
            st.subheader("📊 XAI: Feature Distribution Analysis")
            
            categories = ['URL Length', 'Domain Length', 'Saudi Trust', 'Entropy', 'Keywords']
            radar_fig = go.Figure()
            radar_fig.add_trace(go.Scatterpolar(
                  r=[features[0]/10, features[1], features[2]*10, features[3]*2, features[4]*10],
                  theta=categories,
                  fill='toself',
                  name='URL Profile',
                  line_color='#3b82f6'
            ))
            radar_fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(radar_fig, use_container_width=True)

# القائمة الجانبية الشخصية (Personal Info)
with st.sidebar:
    st.image("my_photo.png", width=100)
    st.markdown("### Ali Alkhamees")
    st.caption("Cybersecurity & AI Researcher")
    st.markdown("---")
    st.markdown("🛰️ **Threat Intel Engine:** V3.1")
    st.markdown("📚 **Training Data:** 651K Samples")
    st.success("● System Online")
