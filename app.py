import streamlit as st
import json
import os

st.set_page_config(page_title="Read & Rise 精读馆", layout="wide")

# --- 1. 加载数据 ---
DB_FILE = "library_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# --- 2. 侧边栏：变量名统一为 current_font ---
st.sidebar.title("🎨 视觉自定义")
current_size = st.sidebar.slider("调整字号", 14, 26, 18)
current_font = st.sidebar.selectbox("选择字体", ["Georgia, serif", "Arial, sans-serif", "Verdana"])

# --- 3. 样式注入：解决英文消失问题 ---
# 强制背景为白色，文字为深灰色，确保深色模式下也能看清
st.markdown(f"""
    <style>
    .reading-box {{
        font-family: {current_font} !important;
        font-size: {current_size}px !important;
        line-height: 1.8 !important;
        padding: 25px !important;
        background-color: #FFFFFF !important;  /* 强制白底 */
        color: #1A1A1A !important;             /* 强制深色字 */
        border: 1px solid #DDDDDD !important;
        border-radius: 12px !important;
        height: 600px !important;
        overflow-y: auto !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. 页面内容 ---
st.title("📖 Read & Rise 精读馆")
library = load_data()

if not library:
    st.info("馆长正在努力更新中，请稍后再来...")
else:
    # 修复截图一中的 TypeError: string indices 隐患
    titles = []
    for a in library:
        label = a.get('analysis', {}).get('label', '外刊')
        title = a.get('title', '无标题')
        titles.append(f"[{label}] {title}")
        
    idx = st.selectbox("🔍 选择学习文章：", range(len(titles)), format_func=lambda x: titles[x])
    curr = library[idx]
    ana = curr.get('analysis', {})

    # 左右对照排版
    col_en, col_cn = st.columns(2)
    with col_en:
        st.subheader("🇬🇧 English Original")
        st.markdown(f'<div class="reading-box">{curr.get("body", "").replace("\n", "<br>")}</div>', unsafe_allow_html=True)
    with col_cn:
        st.subheader("🇨🇳 中文翻译")
        st.markdown(f'<div class="reading-box" style="color:#444 !important;">{ana.get("translation", "暂无翻译").replace("\n", "<br>")}</div>', unsafe_allow_html=True)

    st.divider()
    
    # 底部解析 Tab
    t1, t2, t3 = st.tabs(["🔤 核心词汇", "📝 写作语法", "🗣️ 口语实战"])
    with t1:
        for v in ana.get('vocabulary', []):
            st.write(f"**{v.get('word')}** : {v.get('mean')}")
            st.caption(f"例句：{v.get('ex')}")
            st.write("---")
    with t2:
        st.info(f"**语法拆解：**\n\n{ana.get('grammar', '暂无')}")
        st.success(f"**写作建议：**\n\n{ana.get('writing', '暂无')}")
    with t3:
        st.warning(ana.get('oral', '暂无'))
