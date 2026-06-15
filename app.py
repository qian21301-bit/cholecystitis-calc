import streamlit as st
import pandas as pd
import numpy as np
import joblib

# ===================== 页面基础配置 =====================
st.set_page_config(
    page_title="急性胆囊炎风险识别计算器",
    page_icon="🏥",
    layout="centered"
)

st.title("胆囊结石患者急性胆囊炎风险识别计算器")
st.markdown("本计算器基于XGB机器学习模型，用于评估胆囊结石患者发生急性胆囊炎的风险。")
st.divider()


# ===================== 加载模型（缓存加速） =====================
@st.cache_resource
def load_model_bundle():
    bundle = joblib.load("final_model_bundle.joblib")
    return bundle


bundle = load_model_bundle()
model = bundle["best_model"]
calibrator = bundle["calibrator"]
features = bundle["features"]
winsor_bounds = bundle["winsor_bounds"]

# 验证集确定的风险分层阈值（固定值，不随测试集变动）
LOW_RISK_THRESHOLD = 0.125  # < 12.5% → 低风险
HIGH_RISK_THRESHOLD = 0.155  # ≥ 15.5% → 高风险

# ===================== 输入区 =====================
st.subheader("患者基础信息")

age = st.number_input("年龄（岁）", min_value=18, max_value=100, value=60)
sex_text = st.selectbox("性别", ["女", "男"])
sex = 1 if sex_text == "男" else 0

# 身高体重双列布局 → 自动计算BMI
col_h, col_w = st.columns(2)
with col_h:
    height = st.number_input("身高（cm）", min_value=100.0, max_value=250.0, value=165.0, step=0.1)
with col_w:
    weight = st.number_input("体重（kg）", min_value=30.0, max_value=200.0, value=60.0, step=0.1)

# 实时自动计算并显示BMI
bmi = weight / ((height / 100) ** 2)
st.info(f"✅ 自动计算 BMI：{bmi:.1f} kg/m²")

st.divider()
st.subheader("实验室检查指标")

ast = st.number_input("AST (天门冬氨酸氨基转移酶)（U/L）", min_value=0.0, max_value=1000.0, value=30.0, step=0.1)
alt = st.number_input("ALT (丙氨酸氨基酸转移酶)（U/L）", min_value=0.0, max_value=1000.0, value=30.0, step=0.1)
ggt = st.number_input("GGT (r-谷氨酰转肽酶)（U/L）", min_value=0.0, max_value=2000.0, value=50.0, step=0.1)
tb = st.number_input("TB(总胆红素)（mol/L）", min_value=0.0, max_value=1000.0, value=20.0, step=0.1)
hgb = st.number_input("HGB (血红蛋白)（g/L）", min_value=30.0, max_value=250.0, value=130.0, step=0.1)

# ===================== 计算按钮 + 预测逻辑 =====================
if st.button("🧮 计算风险", type="primary", use_container_width=True):
    # 构造输入数据，列名必须与模型训练时的特征名完全一致
    input_df = pd.DataFrame([{
        "年龄": age,
        "性别": sex,
        "BMI": bmi,
        "AST (天门冬氨酸氨基转移酶)U/L": ast,
        "ALT (丙氨酸氨基酸转移酶) U/L": alt,
        "GGT (r-谷氨酰转肽酶)U/L": ggt,
        "TB(总胆红素)mol/L": tb,
        "HGB (血红蛋白)g/L": hgb
    }])

    # 按模型特征顺序对齐
    input_df = input_df[features]

    # 执行缩尾处理（和训练集保持一致）
    for col, bounds in winsor_bounds.items():
        if col in input_df.columns:
            lower, upper = bounds
            input_df[col] = input_df[col].clip(lower, upper)

    # 模型预测 + 概率校准
    raw_prob = model.predict_proba(input_df)[:, 1]
    calibrated_prob = calibrator.predict(raw_prob)[0]
    prob_percent = calibrated_prob * 100

    # 风险分层
    if calibrated_prob < LOW_RISK_THRESHOLD:
        risk_level = "低风险"
        explanation = "该患者根据模型预测属于低风险人群，发生急性胆囊炎的风险较低，建议常规随访观察。"
    elif calibrated_prob < HIGH_RISK_THRESHOLD:
        risk_level = "中风险"
        explanation = "该患者根据模型预测属于中风险人群，存在一定急性胆囊炎风险，建议结合临床症状、体征及影像学检查进一步评估。"
    else:
        risk_level = "高风险"
        explanation = "该患者根据模型预测属于高风险人群，发生急性胆囊炎的可能性较高，建议重点关注，结合临床综合判断，必要时及时干预。"

    # ===================== 输出区 =====================
    st.divider()
    st.subheader("📊 预测结果")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("预测风险", f"{prob_percent:.1f}%")
    with col2:
        st.metric("风险分层", risk_level)

    # ===================== 解释区 =====================
    st.success(explanation)

# 底部免责声明
st.divider()
st.caption("⚠️ 本工具仅用于科研展示与风险辅助识别，不能替代专业临床诊断。")