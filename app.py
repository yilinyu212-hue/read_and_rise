import streamlit as st
import json
import os

st.set_page_config(page_title="Read & Rise | 全能双语精读馆", layout="wide")

# --- 数据加载 ---
DB_FILE = "library_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# --- 侧边栏：字体调节 ---
st.sidebar.title("🎨 视觉自定义")
f_size = st.sidebar.slider("调整字号", 14, 26, 18)
f_family = st.sidebar.selectbox("选择字体", ["Georgia, serif", "Arial, sans-serif", "Verdana"])

st.markdown(f"""
    <style>
    .reading-box {{
        font-family: {f_family};
        font-size: {f_size}px;
        line-height: 1.8;
        padding: 20px;
        background-color: #fcfcfc;
        border: 1px solid #eee;
        border-radius: 10px;
        height: 600px;
        overflow-y: auto;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 页面内容 ---
st.title("📖 Read & Rise 精读馆")
library = load_data()

if not library:
    st.info("馆长正在努力筹备中，请稍后再来...")
else:
    titles = [f"[{a['analysis'].get('label', '外刊')}] {a['title']}" for a in library]
    idx = st.selectbox("🔍 选择文章：", range(len(titles)), format_func=lambda x: titles[x])
    curr = library[idx]
    ana = curr['analysis']

    st.divider()
    
    # 核心：中英左右对照排版
    col_en, col_cn = st.columns(2)
    with col_en:
        st.subheader("🇬🇧 English")
        st.markdown(f'<div class="reading-box">{curr["body"].replace("\n", "<br>")}</div>', unsafe_allow_html=True)
    with col_cn:
        st.subheader("🇨🇳 中文翻译")
        st.markdown(f'<div class="reading-box" style="color:#555;">{ana.get("translation", "").replace("\n", "<br>")}</div>', unsafe_allow_html=True)

    st.divider()
    
    # 解析专区
    t1, t2, t3 = st.tabs(["🔤 核心词汇", "📝 写作语法", "🗣️ 口语实战"])
    with t1:
        for v in ana.get('vocabulary', []):
            st.write(f"**{v['word']}** : {v['mean']}")
            st.caption(f"例句：{v['ex']}")
            st.write("---")
    with t2:
        st.info(f"**语法分析：**\n\n{ana.get('grammar')}")
        st.success(f"**写作建议：**\n\n{ana.get('writing')}")
    with t3:
        st.warning(ana.get('oral'))