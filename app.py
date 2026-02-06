import streamlit as st
import json
import pandas as pd
from datetime import datetime
import requests
import re

# ========== 페이지 설정 ==========
st.set_page_config(
    page_title="AI중심대학 자가진단",
    page_icon="🎯",
    layout="wide"
)

# ========== 질문 데이터 ==========
SECTIONS = [
    {"id": 1, "title": "총장 직속 AI 거버넌스", "total": 25, "questions": [
        {"code": "q1_1", "text": "총장 직속 AI 총괄조직(예: AI융합교육원)이 있습니까?", "points": 6},
        {"code": "q1_2", "text": "위 조직이 단과대·학과를 조정할 실질적 권한이 있습니까?", "points": 6},
        {"code": "q1_3", "text": "일회성 TF가 아닌 상설 조직입니까?", "points": 5},
        {"code": "q1_4", "text": "산업체가 참여하는 교과과정혁신위원회가 있습니까?", "points": 5},
        {"code": "q1_5", "text": "위원회가 정기적으로 운영되고 환류체계가 있습니까?", "points": 3},
    ]},
    {"id": 2, "title": "학부·대학원 교육체계", "total": 25, "questions": [
        {"code": "q2_1", "text": "AI 학과/학부/단과대가 있거나 3년 내 신설 예정입니까?", "points": 6},
        {"code": "q2_2", "text": "전교생 AI 기초교육이 교양필수로 의무화되어 있습니까?", "points": 5},
        {"code": "q2_3", "text": "비전공자용 AI융합교육(연계전공, 복수전공)이 있습니까?", "points": 5},
        {"code": "q2_4", "text": "학·석사 연계(패스트트랙)가 40명 이상 운영 가능합니까?", "points": 5},
        {"code": "q2_5", "text": "브릿지 교과목(타전공+AI 연계)이 개발되어 있습니까?", "points": 4},
    ]},
    {"id": 3, "title": "제도화 가능성", "total": 20, "questions": [
        {"code": "q3_1", "text": "AI교육 관련 사항이 학칙에 반영되어 있습니까?", "points": 5},
        {"code": "q3_2", "text": "산업체 재직자 겸직교원 임용제도가 학칙에 있습니까?", "points": 5},
        {"code": "q3_3", "text": "교원 평가에 AI 교육성과가 반영됩니까?", "points": 4},
        {"code": "q3_4", "text": "AI 실습용 토큰 지원 예산이 확보되어 있습니까?", "points": 4},
        {"code": "q3_5", "text": "'시범'이 아닌 '정규 제도'로 운영 중입니까?", "points": 2},
    ]},
    {"id": 4, "title": "산업 연계의 현실성", "total": 15, "questions": [
        {"code": "q4_1", "text": "실질적으로 협력 중인 AI 기업 파트너가 있습니까?", "points": 4},
        {"code": "q4_2", "text": "산학협력 PBL이 졸업요건으로 필수화되어 있습니까?", "points": 4},
        {"code": "q4_3", "text": "산업계 멘토가 프로젝트에 실제 참여하고 있습니까?", "points": 3},
        {"code": "q4_4", "text": "계약학과 또는 채용연계형 프로그램이 있습니까?", "points": 2},
        {"code": "q4_5", "text": "MOU가 아닌 실질적 협력(공동R&D, 인턴십)입니까?", "points": 2},
    ]},
    {"id": 5, "title": "대학 특성화 논리", "total": 10, "questions": [
        {"code": "q5_1", "text": "대학 강점 분야와 AI의 결합 논리가 명확합니까?", "points": 3},
        {"code": "q5_2", "text": "지역 산업과의 연계 계획이 구체적입니까?", "points": 3},
        {"code": "q5_3", "text": "다른 대학과 차별화된 특성화 전략이 있습니까?", "points": 2},
        {"code": "q5_4", "text": "'왜 우리 대학인가'에 대한 명확한 답이 있습니까?", "points": 2},
    ]},
    {"id": 6, "title": "확산·부가 프로그램", "total": 5, "questions": [
        {"code": "q6_1", "text": "타 대학·지역사회 대상 AI교육 확산 계획이 있습니까?", "points": 2},
        {"code": "q6_2", "text": "AI 교육콘텐츠 외부 공유 계획이 있습니까?", "points": 1},
        {"code": "q6_3", "text": "고교생 AI교육 연계 프로그램이 있습니까?", "points": 1},
        {"code": "q6_4", "text": "해외 대학 AI교육 교류 계획이 있습니까?", "points": 1},
    ]},
]

BUDGET_QUESTIONS = [
    {"code": "qb_1", "text": "기관부담금 10% (연 약 3억원) 현금 매칭이 가능합니까?"},
    {"code": "qb_2", "text": "예비창업지원금 별도 재원 마련이 가능합니까?"},
]

# ========== 세션 상태 초기화 ==========
if 'ai_evaluations' not in st.session_state:
    st.session_state.ai_evaluations = {}

# ========== API 키 가져오기 ==========
def get_openai_key():
    try:
        return st.secrets["OPENAI_API_KEY"]
    except:
        return None

# ========== AI 평가 함수 ==========
def evaluate_with_ai(question_text, plan_content):
    api_key = get_openai_key()
    if not api_key or not plan_content:
        return {"score": 0.5, "comment": "AI 평가 불가"}
    
    prompt = f"""당신은 AI중심대학 사업 신청서를 평가하는 전문가입니다.

[평가 항목]
{question_text}

[대학이 제출한 계획]
{plan_content}

[평가 기준]
- 구체성: 실행 계획이 구체적인가?
- 실현가능성: 현실적으로 달성 가능한가?
- 적절성: 평가 항목의 요구사항을 충족하는가?

[응답 형식 - 반드시 이 형식으로]
점수: 0.XX
평가: (한 줄 평가)

점수는 0.00~1.00 사이 (0.9이상:매우우수, 0.7~0.9:우수, 0.5~0.7:보통, 0.3~0.5:미흡, 0.3미만:매우미흡)"""

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200,
                "temperature": 0.3
            },
            timeout=30
        )
        
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            
            score = 0.5
            score_match = re.search(r'점수[:\s]*([0-9.]+)', content)
            if score_match:
                score = float(score_match.group(1))
                if score > 1:
                    score = score / 100
                score = max(0, min(1, score))
            
            comment_match = re.search(r'평가[:\s]*(.+)', content, re.DOTALL)
            comment = comment_match.group(1).strip() if comment_match else content.strip()
            
            return {"score": score, "comment": comment}
    except Exception as e:
        return {"score": 0.5, "comment": f"평가 오류: {str(e)}"}
    
    return {"score": 0.5, "comment": "AI 평가 실패"}

# ========== 점수 계산 ==========
def calculate_scores():
    section_scores = {}
    total = 0
    
    for section in SECTIONS:
        section_score = 0
        for q in section["questions"]:
            code = q["code"]
            radio_key = f"radio_{code}"
            if radio_key in st.session_state:
                selected = st.session_state[radio_key]
                if "있음" in selected and "계획" not in selected:
                    value = 1
                elif "계획있음" in selected:
                    value = 0.5
                else:
                    value = 0
                
                if value == 1:
                    section_score += q["points"]
                elif value == 0.5:
                    ai_score = st.session_state.ai_evaluations.get(code, {}).get("score", 0.5)
                    section_score += q["points"] * ai_score
        
        section_scores[section["id"]] = int(round(section_score))
        total += section_score
    
    return section_scores, int(round(total))

def get_grade(score):
    if score >= 85:
        return "A", "선정 가능성 높음", "#27ae60"
    elif score >= 70:
        return "B", "보완 후 도전 가능", "#3498db"
    elif score >= 55:
        return "C", "상당한 준비 필요", "#f39c12"
    elif score >= 40:
        return "D", "기반 구축 필요", "#e67e22"
    elif score > 0:
        return "F", "재검토 권고", "#e74c3c"
    else:
        return "-", "응답을 시작하세요", "#95a5a6"

# ========== 데이터 수집 ==========
def get_all_responses():
    responses = {}
    plans = {}
    
    for section in SECTIONS:
        for q in section["questions"]:
            code = q["code"]
            radio_key = f"radio_{code}"
            plan_key = f"plan_{code}"
            
            if radio_key in st.session_state:
                selected = st.session_state[radio_key]
                if "있음" in selected and "계획" not in selected:
                    responses[code] = 1
                elif "계획있음" in selected:
                    responses[code] = 0.5
                else:
                    responses[code] = 0
            
            if plan_key in st.session_state and st.session_state[plan_key]:
                plans[code] = st.session_state[plan_key]
    
    for q in BUDGET_QUESTIONS:
        code = q["code"]
        radio_key = f"radio_{code}"
        plan_key = f"plan_{code}"
        
        if radio_key in st.session_state:
            selected = st.session_state[radio_key]
            if selected == "가능":
                responses[code] = 1
            elif selected == "확보 중":
                responses[code] = 0.5
            else:
                responses[code] = 0
        
        if plan_key in st.session_state and st.session_state[plan_key]:
            plans[code] = st.session_state[plan_key]
    
    return responses, plans

# ========== JSON 내보내기 ==========
def export_to_json(university_name, respondent_info):
    responses, plans = get_all_responses()
    section_scores, total_score = calculate_scores()
    grade, _, _ = get_grade(total_score)
    
    data = {
        "university_name": university_name,
        "respondent_info": respondent_info,
        "responses": responses,
        "plans": plans,
        "ai_evaluations": st.session_state.ai_evaluations,
        "section_scores": section_scores,
        "total_score": total_score,
        "grade": grade,
        "saved_at": datetime.now().isoformat()
    }
    
    return json.dumps(data, ensure_ascii=False, indent=2)

# ========== 엑셀 데이터 ==========
def create_excel_data(university_name):
    responses, plans = get_all_responses()
    section_scores, total_score = calculate_scores()
    grade, _, _ = get_grade(total_score)
    
    rows = []
    for section in SECTIONS:
        for q in section["questions"]:
            code = q["code"]
            value = responses.get(code, 0)
            
            if value == 1:
                answer = "있음"
                earned = q["points"]
            elif value == 0.5:
                answer = "계획있음"
                ai_score = st.session_state.ai_evaluations.get(code, {}).get("score", 0.5)
                earned = round(q["points"] * ai_score, 1)
            else:
                answer = "없음"
                earned = 0
            
            plan_content = plans.get(code, "")
            ai_eval = st.session_state.ai_evaluations.get(code, {})
            ai_score_display = f"{round(ai_eval.get('score', 0) * 100)}%" if ai_eval else "-"
            ai_comment = ai_eval.get("comment", "-") if ai_eval else "-"
            
            rows.append({
                "영역": f"{section['id']}. {section['title']}",
                "항목": q["text"],
                "응답": answer,
                "배점": q["points"],
                "획득점수": earned,
                "계획내용": plan_content,
                "AI점수": ai_score_display,
                "AI평가의견": ai_comment
            })
    
    for q in BUDGET_QUESTIONS:
        code = q["code"]
        value = responses.get(code, 0)
        answer = "가능" if value == 1 else ("확보중" if value == 0.5 else "불가능")
        
        rows.append({
            "영역": "※ 예산",
            "항목": q["text"],
            "응답": answer,
            "배점": "필수",
            "획득점수": "-",
            "계획내용": plans.get(code, ""),
            "AI점수": "-",
            "AI평가의견": "-"
        })
    
    return pd.DataFrame(rows), total_score, grade

# ==========================================
# UI 시작
# ==========================================

st.title("🎯 AI중심대학 준비도 자가진단")
st.markdown("**2026년 AI중심대학 사업 신청을 위한 우리 대학의 준비 현황을 점검합니다**")

# API 상태
if get_openai_key():
    st.success("✅ OpenAI API 연결됨 - AI 평가 가능")
else:
    st.warning("⚠️ OpenAI API 미설정 - '계획있음' 선택 시 50% 고정 점수 적용")

st.divider()

# ========== 점수판 (테이블 형식) ==========
section_scores, total_score = calculate_scores()
grade, grade_desc, grade_color = get_grade(total_score)

col_total, col_table, col_grade = st.columns([1, 3, 1])

with col_total:
    st.markdown(f"""
    <div style="text-align:center; padding:20px;">
        <div style="font-size:4em; font-weight:bold; color:#667eea;">{total_score}</div>
        <div style="font-size:1.2em; color:#666;">/ 100점</div>
    </div>
    """, unsafe_allow_html=True)

with col_table:
    # 세부 점수를 데이터프레임으로 표시
    score_df = pd.DataFrame({
        "영역": ["거버넌스", "교육체계", "제도화", "산업연계", "특성화", "확산"],
        "획득": [section_scores.get(i, 0) for i in range(1, 7)],
        "만점": [25, 25, 20, 15, 10, 5]
    })
    st.dataframe(
        score_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "영역": st.column_config.TextColumn("영역", width="medium"),
            "획득": st.column_config.NumberColumn("획득", format="%d점"),
            "만점": st.column_config.NumberColumn("만점", format="%d점"),
        }
    )

with col_grade:
    st.markdown(f"""
    <div style="background:{grade_color}; color:white; padding:30px 20px; border-radius:15px; text-align:center; height:100%;">
        <div style="font-size:3em; font-weight:bold;">{grade}</div>
        <div style="font-size:0.9em; margin-top:10px;">{grade_desc}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ========== 대학 정보 ==========
col_uni1, col_uni2 = st.columns(2)
with col_uni1:
    university_name = st.text_input("📍 대학명 *", key="university_name")
with col_uni2:
    respondent_info = st.text_input("👤 응답자 정보 (선택)", key="respondent_info")

# ========== 기존 데이터 불러오기 ==========
with st.expander("📂 기존 데이터 불러오기 (JSON 파일)"):
    uploaded_file = st.file_uploader("JSON 파일 선택", type=['json'], label_visibility="collapsed")
    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
            st.session_state.ai_evaluations = data.get("ai_evaluations", {})
            st.success(f"✅ 불러오기 완료! ({data.get('university_name', '')} - {data.get('total_score', 0)}점)")
            st.info("⚠️ 응답 데이터를 적용하려면 페이지를 새로고침 후 다시 불러오세요")
        except Exception as e:
            st.error(f"파일 읽기 오류: {e}")

st.divider()

# ========== 질문 섹션 ==========
for section in SECTIONS:
    with st.expander(f"**{section['id']}. {section['title']}** ({section['total']}점)", expanded=True):
        for q in section["questions"]:
            st.markdown(f"**{q['text']}** `{q['points']}점`")
            
            options = ["없음 (0점)", "계획있음 (AI평가)", f"있음 ({q['points']}점)"]
            
            selected = st.radio(
                f"응답_{q['code']}",
                options,
                index=0,
                key=f"radio_{q['code']}",
                label_visibility="collapsed",
                horizontal=True
            )
            
            # "계획있음" 선택 시 계획 입력란 표시
            if "계획있음" in selected:
                st.text_area(
                    "📝 계획 내용을 입력하세요 (AI가 평가합니다)",
                    key=f"plan_{q['code']}",
                    height=100,
                    placeholder="구체적인 추진 계획을 작성하세요..."
                )
                
                # AI 평가 결과 표시
                if q["code"] in st.session_state.ai_evaluations:
                    ai_eval = st.session_state.ai_evaluations[q["code"]]
                    st.info(f"🤖 **AI 평가: {round(ai_eval['score']*100)}%** - {ai_eval['comment']}")
            
            st.markdown("---")

# ========== 예산 섹션 ==========
with st.expander("**※ 예산 (필수 확인)**", expanded=True):
    for q in BUDGET_QUESTIONS:
        st.markdown(f"**{q['text']}** `🔴 필수`")
        
        options = ["불가능", "확보 중", "가능"]
        
        selected = st.radio(
            f"응답_{q['code']}",
            options,
            index=0,
            key=f"radio_{q['code']}",
            label_visibility="collapsed",
            horizontal=True
        )
        
        if selected == "확보 중":
            st.text_area(
                "📝 확보 계획을 입력하세요",
                key=f"plan_{q['code']}",
                height=100,
                placeholder="예산 확보 계획을 작성하세요..."
            )
        
        st.markdown("---")

st.divider()

# ========== 액션 버튼 ==========
col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

with col_btn1:
    if st.button("🔄 초기화", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

with col_btn2:
    if st.button("🤖 AI 평가 실행", use_container_width=True, type="primary"):
        if not get_openai_key():
            st.error("OpenAI API Key가 설정되지 않았습니다")
        else:
            responses, plans = get_all_responses()
            
            plans_to_evaluate = [
                code for code, value in responses.items()
                if value == 0.5 and plans.get(code)
            ]
            
            if plans_to_evaluate:
                progress = st.progress(0)
                status = st.empty()
                
                for i, code in enumerate(plans_to_evaluate):
                    status.text(f"평가 중... ({i+1}/{len(plans_to_evaluate)})")
                    
                    q_text = code
                    for section in SECTIONS:
                        for q in section["questions"]:
                            if q["code"] == code:
                                q_text = q["text"]
                                break
                    for q in BUDGET_QUESTIONS:
                        if q["code"] == code:
                            q_text = q["text"]
                    
                    result = evaluate_with_ai(q_text, plans[code])
                    st.session_state.ai_evaluations[code] = result
                    progress.progress((i + 1) / len(plans_to_evaluate))
                
                st.success(f"✅ AI 평가 완료! ({len(plans_to_evaluate)}개 항목)")
                st.rerun()
            else:
                st.warning("평가할 항목이 없습니다. '계획있음' 선택 후 계획을 입력하세요.")

with col_btn3:
    json_data = export_to_json(university_name or "대학", respondent_info or "")
    st.download_button(
        "💾 JSON 저장",
        json_data,
        f"{university_name or '대학'}_자가진단_{datetime.now().strftime('%Y%m%d')}.json",
        "application/json",
        use_container_width=True
    )

with col_btn4:
    df, total, grade = create_excel_data(university_name or "대학")
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        "📥 엑셀 다운로드",
        csv,
        f"{university_name or '대학'}_자가진단_{datetime.now().strftime('%Y%m%d')}.csv",
        "text/csv",
        use_container_width=True
    )

# ========== Footer ==========
st.divider()
st.markdown("""
<div style="text-align:center; color:#666; font-size:0.9em;">
    <p>💡 사용법: "계획있음" 선택 → 계획 작성 → "AI 평가 실행" 클릭</p>
    <p>💾 JSON 저장 후 나중에 다시 불러올 수 있습니다</p>
</div>
""", unsafe_allow_html=True)
