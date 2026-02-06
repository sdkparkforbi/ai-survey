import streamlit as st
import json
import pandas as pd
from datetime import datetime
import requests
import io

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
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'plans' not in st.session_state:
    st.session_state.plans = {}
if 'ai_evaluations' not in st.session_state:
    st.session_state.ai_evaluations = {}
if 'gist_id' not in st.session_state:
    st.session_state.gist_id = ""

# ========== API 키 가져오기 ==========
def get_openai_key():
    try:
        return st.secrets["OPENAI_API_KEY"]
    except:
        return None

def get_github_token():
    try:
        return st.secrets["GITHUB_TOKEN"]
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
            
            # 점수 파싱
            import re
            score = 0.5
            score_match = re.search(r'점수[:\s]*([0-9.]+)', content)
            if score_match:
                score = float(score_match.group(1))
                if score > 1:
                    score = score / 100
                score = max(0, min(1, score))
            
            # 평가 의견 파싱
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
            value = st.session_state.responses.get(code, 0)
            
            if value == 1:
                section_score += q["points"]
            elif value == 0.5:
                ai_score = st.session_state.ai_evaluations.get(code, {}).get("score", 0.5)
                section_score += q["points"] * ai_score
        
        section_scores[section["id"]] = round(section_score, 1)
        total += section_score
    
    return section_scores, round(total, 1)

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

# ========== GitHub Gist 저장/불러오기 ==========
def save_to_gist(university_name, respondent_info):
    token = get_github_token()
    if not token:
        return False, "GitHub Token이 설정되지 않았습니다"
    
    section_scores, total_score = calculate_scores()
    grade, _, _ = get_grade(total_score)
    
    data = {
        "university_name": university_name,
        "respondent_info": respondent_info,
        "responses": st.session_state.responses,
        "plans": st.session_state.plans,
        "ai_evaluations": st.session_state.ai_evaluations,
        "section_scores": section_scores,
        "total_score": total_score,
        "grade": grade,
        "saved_at": datetime.now().isoformat()
    }
    
    filename = f"ai_survey_{university_name.replace(' ', '_')}.json"
    gist_data = {
        "description": f"AI중심대학 자가진단 - {university_name}",
        "public": False,
        "files": {filename: {"content": json.dumps(data, ensure_ascii=False, indent=2)}}
    }
    
    try:
        if st.session_state.gist_id:
            response = requests.patch(
                f"https://api.github.com/gists/{st.session_state.gist_id}",
                headers={"Authorization": f"token {token}"},
                json=gist_data
            )
        else:
            response = requests.post(
                "https://api.github.com/gists",
                headers={"Authorization": f"token {token}"},
                json=gist_data
            )
        
        if response.status_code in [200, 201]:
            result = response.json()
            st.session_state.gist_id = result["id"]
            return True, f"저장 완료! Gist ID: {result['id']}"
        else:
            return False, f"저장 실패: {response.json().get('message', '알 수 없는 오류')}"
    except Exception as e:
        return False, f"오류: {str(e)}"

def load_from_gist(gist_id):
    token = get_github_token()
    if not token:
        return False, "GitHub Token이 설정되지 않았습니다"
    
    try:
        response = requests.get(
            f"https://api.github.com/gists/{gist_id}",
            headers={"Authorization": f"token {token}"}
        )
        
        if response.status_code == 200:
            gist = response.json()
            files = list(gist["files"].values())
            if files:
                data = json.loads(files[0]["content"])
                st.session_state.responses = data.get("responses", {})
                st.session_state.plans = data.get("plans", {})
                st.session_state.ai_evaluations = data.get("ai_evaluations", {})
                st.session_state.gist_id = gist_id
                return True, data
        return False, "Gist를 찾을 수 없습니다"
    except Exception as e:
        return False, f"오류: {str(e)}"

# ========== 엑셀 다운로드 ==========
def create_excel_data(university_name):
    section_scores, total_score = calculate_scores()
    grade, _, _ = get_grade(total_score)
    
    rows = []
    for section in SECTIONS:
        for q in section["questions"]:
            code = q["code"]
            value = st.session_state.responses.get(code, 0)
            
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
            
            plan_content = st.session_state.plans.get(code, "")
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
    
    # 예산 항목
    for q in BUDGET_QUESTIONS:
        code = q["code"]
        value = st.session_state.responses.get(code, 0)
        answer = "가능" if value == 1 else ("확보중" if value == 0.5 else "불가능")
        
        rows.append({
            "영역": "※ 예산",
            "항목": q["text"],
            "응답": answer,
            "배점": "필수",
            "획득점수": "-",
            "계획내용": st.session_state.plans.get(code, ""),
            "AI점수": "-",
            "AI평가의견": "-"
        })
    
    return pd.DataFrame(rows), total_score, grade

# ========== UI 시작 ==========
st.title("🎯 AI중심대학 준비도 자가진단")
st.markdown("**2026년 AI중심대학 사업 신청을 위한 우리 대학의 준비 현황을 점검합니다**")

# API 상태 표시
col_api1, col_api2 = st.columns(2)
with col_api1:
    if get_openai_key():
        st.success("✅ OpenAI API 연결됨 (AI 평가 가능)")
    else:
        st.warning("⚠️ OpenAI API 미설정 (계획있음 = 50% 고정)")
with col_api2:
    if get_github_token():
        st.success("✅ GitHub 연결됨 (클라우드 저장 가능)")
    else:
        st.warning("⚠️ GitHub 미설정 (로컬 저장만 가능)")

st.divider()

# ========== 점수판 ==========
section_scores, total_score = calculate_scores()
grade, grade_desc, grade_color = get_grade(total_score)

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.metric("총점", f"{total_score}/100점")

with col2:
    score_cols = st.columns(6)
    section_names = ["거버넌스", "교육체계", "제도화", "산업연계", "특성화", "확산"]
    section_totals = [25, 25, 20, 15, 10, 5]
    for i, (name, stotal) in enumerate(zip(section_names, section_totals)):
        with score_cols[i]:
            st.metric(name, f"{section_scores.get(i+1, 0)}/{stotal}")

with col3:
    st.markdown(f"""
    <div style="background:{grade_color}; color:white; padding:20px; border-radius:15px; text-align:center;">
        <div style="font-size:2.5em; font-weight:bold;">{grade}</div>
        <div style="font-size:0.9em;">{grade_desc}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ========== 대학 정보 입력 ==========
col_uni1, col_uni2 = st.columns(2)
with col_uni1:
    university_name = st.text_input("📍 대학명 *", key="university_name")
with col_uni2:
    respondent_info = st.text_input("👤 응답자 정보 (선택)", key="respondent_info")

# Gist 불러오기
with st.expander("📂 기존 데이터 불러오기"):
    col_gist1, col_gist2 = st.columns([3, 1])
    with col_gist1:
        gist_id_input = st.text_input("Gist ID", value=st.session_state.gist_id, key="gist_id_input")
    with col_gist2:
        if st.button("불러오기", use_container_width=True):
            if gist_id_input:
                success, result = load_from_gist(gist_id_input)
                if success:
                    st.success("✅ 불러오기 완료!")
                    st.rerun()
                else:
                    st.error(f"❌ {result}")
            else:
                st.warning("Gist ID를 입력하세요")

st.divider()

# ========== 질문 섹션 ==========
for section in SECTIONS:
    with st.expander(f"**{section['id']}. {section['title']}** ({section['total']}점)", expanded=True):
        for q in section["questions"]:
            st.markdown(f"**{q['text']}** ({q['points']}점)")
            
            col_opt, col_plan = st.columns([1, 2])
            
            with col_opt:
                options = ["없음 (0점)", f"계획있음 (AI평가)", f"있음 ({q['points']}점)"]
                current = st.session_state.responses.get(q["code"], 0)
                if current == 1:
                    default_idx = 2
                elif current == 0.5:
                    default_idx = 1
                else:
                    default_idx = 0
                
                selected = st.radio(
                    "응답",
                    options,
                    index=default_idx,
                    key=f"radio_{q['code']}",
                    label_visibility="collapsed",
                    horizontal=True
                )
                
                # 값 저장
                if "있음" in selected:
                    st.session_state.responses[q["code"]] = 1
                elif "계획있음" in selected:
                    st.session_state.responses[q["code"]] = 0.5
                else:
                    st.session_state.responses[q["code"]] = 0
            
            with col_plan:
                if st.session_state.responses.get(q["code"]) == 0.5:
                    plan = st.text_area(
                        "계획 내용 (AI가 평가합니다)",
                        value=st.session_state.plans.get(q["code"], ""),
                        key=f"plan_{q['code']}",
                        height=80,
                        label_visibility="collapsed",
                        placeholder="구체적인 계획을 작성하세요..."
                    )
                    st.session_state.plans[q["code"]] = plan
                    
                    # AI 평가 결과 표시
                    if q["code"] in st.session_state.ai_evaluations:
                        ai_eval = st.session_state.ai_evaluations[q["code"]]
                        st.info(f"🤖 AI 평가: **{round(ai_eval['score']*100)}%** - {ai_eval['comment']}")
            
            st.markdown("---")

# ========== 예산 섹션 ==========
with st.expander("**※ 예산 (필수 확인)**", expanded=True):
    for q in BUDGET_QUESTIONS:
        st.markdown(f"**{q['text']}** 🔴 필수")
        
        col_opt, col_plan = st.columns([1, 2])
        
        with col_opt:
            options = ["불가능", "확보 중", "가능"]
            current = st.session_state.responses.get(q["code"], 0)
            if current == 1:
                default_idx = 2
            elif current == 0.5:
                default_idx = 1
            else:
                default_idx = 0
            
            selected = st.radio(
                "응답",
                options,
                index=default_idx,
                key=f"radio_{q['code']}",
                label_visibility="collapsed",
                horizontal=True
            )
            
            if selected == "가능":
                st.session_state.responses[q["code"]] = 1
            elif selected == "확보 중":
                st.session_state.responses[q["code"]] = 0.5
            else:
                st.session_state.responses[q["code"]] = 0
        
        with col_plan:
            if st.session_state.responses.get(q["code"]) == 0.5:
                plan = st.text_area(
                    "확보 계획",
                    value=st.session_state.plans.get(q["code"], ""),
                    key=f"plan_{q['code']}",
                    height=80,
                    label_visibility="collapsed"
                )
                st.session_state.plans[q["code"]] = plan
        
        st.markdown("---")

st.divider()

# ========== 액션 버튼 ==========
col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

with col_btn1:
    if st.button("🔄 초기화", use_container_width=True):
        st.session_state.responses = {}
        st.session_state.plans = {}
        st.session_state.ai_evaluations = {}
        st.rerun()

with col_btn2:
    if st.button("🤖 AI 평가 실행", use_container_width=True, type="primary"):
        if not get_openai_key():
            st.error("OpenAI API Key가 설정되지 않았습니다")
        else:
            # 계획있음 항목만 평가
            plans_to_evaluate = [
                code for code, value in st.session_state.responses.items()
                if value == 0.5 and st.session_state.plans.get(code)
            ]
            
            if plans_to_evaluate:
                progress = st.progress(0)
                status = st.empty()
                
                for i, code in enumerate(plans_to_evaluate):
                    status.text(f"평가 중... ({i+1}/{len(plans_to_evaluate)})")
                    
                    # 질문 텍스트 찾기
                    q_text = code
                    for section in SECTIONS:
                        for q in section["questions"]:
                            if q["code"] == code:
                                q_text = q["text"]
                                break
                    for q in BUDGET_QUESTIONS:
                        if q["code"] == code:
                            q_text = q["text"]
                    
                    result = evaluate_with_ai(q_text, st.session_state.plans[code])
                    st.session_state.ai_evaluations[code] = result
                    progress.progress((i + 1) / len(plans_to_evaluate))
                
                status.text("✅ AI 평가 완료!")
                st.rerun()
            else:
                st.warning("평가할 '계획있음' 항목이 없습니다")

with col_btn3:
    if st.button("💾 GitHub 저장", use_container_width=True):
        if not university_name:
            st.error("대학명을 입력하세요")
        elif not get_github_token():
            st.error("GitHub Token이 설정되지 않았습니다")
        else:
            success, message = save_to_gist(university_name, respondent_info)
            if success:
                st.success(message)
            else:
                st.error(message)

with col_btn4:
    df, total, grade = create_excel_data(university_name or "대학")
    
    # CSV로 다운로드 (엑셀 호환)
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
    <p>2026년 AI중심대학 자가진단 도구</p>
    <p>💡 "계획있음" 선택 후 계획 작성 → "AI 평가 실행" 클릭</p>
    <p>📁 GitHub 저장 시 Gist ID가 생성되며, 이후 불러오기 가능</p>
</div>
""", unsafe_allow_html=True)
