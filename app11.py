# 栖安｜家庭共建差异化版本 + 一键清空全部数据
# 区分个人 / 家庭模式：家庭共享积分池、家庭专属成就、成员贡献看板
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64

# ===================== 全局美化配置 | 绿白暖白可爱风格 =====================
st.set_page_config(
    page_title="🌿 栖安｜居家过敏健康守护系统",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS 暖白背景+绿色主题+可爱卡片圆角美化
st.markdown("""
<style>
/* 全局背景暖白色 */
.stApp {
    background-color: #fbfef9;
}
/* 标题绿色 */
h1,h2,h3,h4 {
    color: #2E8B57 !important;
    font-weight:600;
}
/* 卡片圆角 */
div.stCard {
    border-radius:16px !important;
    border:1px solid #e6f4ea !important;
}
/* 按钮绿色可爱 */
.stButton>button {
    background-color:#52b788 !important;
    color:white !important;
    border-radius:12px !important;
    border:none;
    padding:6px 20px;
}
.stButton>button:hover {
    background-color:#40916c !important;
}
/* 危险删除按钮单独样式 */
.danger-btn>button {
    background-color:#e63946 !important;
}
.danger-btn>button:hover {
    background-color:#c1121f !important;
}
/* 提示框美化 */
.stAlert {
    border-radius:14px !important;
}
/* 输入框圆角 */
.stTextInput>div>div>input {
    border-radius:10px;
}
.stSelectbox>div>div {
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

# ===================== 工具函数 =====================
def export_report(content, filename):
    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">📥 点击导出完整报告</a>'

# ===================== 全局状态初始化 =====================
# 会员权限
if "is_pro" not in st.session_state:
    st.session_state.is_pro = False

# ---- 个人数据 ----
if "user_score" not in st.session_state:
    st.session_state.user_score = 0
if "user_tree" not in st.session_state:
    st.session_state.user_tree = 0
if "continue_day" not in st.session_state:
    st.session_state.continue_day = 0
if "last_check_day" not in st.session_state:
    st.session_state.last_check_day = ""

# ---- 家庭共建数据（重点新增） ----
if "family_mode" not in st.session_state:
    st.session_state.family_mode = False
if "family_score" not in st.session_state:
    st.session_state.family_score = 0
if "family_tree" not in st.session_state:
    st.session_state.family_tree = 0
if "family_members" not in st.session_state:
    st.session_state.family_members = ["我"]
# 每个成员的打卡记录、积分贡献
if "member_contribution" not in st.session_state:
    st.session_state.member_contribution = {"我": {"score":0, "check_times":0}}
if "family_check_log" not in st.session_state:
    st.session_state.family_check_log = []
if "family_achievement_list" not in st.session_state:
    st.session_state.family_achievement_list = []

# 通用数据记录
if "eval_record" not in st.session_state:
    st.session_state.eval_record = []
if "check_record" not in st.session_state:
    st.session_state.check_record = []

# 个人成就系统
if "achievement_list" not in st.session_state:
    st.session_state.achievement_list = []
if "first_eval_flag" not in st.session_state:
    st.session_state.first_eval_flag = False
if "first_check_flag" not in st.session_state:
    st.session_state.first_check_flag = False
if "prev_risk_score" not in st.session_state:
    st.session_state.prev_risk_score = None

# Pro多成员档案
if "member_archive" not in st.session_state:
    st.session_state.member_archive = {}

# 反馈&问卷系统
if "user_feedback" not in st.session_state:
    st.session_state.user_feedback = []
if "monthly_questionnaire" not in st.session_state:
    st.session_state.monthly_questionnaire = []

# ===================== 侧边栏菜单 =====================
with st.sidebar:
    st.markdown("## 🌿 栖安·健康守护")
    st.markdown("<p style='color:#52b788'>🍃 栖于青绿，岁岁安澜</p>", unsafe_allow_html=True)
    st.divider()

    # 会员切换
    st.session_state.is_pro = st.toggle("💎 开启Pro高级会员", st.session_state.is_pro)
    if st.session_state.is_pro:
        st.success("✅ Pro特权：深度归因｜图表分析｜报告导出｜成员档案｜问卷权益")
    else:
        st.info("🔓 普通用户：基础评估｜打卡｜周报｜知识库｜反馈")

    st.divider()
    # 家庭/个人模式
    st.session_state.family_mode = st.toggle("👨‍👩‍👧 家庭共建模式", st.session_state.family_mode)
    if st.session_state.family_mode:
        st.markdown("### 🤝 家庭共建模式已开启")
        st.markdown(f"💚 家庭总积分：{st.session_state.family_score}")
        st.markdown(f"🌳 家庭守护树：{st.session_state.family_tree} 棵")
        st.markdown("📌 规则：任意成员打卡+5积分｜10积分=1棵共同守护树")
        st.info("💡 积分全家共享，一起种树解锁家庭专属成就！")
    else:
        st.markdown("### 👤 个人守护模式")
        st.markdown(f"💚 个人积分：{st.session_state.user_score}")
        st.markdown(f"🌳 个人守护树：{st.session_state.user_tree} 棵")
        st.markdown("📌 规则：本人打卡+5积分｜10积分=1棵守护树")

    st.divider()
    st.warning("🔒 隐私保障：所有敏感健康数据仅本地处理")
    st.info("🔌 硬件预留：适配温湿度、PM2.5、VOC、CO₂传感器接入")

    st.divider()
    # ========== 新增：一键删除全部数据 ==========
    st.markdown("### ⚠️ 危险操作区")
    confirm_del = st.checkbox("我确认要清空所有打卡、评估、积分、成就数据，不可恢复！")
    if confirm_del:
        with st.container():
            st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
            if st.button("🗑️ 一键清空全部数据"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ===================== 页面标签页 =====================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🏠 完整环境风险评估",
    "✅ 每日打卡·健康森林",
    "📄 健康记录报告",
    "📅 全员每周周报",
    "🔔 周期性健康提醒",
    "📖 全场景防护知识库",
    "💬 反馈建议&月度问卷",
    "👨‍👩‍👧 成员档案管理(Pro)"
])

# ===================== Tab1 完整环境风险评估录入 =====================
with tab1:
    st.header("🏠 全维度居家过敏风险专家评估")
    st.markdown("<p style='color:#52b788'>🍃 录入环境、生活习惯、身体状态，系统加权评估、自动归因预警</p>", unsafe_allow_html=True)

    data_source = st.radio("📡 数据采集方式", ["🖐️ 手动完整录入", "🔌 智能传感器自动接入（远期预留）"], horizontal=True)
    select_user = "我"
    if st.session_state.is_pro and len(st.session_state.family_members) > 0:
        select_user = st.selectbox("👤 本次记录归属成员", st.session_state.family_members)

    with st.form("full_assess_form"):
        col_left, col_right = st.columns(2)
        with col_left:
            scene_type = st.selectbox("📍 当前评估环境场景", ["卧室","浴室","客厅","宿舍","书房","办公室"])
            is_pet_home = st.selectbox("🐾 是否宠物饲养家庭", ["否","是"])
            have_rhinitis = st.selectbox("🤧 是否有过敏性鼻炎病史", ["否","是"])
            have_asthma = st.selectbox("🫁 是否有过敏性哮喘病史", ["否","是"])

            if data_source == "🔌 智能传感器自动接入（远期预留）":
                st.info("✅ 传感器字段已预留：温度/湿度/PM2.5/PM10/VOC/CO₂ 硬件可直接对接")
                temp, humi, pm25, pm10, voc, co2 = 24, 55, 35, 40, 0.4, 800
            else:
                temp = st.number_input("🌡️ 室内实时温度(℃)", min_value=0, max_value=45, value=24)
                humi = st.number_input("💧 室内相对湿度(%)", min_value=0, max_value=100, value=55)
                pm25 = st.number_input("🌫️ PM2.5数值(μg/m³)", min_value=0, max_value=500, value=35)
                pm10 = st.number_input("🌫️ PM10数值(μg/m³)", min_value=0, max_value=500, value=40)
                voc = st.number_input("🧪 VOC有害气体(mg/m³)", min_value=0.0, max_value=10.0, value=0.4)
                co2 = st.number_input("💨 CO₂浓度(ppm)", min_value=400, max_value=5000, value=800)

            bed_sun_day = st.number_input("🛏️ 距离上次被褥暴晒晾晒天数", min_value=0, value=7)
            room_close_hour = st.number_input("🪟 每日室内密闭不通风时长(小时)", min_value=0, max_value=24, value=8)

        with col_right:
            vent_frequency = st.number_input("🍃 每日开窗通风次数", min_value=0, max_value=10, value=2)
            clean_curtain_day = st.number_input("🧺 距离上次床帘/窗帘深度清洗天数", min_value=0, value=14)
            pollen_degree = st.selectbox("🌼 当地实时花粉等级", ["无","低","中","高","极高"])
            now_season = st.selectbox("🗓️ 当前所处季节", ["春季","夏季","秋季","冬季"])
            now_weather = st.selectbox("☁️ 今日户外天气状况", ["晴天","阴天","雨天","雾天","大风"])
            today_symptom = st.multiselect("😵 今日过敏不适症状",
                ["无不适","鼻痒打喷嚏","鼻塞流涕","咽痒干咳","胸闷喘息","眼痒流泪","皮肤瘙痒"],
                default=["无不适"])

        submit_assess = st.form_submit_button("🔍 启动专家模型·场景加权评估")

    if submit_assess:
        scene_weight_dict = {"卧室":1.25,"浴室":1.30,"客厅":1.10,"宿舍":1.15,"书房":1.00,"办公室":1.05}
        scene_weight = scene_weight_dict[scene_type]
        pet_weight = 1.15 if is_pet_home == "是" else 1.0

        mite_score = 0
        if 20 <= temp <= 28: mite_score += 20
        if humi >= 55: mite_score += 25
        if bed_sun_day >= 14: mite_score += 30
        if vent_frequency <= 1: mite_score += 15
        if room_close_hour >= 12: mite_score += 10

        mold_score = 0
        if humi >= 60: mold_score += 35
        if room_close_hour >= 12: mold_score += 25
        if vent_frequency <= 1: mold_score += 20
        if now_weather in ["雨天","雾天"]: mold_score += 20

        pollen_score_map = {"无":0,"低":15,"中":35,"高":60,"极高":80}
        pollen_score = pollen_score_map[pollen_degree]
        if now_season in ["春季","秋季"]: pollen_score += 15
        if now_weather == "大风": pollen_score += 10

        mite_score = round(mite_score * scene_weight * pet_weight, 1)
        mold_score = round(mold_score * scene_weight * pet_weight, 1)
        pollen_score = round(pollen_score * scene_weight * pet_weight, 1)

        body_susceptible = 0
        if have_rhinitis == "是": body_susceptible += 15
        if have_asthma == "是": body_susceptible += 20
        if "无不适" not in today_symptom: body_susceptible += 15

        total_risk = int(0.35*mite_score + 0.3*mold_score + 0.25*pollen_score + body_susceptible)

        def get_risk_level(score):
            if score < 30: return "🟢 低风险｜安全"
            elif score < 60: return "🟡 中风险｜需改善"
            else: return "🔴 高风险｜紧急预警"

        mite_level = get_risk_level(mite_score)
        mold_level = get_risk_level(mold_score)
        pollen_level = get_risk_level(pollen_score)
        total_level = get_risk_level(total_risk)

        reason_list = []
        if mite_score >= 60: reason_list.append("尘螨超标：温湿度适宜螨虫繁殖+被褥长期未晾晒+通风不足")
        if mold_score >= 60: reason_list.append("霉菌超标：室内湿度过高、密闭时间过长、阴雨雾天滋生加剧")
        if pollen_score >= 60: reason_list.append("花粉超标：户外花粉浓度高、春秋高发、大风带入室内")
        if have_rhinitis=="是" or have_asthma=="是": reason_list.append("体质易感：存在鼻炎/哮喘过敏基础病史")
        if "无不适" not in today_symptom: reason_list.append("症状佐证：当日已出现过敏不适反应")
        if scene_weight > 1.1: reason_list.append(f"场景加权：{scene_type}为过敏高风险场景")
        if is_pet_home == "是": reason_list.append("宠物致敏：皮屑、毛发增加室内过敏源")

        st.divider()
        st.subheader("📊 分项过敏风险评级｜专家加权结果")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("🛏️ 尘螨风险", mite_level, f"{mite_score} 分")
        c2.metric("🍄 霉菌风险", mold_level, f"{mold_score} 分")
        c3.metric("🌼 花粉风险", pollen_level, f"{pollen_score} 分")
        c4.metric("📌 综合风险", total_level, f"{total_risk} 分")

        if reason_list:
            st.info("🔍 智能自动归因：" + "；".join(reason_list))
        else:
            st.success("🔍 当前环境无明显致敏诱因，健康状态良好✅")

        st.subheader("🚨 高风险专项预警｜一对一整改方案")
        solve_tips = []
        if mite_score >= 60:
            solve_tips.append("🛏️【尘螨整改】55℃热水清洗床品，被褥暴晒4小时以上，减少毛绒布艺，控温湿度。")
        if mold_score >= 60:
            solve_tips.append("🍄【霉菌整改】及时通风擦干积水，阴雨天关窗除湿，湿度维持40%-55%。")
        if pollen_score >= 60:
            solve_tips.append("🌼【花粉整改】大风天花季关窗，外出做好防护，回家洗脸洗鼻换外衣。")

        if total_risk >= 60:
            st.error("🚨 综合高风险预警！极易诱发咳喘鼻炎，及时整改，不适尽快就医！")
        for tip in solve_tips:
            st.warning(tip)
        if not solve_tips:
            st.success("✅ 环境风险平稳！继续保持清洁通风晾晒习惯！")

        save_data = {
            "评估时间":datetime.now().strftime("%Y-%m-%d %H:%M"),
            "归属成员":select_user,
            "评估场景":scene_type,
            "宠物家庭":is_pet_home,
            "鼻炎病史":have_rhinitis,
            "哮喘病史":have_asthma,
            "当日症状":today_symptom,
            "温度":temp,
            "湿度":humi,
            "PM2.5":pm25,
            "PM10":pm10,
            "VOC":voc,
            "CO2":co2,
            "被褥晾晒天数":bed_sun_day,
            "每日密闭时长":room_close_hour,
            "每日通风次数":vent_frequency,
            "窗帘清洗天数":clean_curtain_day,
            "花粉等级":pollen_degree,
            "当前季节":now_season,
            "当日天气":now_weather,
            "尘螨得分":mite_score,
            "霉菌得分":mold_score,
            "花粉得分":pollen_score,
            "综合得分":total_risk,
            "风险等级":total_level,
            "风险归因":"；".join(reason_list) if reason_list else "无"
        }
        st.session_state.eval_record.append(save_data)
        if select_user not in st.session_state.member_archive:
            st.session_state.member_archive[select_user] = []
        st.session_state.member_archive[select_user].append(save_data)

        # 个人成就触发
        if not st.session_state.first_eval_flag:
            st.session_state.first_eval_flag = True
            st.session_state.achievement_list.append("📝 风险观察员｜首次完成专业评估")
            st.success("🏆 解锁成就：风险观察员！")
            st.balloons()
        if st.session_state.prev_risk_score is not None and total_risk < st.session_state.prev_risk_score:
            if "📉 渐入佳境｜健康风险持续下降" not in st.session_state.achievement_list:
                st.session_state.achievement_list.append("📉 渐入佳境｜健康风险持续下降")
                st.success("🏆 解锁高阶成就！环境健康度持续提升✨")
                st.balloons()
        st.session_state.prev_risk_score = total_risk

        # Pro深度归因报告
        if st.session_state.is_pro:
            st.divider()
            st.subheader("📄 Pro专属｜深度归因分析报告（可导出）")
            full_report = f"""
====== 栖安·深度过敏健康归因报告 ======
报告生成时间：{save_data['评估时间']}
评估成员：{select_user}
评估场景：{scene_type}｜场景加权系数：{scene_weight}
宠物家庭：{is_pet_home}

【个人过敏基础信息】
过敏性鼻炎：{have_rhinitis}
过敏性哮喘：{have_asthma}
当日身体不适：{"、".join(today_symptom)}

【完整环境监测数据】
室内温度：{temp}℃
室内湿度：{humi}%
PM2.5：{pm25}μg/m³
PM10：{pm10}μg/m³
VOC有害气体：{voc}mg/m³
CO₂浓度：{co2}ppm

【生活习惯完整记录】
被褥晾晒间隔天数：{bed_sun_day}天
窗帘床帘清洗间隔：{clean_curtain_day}天
每日密闭不通风时长：{room_close_hour}小时
每日开窗通风次数：{vent_frequency}次

【户外环境参数】
当前季节：{now_season}
当日天气：{now_weather}
花粉浓度等级：{pollen_degree}

【专家评分结果】
尘螨风险得分：{mite_score}｜{mite_level}
霉菌风险得分：{mold_score}｜{mold_level}
花粉风险得分：{pollen_score}｜{pollen_level}
综合过敏风险：{total_risk}｜{total_level}

【核心风险归因结论】
{save_data['风险归因']}

【长期专业防护建议】
1. 长期维持室内湿度40%-55%，从根源杜绝霉菌、螨虫滋生
2. 固定每周暴晒被褥、每月深度清洗布艺软装
3. 春秋花粉季、阴雨雾天严格做好封闭防护
4. 过敏体质坚持每日规律通风，减少密闭环境停留时长
5. 宠物家庭定期吸尘除毛，降低皮屑致敏风险
            """
            st.text_area("完整深度报告", full_report, height=380)
            st.markdown(export_report(full_report,f"栖安深度报告_{datetime.now().strftime('%Y%m%d')}.txt"), unsafe_allow_html=True)

            if len(st.session_state.eval_record)>=2:
                df_chart = pd.DataFrame(st.session_state.eval_record)
                fig_line = px.line(df_chart, x="评估时间", y="综合得分", title="📈 长期综合风险变化趋势", markers=True, color_discrete_sequence=["#52b788"])
                fig_pie = px.pie(values=[mite_score,mold_score,pollen_score,body_susceptible],
                                 names=["尘螨风险","霉菌风险","花粉风险","体质易感"],
                                 title="🥧 本次风险构成占比分析",
                                 color_discrete_sequence=["#74c69d","#52b788","#40916c","#2d6a4f"])
                st.plotly_chart(fig_line, use_container_width=True)
                st.plotly_chart(fig_pie, use_container_width=True)

# ===================== Tab2 每日打卡+健康森林+成就系统 =====================
with tab2:
    st.header("✅ 每日健康打卡 · 🌲 守护森林系统")
    if st.session_state.family_mode:
        st.markdown("<p style='color:#52b788'>🤝 当前：家庭共建模式｜任意成员打卡，全家共享积分种树，解锁家庭专属成就</p>", unsafe_allow_html=True)
        select_check_member = st.selectbox("👤 本次打卡成员", st.session_state.family_members)
    else:
        st.markdown("<p style='color:#52b788'>👤 当前：个人守护模式｜打卡积累个人积分，打造属于自己的健康森林</p>", unsafe_allow_html=True)
        select_check_member = "我"

    if st.button("🌿 立即打卡 +5积分"):
        today = datetime.now().strftime("%Y-%m-%d")
        if st.session_state.family_mode:
            # ========== 家庭打卡逻辑 ==========
            already_today = any(item["日期"] == today and item["成员"] == select_check_member for item in st.session_state.family_check_log)
            if already_today:
                st.info(f"💤 {select_check_member} 今天已经打卡啦！")
            else:
                st.balloons()
                st.session_state.family_check_log.append({"日期":today, "成员":select_check_member})
                st.session_state.family_score +=5
                st.session_state.member_contribution[select_check_member]["score"] +=5
                st.session_state.member_contribution[select_check_member]["check_times"] +=1
                new_tree = st.session_state.family_score //10
                add_tree = new_tree - st.session_state.family_tree
                st.session_state.family_tree = new_tree

                st.success(f"✅ {select_check_member}打卡成功！家庭积分+5")
                if add_tree>0:
                    st.success(f"🎉 全家共同种下 {add_tree} 棵守护树🌳")
                    st.balloons()

                # -------- 家庭专属成就解锁 --------
                if "🤍 阖家启新｜家庭第一签" not in st.session_state.family_achievement_list:
                    st.session_state.family_achievement_list.append("🤍 阖家启新｜家庭第一签")
                    st.success("🏆 解锁家庭成就：阖家启新！")
                    st.balloons()
                family_total_check = len(st.session_state.family_check_log)
                if family_total_check >=7 and "📅 同心七日｜全家累计打卡7次" not in st.session_state.family_achievement_list:
                    st.session_state.family_achievement_list.append("📅 同心七日｜全家累计打卡7次")
                    st.success("🏆 解锁家庭成就：同心七日！")
                    st.balloons()
                if st.session_state.family_tree >=10 and "🌲 草木同生｜家庭种下第10棵树" not in st.session_state.family_achievement_list:
                    st.session_state.family_achievement_list.append("🌲 草木同生｜家庭种下第10棵树")
                    st.success("🏆 解锁家庭成就：草木同生！")
                    st.balloons()

        else:
            # ========== 个人打卡逻辑 ==========
            if st.session_state.last_check_day == today:
                st.info("💤 今日已打卡！坚持守护健康～")
            else:
                st.balloons()
                st.session_state.last_check_day = today
                st.session_state.continue_day +=1
                st.session_state.check_record.append({"日期":today})
                st.session_state.user_score +=5
                new_tree = st.session_state.user_score //10
                add_tree = new_tree - st.session_state.user_tree
                st.session_state.user_tree = new_tree

                st.success(f"✅ 打卡成功！连续打卡：{st.session_state.continue_day} 天")
                if add_tree>0:
                    st.success(f"🎉 新增 {add_tree} 棵守护树🌳")
                    st.balloons()

                if not st.session_state.first_check_flag:
                    st.session_state.first_check_flag = True
                    st.session_state.achievement_list.append("🌱 初心启航｜首次健康打卡")
                    st.success("🏆 解锁成就：初心启航！")
                    st.balloons()
                if st.session_state.continue_day ==7 and "📅 七日自律｜连续打卡7天" not in st.session_state.achievement_list:
                    st.session_state.achievement_list.append("📅 七日自律｜连续打卡7天")
                    st.success("🏆 解锁成就：七日自律！")
                    st.balloons()
                if st.session_state.continue_day ==14 and "🤍 半月坚守｜连续打卡14天" not in st.session_state.achievement_list:
                    st.session_state.achievement_list.append("🤍 半月坚守｜连续打卡14天")
                    st.success("🏆 解锁成就：半月坚守！")
                    st.balloons()

    st.divider()
    # -------- 看板区分展示 --------
    if st.session_state.family_mode:
        st.subheader("🏠 家庭守护看板")
        df_contri = pd.DataFrame([
            {"成员":k, "贡献积分":v["score"], "打卡次数":v["check_times"]}
            for k,v in st.session_state.member_contribution.items()
        ])
        st.dataframe(df_contri, use_container_width=True)
        if len(df_contri)>0:
            top_member = df_contri.sort_values("打卡次数", ascending=False).iloc[0]["成员"]
            st.info(f"⭐ 当前家庭守护之星：{top_member}")

        st.subheader("🏅 家庭专属成就")
        if st.session_state.family_achievement_list:
            for a in st.session_state.family_achievement_list:
                st.success(a)
        else:
            st.info("✨ 还没有家庭成就，快来第一个打卡！")

    else:
        st.subheader("🏅 我的个人成就勋章")
        if st.session_state.achievement_list:
            for a in st.session_state.achievement_list:
                st.success(a)
        else:
            st.info("✨ 暂无成就，打卡、评估解锁勋章！")

# ===================== Tab3 健康记录报告 =====================
with tab3:
    st.header("📄 个人&家庭健康记录总报告")
    st.markdown("<p style='color:#52b788'>普通用户查看记录｜Pro会员解锁长期趋势分析</p>", unsafe_allow_html=True)
    if len(st.session_state.eval_record) ==0:
        st.info("🍃 暂无评估记录，前往【环境风险评估】完成首次检测！")
    else:
        df_all = pd.DataFrame(st.session_state.eval_record)
        st.dataframe(df_all, use_container_width=True)

# ===================== Tab4 每周健康周报 =====================
with tab4:
    st.header("📅 全员通用｜每周健康周报")
    st.markdown("<p style='color:#52b788'>所有用户均可生成周报｜Pro会员专属可视化图表</p>", unsafe_allow_html=True)
    if len(st.session_state.eval_record)==0 and len(st.session_state.check_record)==0 and len(st.session_state.family_check_log)==0:
        st.info("暂无打卡与评估数据，持续使用生成周报✨")
    else:
        st.subheader("📋 本周健康总结")
        if st.session_state.family_mode:
            st.write(f"✅ 家庭累计打卡次数：{len(st.session_state.family_check_log)}")
            st.write(f"🌳 家庭总树木：{st.session_state.family_tree}")
        else:
            st.write(f"✅ 个人累计打卡次数：{len(st.session_state.check_record)}")
            st.write(f"🔥 当前连续守护天数：{st.session_state.continue_day} 天")
        st.write(f"📊 评估记录总数：{len(st.session_state.eval_record)}")
        if len(st.session_state.eval_record)>0:
            last_data = st.session_state.eval_record[-1]
            st.write(f"⚠️ 最新环境风险等级：{last_data['风险等级']}")
            st.write(f"🔍 核心健康归因：{last_data['风险归因']}")

# ===================== Tab5 周期性健康提醒 =====================
with tab5:
    st.header("🔔 周期性智能健康提醒")
    st.markdown("<p style='color:#52b788'>定时提醒清洁、通风、晾晒、防护，维持低敏环境🍃</p>", unsafe_allow_html=True)
    remind = [
        "🛏️【每周必做】被褥、枕芯阳光暴晒4小时以上，深度除螨",
        "🧺【每两周必做】清洗床帘、窗帘、沙发套、抱枕套布艺软装",
        "🍃【每日必做】早晚对流通风各20分钟，置换室内浊气",
        "🌼【花粉季】大风天紧闭门窗，外出做好防护，进门洗鼻洗脸换衣物",
        "💧【梅雨季/雨天】开启除湿，严控湿度40%-55%防霉",
        "🐾【宠物家庭】每周全屋吸尘，清理毛发皮屑",
        "🩺【过敏体质】持续咳喘、胸闷立刻离开致敏环境并就医"
    ]
    for r in remind:
        st.info(r)

# ===================== Tab6 全场景知识库 =====================
with tab6:
    st.header("📖 全场景过敏防护超级知识库")
    kb_select = st.selectbox("选择场景查看方案", ["新房除醛净化","卧室防螨养护","浴室防霉抑菌","宿舍低敏管理","办公室防护","春秋花粉抗敏","宠物家庭脱敏"])
    if kb_select == "新房除醛净化":
        st.subheader("🏠 新房除醛&有害气体全方位防护方案")
        st.write("新房甲醛、苯、TVOC诱发鼻炎干咳哮喘，释放周期3-15年，高温高湿加速挥发。优先高温密闭+开窗循环通风，优先ENF实木家具，搭配带分解滤网净化器。")
    elif kb_select == "卧室防螨养护":
        st.subheader("🛏️ 卧室尘螨终极防控方案")
        st.write("尘螨是鼻炎头号过敏源，20-28℃湿度>55%疯狂繁殖。床品每周55℃热水清洗，被褥暴晒拍打，精简毛绒软装，控湿40%-50%。")
    elif kb_select == "浴室防霉抑菌":
        st.subheader("🍄 浴室霉菌治理方案")
        st.write("潮湿密闭滋生霉菌孢子，诱发咽痛咳喘。洗完澡排风开门，擦干积水，定期清洁瓷砖缝隙，霉斑及时清理。")
    elif kb_select == "宿舍低敏管理":
        st.subheader("🎒 学生宿舍低敏防护方案")
        st.write("宿舍通风差、晾晒难。每日开窗通风，被褥密封收纳，减少挂布玩偶，阴雨天注意除湿。")
    elif kb_select == "办公室防护":
        st.subheader("💻 办公室过敏防护方案")
        st.write("空调滤网、地毯粉尘是隐患。定期清洗滤网，工位除尘，减少堆积纸质文件，定时透气。")
    elif kb_select == "春秋花粉抗敏":
        st.subheader("🌼 春秋季花粉强效抗敏方案")
        st.write("大风晴天花粉浓度最高，关好门窗，外出佩戴口罩护目镜，回家换衣洗脸洗鼻。")
    elif kb_select == "宠物家庭脱敏":
        st.subheader("🐱 宠物家庭低敏养护方案")
        st.write("致敏源是皮屑唾液，不是毛发。定期吸尘梳毛，禁止宠物上床沙发，保持通风干燥。")

# ===================== Tab7 反馈建议&月度问卷系统 =====================
with tab7:
    st.header("💬 用户反馈｜月度专属问卷调查")
    st.markdown("<p style='color:#52b788'>提交建议，持续迭代✨</p>", unsafe_allow_html=True)
    feedback_text = st.text_area("功能建议、bug反馈：", height=120)
    if st.button("✅ 提交反馈"):
        if feedback_text.strip()!="":
            st.session_state.user_feedback.append({"时间":datetime.now().strftime("%Y-%m-%d %H:%M"),"内容":feedback_text})
            st.success("🎉 反馈提交成功！")
            st.balloons()
        else:
            st.warning("请输入反馈内容！")
    st.divider()
    st.subheader("📋 月度用户体验问卷（Pro&活跃用户）")
    if st.session_state.is_pro or len(st.session_state.eval_record)>=3:
        q1 = st.radio("1. 整体满意度？", ["非常满意","满意","一般","不满意"])
        q2 = st.radio("2. 最常用功能？", ["环境风险评估","打卡森林","周报","知识库","提醒"])
        q3 = st.text_input("3. 想要新增功能：")
        q4 = st.radio("4. 是否持续使用？", ["一定会","偶尔会","不确定"])
        if st.button("📩 提交问卷"):
            st.session_state.monthly_questionnaire.append({
                "时间":datetime.now().strftime("%Y-%m-%d"),
                "满意度":q1,
                "常用功能":q2,
                "新增需求":q3,
                "持续使用":q4
            })
            st.success("✅ 问卷提交完成！感谢你的反馈🥰")
            st.balloons()
    else:
        st.info("🔒 完成3次评估或开通Pro会员即可填写月度问卷")

# ===================== Tab8 成员档案管理(Pro) =====================
with tab8:
    st.header("👨‍👩‍👧 家庭成员档案管理（Pro专属）")
    if not st.session_state.is_pro:
        st.info("🔒 开通Pro会员解锁成员管理，添加、管理家庭成员，分开记录健康档案")
    else:
        new_member = st.text_input("➕ 添加新家庭成员名字")
        if st.button("添加成员"):
            if new_member.strip() and new_member not in st.session_state.family_members:
                st.session_state.family_members.append(new_member.strip())
                st.session_state.member_contribution[new_member.strip()] = {"score":0, "check_times":0}
                st.success(f"✅ 成员【{new_member.strip()}】添加成功！")
            elif new_member in st.session_state.family_members:
                st.warning("该成员已经存在！")
        st.divider()
        st.subheader("📋 当前家庭成员列表")
        st.write(st.session_state.family_members)
