# 急性胆囊炎风险计算器 - Streamlit永久云端版
# 基于你原有Flask代码1:1改造，计算逻辑完全不变
import streamlit as st


# ====================== 【你的原始计算公式，完全没改】 ======================
def predict_cholecystitis(age, gender, bmi, nlr, tg, hdl):
    weights = {
        "age": age * 0.02,
        "gender": 5 if gender == 1 else 0,
        "bmi": bmi * 0.8,
        "nlr": nlr * 3,
        "tg": tg * 4,
        "hdl": hdl * (-5)
    }
    base_risk = 10
    total_risk = base_risk + sum(weights.values())
    total_risk = max(5, min(95, round(total_risk, 1)))

    if total_risk < 30:
        risk_level = "低风险"
        suggestion = "建议门诊随访，定期复查相关指标"
    elif total_risk < 70:
        risk_level = "中风险"
        suggestion = "建议尽快就医完善检查，必要时住院观察"
    else:
        risk_level = "高风险"
        suggestion = "立即急诊就诊，高度怀疑急性胆囊炎风险"
    return total_risk, risk_level, suggestion


# ====================== 页面UI（手机友好） ======================
st.set_page_config(
    page_title="急性胆囊炎风险计算器",
    page_icon="🏥",
    layout="centered"  # 手机适配最佳
)

# 标题
st.title("🏥 急性胆囊炎风险计算器")
st.markdown("---")

# 输入表单
with st.form("calc_form"):
    st.subheader("请输入临床指标")
    age = st.number_input("年龄(岁)", min_value=1, max_value=120, value=50)
    gender = st.radio("性别", options=[1, 0], format_func=lambda x: "男" if x == 1 else "女", horizontal=True)

    col1, col2 = st.columns(2)
    with col1:
        height = st.number_input("身高(cm)", min_value=50.0, max_value=250.0, value=165.0)
    with col2:
        weight = st.number_input("体重(kg)", min_value=10.0, max_value=200.0, value=65.0)

    nlr = st.number_input("NLR 中性粒细胞比值", min_value=0.1, max_value=50.0, value=2.0, step=0.1)
    tg = st.number_input("甘油三酯 TG (mmol/L)", min_value=0.1, max_value=20.0, value=1.5, step=0.1)
    hdl = st.number_input("高密度脂蛋白 HDL-C (mmol/L)", min_value=0.1, max_value=5.0, value=1.2, step=0.1)

    # 计算按钮
    submit = st.form_submit_button("🧮 计算患病概率", type="primary")

# 自动计算BMI
bmi = weight / ((height / 100) ** 2)
st.info(f"📊 自动计算 BMI：{bmi:.1f}")

# 计算结果
if submit:
    prob, level, advice = predict_cholecystitis(age, gender, bmi, nlr, tg, hdl)

    st.markdown("---")
    st.subheader("📋 评估结果")
    st.metric("急性胆囊炎患病概率", f"{prob} %")
    st.success(f"风险等级：{level}")
    st.warning(f"诊疗建议：{advice}")

st.markdown("---")
st.caption("✅ 本工具永久在线，无需开机运行代码")