# 🎯 AI중심대학 자가진단 시스템

2026년 AI중심대학 사업 신청을 위한 우리 대학의 준비 현황을 점검하는 자가진단 도구입니다.

## ✨ 주요 기능

- **30개 항목 자가진단**: 6개 영역 + 예산
- **실시간 점수 계산**: 100점 만점
- **AI 평가**: "계획있음" 선택 시 GPT-4o-mini가 계획 적절성 평가
- **클라우드 저장**: GitHub Gist에 자동 저장/불러오기
- **엑셀 다운로드**: AI 평가 결과 포함

## 🚀 배포 방법 (Streamlit Cloud)

### 1. GitHub 리포지토리 생성

```bash
# 리포지토리 생성 후
git clone https://github.com/your-username/ai-survey.git
cd ai-survey

# 파일 복사
cp app.py requirements.txt .gitignore README.md ./
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/

git add .
git commit -m "Initial commit"
git push
```

### 2. Streamlit Cloud 배포

1. [share.streamlit.io](https://share.streamlit.io) 접속
2. **New app** 클릭
3. GitHub 리포지토리 선택
4. **Deploy!** 클릭

### 3. API 키 설정 (중요!)

배포 후 Streamlit Cloud에서:

1. 앱 설정 → **Secrets** 메뉴
2. 아래 내용 입력:

```toml
OPENAI_API_KEY = "sk-proj-실제-API-키"
GITHUB_TOKEN = "ghp_실제-토큰"
```

3. **Save** 클릭

> ⚠️ **API 키는 Streamlit Cloud의 Secrets에만 저장됩니다. GitHub에는 절대 업로드되지 않습니다.**

## 💻 로컬 실행 방법

```bash
# 가상환경 생성 (선택)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# secrets.toml 설정
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# secrets.toml에 실제 API 키 입력

# 실행
streamlit run app.py
```

## 📊 평가 영역 및 배점

| 영역 | 배점 | 항목 수 |
|------|------|---------|
| 1. 총장 직속 AI 거버넌스 | 25점 | 5 |
| 2. 학부·대학원 교육체계 | 25점 | 5 |
| 3. 제도화 가능성 | 20점 | 5 |
| 4. 산업 연계의 현실성 | 15점 | 5 |
| 5. 대학 특성화 논리 | 10점 | 4 |
| 6. 확산·부가 프로그램 | 5점 | 4 |
| ※ 예산 (필수) | - | 2 |
| **합계** | **100점** | **30** |

## 🎯 등급 기준

| 등급 | 점수 | 설명 |
|------|------|------|
| A | 85점 이상 | 선정 가능성 높음 |
| B | 70~84점 | 보완 후 도전 가능 |
| C | 55~69점 | 상당한 준비 필요 |
| D | 40~54점 | 기반 구축 필요 |
| F | 40점 미만 | 재검토 권고 |

## 🔑 API 키 발급 방법

### OpenAI API Key
1. [platform.openai.com](https://platform.openai.com) 접속
2. 로그인 → API Keys 메뉴
3. **Create new secret key** 클릭
4. 키 복사 (한 번만 표시됨!)

### GitHub Token
1. [github.com/settings/tokens](https://github.com/settings/tokens) 접속
2. **Generate new token (classic)** 클릭
3. Note: "AI Survey" 입력
4. **gist** 권한만 체크
5. **Generate token** 클릭
6. 토큰 복사

## 📁 파일 구조

```
ai-survey-streamlit/
├── app.py                      # 메인 Streamlit 앱
├── requirements.txt            # 패키지 목록
├── .gitignore                  # secrets.toml 제외
├── README.md                   # 이 파일
└── .streamlit/
    └── secrets.toml.example    # API 키 템플릿
```

## 📝 라이선스

MIT License
