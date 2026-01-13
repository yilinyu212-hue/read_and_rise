import streamlit as st
from openai import OpenAI
import json
import os

# --- 1. 核心配置 ---
DEEPSEEK_API_KEY = "sk-65709264042e4c0ca811f7a76386a319" 
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

st.set_page_config(page_title="Read & Rise | 全自动双语馆", layout="wide")

# 建议使用新数据库文件名以确保格式兼容
DB_FILE = "read_rise_v6_full_translation.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

def save_data(article_obj):
    db = load_data()
    db.insert(0, article_obj)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

# --- 2. 侧边栏：视觉自定义 ---
st.sidebar.title("🎨 视觉自定义")
font_choice = st.sidebar.selectbox("选择字体", ["Georgia, serif", "Arial, sans-serif", "Verdana"])
font_size = st.sidebar.slider("调整字号", 14, 26, 18)
line_height = st.sidebar.slider("行间距", 1.5, 2.5, 1.8)

st.markdown(f"""
    <style>
    .reading-box {{
        font-family: {font_choice};
        font-size: {font_size}px;
        line-height: {line_height};
        padding: 20px;
        border-radius: 10px;
        height: 600px;
        overflow-y: auto;
        background-color: #fcfcfc;
        border: 1px solid #eee;
    }}
    .translation-box {{ color: #444; background-color: #f9f9f9; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. 强化版 AI 解析引擎（核心：强制生成翻译） ---
def get_comprehensive_analysis(title, content):
    # 这里的提示词经过强化，强制要求生成高质量翻译
    prompt = f"""
    作为专业的英语教育家和翻译家，请深度解析外刊《{title}》。
    
    任务要求：
    1. 必须提供全文的【高质量中文翻译】，要求忠实原文且表达流畅。
    2. 识别文章的适合级别（如雅思、托福）。
    3. 提取核心词汇，包含音标、释义和双语例句。
    4. 分析长难句，提供写作句式和口语应用。

    原文如下：
    {content[:3000]}
    
    请严格按以下 JSON 格式输出：
    {{
        "label": "建议等级",
        "full_translation": "这里请填入完整的中文翻译内容...",
        "vocabulary": [
            {{"word": "单词 [音标]", "mean": "中文义", "ex": "中英对照例句"}}
        ],
        "grammar": "长难句解析",
        "writing": "写作句式",
        "oral": "口语应用"
    }}
    """
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        response_format={'type': 'json_object'}
    )
    return json.loads(response.choices[0].message.content)

# --- 4. 界面展示 ---
st.title("📖 Read & Rise: 全自动双语精读馆")

tab_read, tab_admin = st.tabs(["💡 学习中心", "🛠️ 老师管理后台"])

with tab_admin:
    st.subheader("发布新内容")
    new_t = st.text_input("文章标题")
    new_c = st.text_area("文章正文", height=250)
    if st.button("✨ 自动生成翻译并存入库"):
        if new_t and new_c:
            with st.spinner("AI 正在全力翻译并解析中..."):
                try:
                    analysis_res = get_comprehensive_analysis(new_t, new_c)
                    save_data({"title": new_t, "body": new_c, "analysis": analysis_res})
                    st.success("教案及翻译生成成功！")
                except Exception as e:
                    st.error(f"生成失败：{e}")

with tab_read:
    articles = load_data()
    if not articles:
        st.info("库中还没有文章，请先前往管理后台录入。")
    else:
        titles = [f"[{a['analysis'].get('label', '外刊')}] {a['title']}" for a in articles]
        idx = st.selectbox("🔍 选择要学习的文章：", range(len(titles)), format_func=lambda x: titles[x])
        curr = articles[idx]
        ana = curr['analysis']

        st.divider()
        
        # 左右对照排版
        col_en, col_cn = st.columns(2)
        with col_en:
            st.markdown("##### 🇬🇧 English Original")
            st.markdown(f'<div class="reading-box">{curr["body"].replace("\n", "<br>")}</div>', unsafe_allow_html=True)
        with col_cn:
            st.markdown("##### 🇨🇳 自动生成翻译")
            # 这里调用 ana["full_translation"] 确保显示生成的内容
            translated_text = ana.get("full_translation", "AI 未能生成翻译，请尝试重新解析。")
            st.markdown(f'<div class="reading-box translation-box">{translated_text.replace("\n", "<br>")}</div>', unsafe_allow_html=True)

        st.divider()
        
        # 教学解析
        st.subheader("🧠 深度解析专区")
        c1, c2, c3 = st.columns(3)
        with c1:
            with st.expander("🔤 核心词汇卡片", expanded=True):
                for v in ana.get('vocabulary', []):
                    st.write(f"**{v['word']}** : {v['mean']}")
                    st.caption(f"例句：{v['ex']}")
                    st.write("---")
        with c2:
            with st.expander("📝 写作与语法", expanded=True):
                st.info(ana.get('grammar', '暂无解析'))
                st.success(ana.get('writing', '暂无句式'))
        with c3:
            with st.expander("🗣️ 口语实战", expanded=True):
                st.warning(ana.get('oral', '暂无建议'))

st.sidebar.markdown("---")
st.sidebar.caption("Read & Rise - 教育者专用版")