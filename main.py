# streamlit_app.py
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

st.set_page_config(page_title="MBTI 학습 컨설팅 👩‍🏫📚", page_icon="🎈", layout="wide")

# ---------- 스타일 ----------
st.markdown("""
<style>
:root {
  --pri: #6C5CE7; /* 보라 */
  --sec: #00CEC9; /* 민트 */
  --acc: #FD79A8; /* 핑크 */
}
html, body, [class*="css"]  {
  font-family: "Pretendard", "Apple SD Gothic Neo", "Noto Sans KR", sans-serif;
}
.big-title {
  font-size: 2.2rem; font-weight: 800; 
  background: linear-gradient(90deg, var(--pri), var(--sec));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  margin-bottom: .1rem;
}
.sub {
  color: #666; margin-bottom: 1rem;
}
.card {
  background: white; border-radius: 20px; padding: 18px 20px; 
  border: 1px solid rgba(0,0,0,.06); box-shadow: 0 6px 24px rgba(0,0,0,.06);
}
.badge {
  display: inline-block; padding: 4px 10px; border-radius: 999px; 
  font-size: .85rem; font-weight: 700; margin-right: 6px;
  background: rgba(108,92,231,.12); color: var(--pri);
}
.highlight {
  background: linear-gradient(90deg, rgba(0,206,201,.15), rgba(253,121,168,.15));
  border-radius: 12px; padding: 8px 12px; display: inline-block;
}
hr { border-top: 1px dashed rgba(0,0,0,.15); margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ---------- 데이터 ----------
MBTI_INFO = {
    "ISTJ": {
        "name": "청렴한 관리자 🧭",
        "strengths": [
            "체계적이고 계획을 잘 세움", "규칙과 마감 준수", "세부사항에 강함"
        ],
        "weaknesses": [
            "변화와 즉흥적 과제에 둔감", "완벽주의로 시간 낭비 가능", "협업 소통이 건조할 수 있음"
        ],
        "methods": [
            "주 1회 '전략 회의'로 주간 학습 로드맵 작성 (체크리스트 ✅)",
            "각 과목마다 요약-예제-오답 순서의 고정 루틴",
            "시간 박스(Time-boxing)로 과목 슬롯 고정 (예: 40분/10분 휴식)"
        ],
        "tools": ["Notion 데이터베이스", "TickTick/Google Tasks", "Anki(카드)"]
    },
    "ISFJ": {
        "name": "수호자 🤝",
        "strengths": ["성실하고 책임감 강함", "장기적 꾸준함", "타인을 돕는 과정에서 동기 상승"],
        "weaknesses": ["도움 요청을 못함", "과도한 봉사로 자기 시간 축소", "실수 두려움"],
        "methods": [
            "동료 튜터링(서로 설명)으로 기억 고착 👥",
            "오답노트에 '왜'와 '다음에' 칸을 분리",
            "하루 마지막 10분 '셀프칭찬 로그'로 자신감 유지"
        ],
        "tools": ["GoodNotes/OneNote", "Forest(집중)", "Study With Me 영상"]
    },
    "INFJ": {
        "name": "옹호자 🔮",
        "strengths": ["목적 지향, 의미 찾기", "깊은 집중과 통합적 이해", "글쓰기/정리 능력"],
        "weaknesses": ["과도한 이상화로 시작 못함", "감정 기복에 생산성 영향", "완벽주의"],
        "methods": [
            "공부의 '왜'를 1문장 미션으로 정의하고 매 세션 상단에 표기",
            "Feynman 기법: 배운 내용을 10살에게 설명하듯 쓰기 ✍️",
            "포모도로 50/10으로 깊공 확보, 세션 후 산책 5분"
        ],
        "tools": ["Obsidian(지식 그래프)", "Notability", "Calm/Breathwrk(감정 조절)"]
    },
    "INTJ": {
        "name": "전략가 ♟️",
        "strengths": ["장기계획 수립", "패턴/원리 파악", "독학 능력"],
        "weaknesses": ["협업 선호 낮음", "관심 없는 과목 무관심", "과한 이론 몰입"],
        "methods": [
            "시험 역산 플랜(Goal → Milestone → Daily Sprint)",
            "개념 20%로 80% 문제 커버하는 '핵심 리스트' 만들기",
            "주 2회 메타인지 점검: 약점 과목에 실전 세트 투입"
        ],
        "tools": ["Notion+Gantt", "Anki Spaced Repetition", "Past papers(기출)"]
    },
    "ISTP": {
        "name": "만능 재주꾼 🛠️",
        "strengths": ["문제 해결력", "실험/손으로 배우기 선호", "침착함"],
        "weaknesses": ["루틴 지루함", "장기 계획 미루기", "마감 직전 러시"],
        "methods": [
            "퀘스트형 체크포인트로 학습(작은 미션, 보상 🎮)",
            "문제 풀며 역으로 개념 채우기(Top-down)",
            "짧은 30/5 스프린트로 지루함 최소화"
        ],
        "tools": ["Khan/유튜브 실험", "Quizlet", "Timer 위젯"]
    },
    "ISFP": {
        "name": "호기심 많은 예술가 🎨",
        "strengths": ["감각/직관 활용", "유연하고 배려심 많음", "몰입 시 창의적 성과"],
        "weaknesses": ["계획 지속 어려움", "비판에 예민", "마감 관리 취약"],
        "methods": [
            "컬러코딩 노트 & 스티커로 시각적 기억 강화",
            "플레이리스트/환경 디자인(향, 조명)으로 몰입",
            "친절한 난이도 사다리: 쉬움→보통→어려움"
        ],
        "tools": ["GoodNotes 스티커", "Lo-fi/피아노 BGM", "Habitica(게이미피케이션)"]
    },
    "INFP": {
        "name": "열정적인 중재자 🌱",
        "strengths": ["가치와 연결 시 무한 동력", "글쓰기/스토리텔링", "공감"],
        "weaknesses": ["흥미 없으면 탈선", "현실적 마감 약함", "과한 자기비판"],
        "methods": [
            "과목을 '내 이야기'로 재해석(캐릭터/메타포 만들기)",
            "2분 규칙(바로 시작) + 첫 10분 '정리만'으로 관성 확보",
            "주 1회 '작은 발표'로 표현 욕구 충족"
        ],
        "tools": ["Obsidian 템플릿", "Roam-like 아웃라이너", "Toggl(시간로그)"]
    },
    "INTP": {
        "name": "논리술사 🧪",
        "strengths": ["분석/추론 탁월", "독창적 아이디어", "개념간 연결"],
        "weaknesses": ["끝맺음 약함", "단조로운 반복 싫어함", "현실감각 부족"],
        "methods": [
            "연결노트(개념→정의→예시→반례) 포맷 고정",
            "문제 세트는 제한시간 모드로 엔진 가동 ⏱️",
            "학습 후 '버그 리포트' 작성(헷갈린 지점 기록)"
        ],
        "tools": ["Notion 수식/LaTeX", "Desmos/GeoGebra", "Code Runner(파이썬)"]
    },
    "ESTP": {
        "name": "사업가 ⚡",
        "strengths": ["실전형, 즉각 실행", "위기대응", "팀을 에너지로 이끎"],
        "weaknesses": ["장기 루틴 지루", "세부 정리 소홀", "충동적 선택"],
        "methods": [
            "스터디 그룹 리더 맡아 책임감 부여",
            "실전 모의·스피드런으로 경쟁심 활용",
            "핵심 요약 카드로 휴대성↑"
        ],
        "tools": ["Kahoot/퀴즈", "Anki 모바일", "Focus To-Do(포모도로)"]
    },
    "ESFP": {
        "name": "자유로운 영혼 🎉",
        "strengths": ["사교성, 분위기 메이커", "감각적 학습", "즉흥 아이디어"],
        "weaknesses": ["집중 분산", "계획 지키기 어려움", "과제 미루기"],
        "methods": [
            "짧은 스프린트(25/5) + 세션마다 소소한 보상",
            "친구와 체크인 사진/이모지 인증 📸",
            "큰 소리로 설명하면서 공부(Active Recall)"
        ],
        "tools": ["Studygram/인증방", "Quizlet 스캔", "Stand desk 타이머"]
    },
    "ENFP": {
        "name": "재기발랄한 활동가 🦋",
        "strengths": ["아이디어 샘솟음", "빠른 이해", "사람에게서 동기"],
        "weaknesses": ["새로운 것에 쉽게 산만", "꾸준함 유지 어려움", "마감 러시"],
        "methods": [
            "3가지 우선순위 규칙(오늘 TOP3만 꼭) ⭐⭐⭐",
            "아이디어는 인박스로 수집하고 밤에 한 번에 분류",
            "책임 파트너와 매일 5분 스탠드업"
        ],
        "tools": ["Notion 캡처 위젯", "Google 캘린더", "Focusmate(책임 파트너)"]
    },
    "ENTP": {
        "name": "토론가 🗣️",
        "strengths": ["논쟁적 사고, 즉흥 토론", "패턴 전환 능력", "문제 재정의"],
        "weaknesses": ["완료보다 시작 선호", "규칙적 연습 부족", "지루함에 취약"],
        "methods": [
            "타이머로 '논증→반례→정리' 3스텝 루프",
            "주 2회 스터디 토론 리드(설명하며 학습)",
            "기출 변형 만들어 보기(창의적 과제)"
        ],
        "tools": ["Debate timer", "Jamboard/화이트보드", "ChatGPT로 반박연습"]
    },
    "ESTJ": {
        "name": "경영자 🧱",
        "strengths": ["조직/관리 능력", "목표-성과 중심", "책임감"],
        "weaknesses": ["유연성 부족", "감정 케어 소홀", "과한 통제"],
        "methods": [
            "KPI 대시보드(모의고사 점수, 진도)로 가시화 📊",
            "주요 과목 SOP 문서화(항상 같은 단계로 실행)",
            "주 1회 '리스크 검토'로 약점 선제 관리"
        ],
        "tools": ["구글시트 대시보드", "TickTick 반복할 일", "Scanner Pro(오답 수집)"]
    },
    "ESFJ": {
        "name": "집정관 🫶",
        "strengths": ["협력, 관계 조성", "성실/정리", "팀 기여로 동기↑"],
        "weaknesses": ["타인 눈치로 자기 일정 희생", "갈등 회피", "새 방법 시도에 망설임"],
        "methods": [
            "짝스터디: 서로 일정 공유 & 칭찬 스티커 🌟",
            "주간 식단/수면/운동까지 포함한 웰빙 체크",
            "학부모/선생님과 주간 리포트 공유"
        ],
        "tools": ["공유 캘린더", "Habit tracker", "Canva 리포트"]
    },
    "ENFJ": {
        "name": "선도자 🧭💬",
        "strengths": ["코칭/리더십", "공감적 의사소통", "팀 기반 성장"],
        "weaknesses": ["자기과제 후순위", "비판에 예민", "과도한 책임"],
        "methods": [
            "팀 과제 리드하며 자기 학습 목표도 얹기",
            "칭찬/피드백 로그(긍정 3 : 개선 1 비율) 유지",
            "발표형 과제 자주 수행(슬라이드 3장 제한)"
        ],
        "tools": ["Slides/Canva", "Trello 보드", "Focusmate/동시접속"]
    },
    "ENTJ": {
        "name": "통솔자 🏁",
        "strengths": ["결단/추진력", "시스템 설계", "경쟁심 강함"],
        "weaknesses": ["완급조절 부족", "협력자 감정 간과", "과부하 위험"],
        "methods": [
            "OKR(목표/핵심결과) 분기 설정 → 주간 KR 체크",
            "데일리 스프린트 보드로 WIP 제한(동시 과제 3개 이하)",
            "실전 모의+리뷰 사이클 자동화"
        ],
        "tools": ["Jira/Trello", "Notion OKR", "Past papers 자동 채점(가능 시)"]
    },
    "ISTJ": {},  # placeholder overwritten above
    "ISFJ": {},  # placeholder overwritten above
    "INFJ": {},  # placeholder overwritten above
    "INTJ": {},  # placeholder overwritten above
    "ISTP": {},  # placeholder overwritten above
    "ISFP": {},  # placeholder overwritten above
    "INFP": {},  # placeholder overwritten above
    "INTP": {},  # placeholder overwritten above
    "ESTP": {},  # placeholder overwritten above
    "ESFP": {},  # placeholder overwritten above
    "ENFP": {},  # placeholder overwritten above
    "ENTP": {},  # placeholder overwritten above
    "ESTJ": {},  # placeholder overwritten above
    "ESFJ": {},  # placeholder overwritten above
    "ENFJ": {},  # placeholder overwritten above
    "ENTJ": {}   # placeholder overwritten above
}

# 위 딕셔너리에서 중복 키 문제 방지용 정제 (빈 dict 제거)
MBTI_INFO = {k: v for k, v in MBTI_INFO.items() if v}

ALL_TYPES = ["ISTJ","ISFJ","INFJ","INTJ","ISTP","ISFP","INFP","INTP",
             "ESTP","ESFP","ENFP","ENTP","ESTJ","ESFJ","ENFJ","ENTJ"]

# ---------- 사이드바 ----------
with st.sidebar:
    st.markdown("### 🎯 내 유형 선택")
    mbti = st.selectbox("MBTI를 선택하세요", ALL_TYPES, index=ALL_TYPES.index("ENFP"))
    st.markdown("---")
    st.markdown("### ⏱️ 포모도로 설정")
    focus_min = st.slider("집중 시간(분)", 20, 60, 40, step=5)
    break_min = st.slider("휴식 시간(분)", 3, 15, 10, step=1)
    total_hours = st.slider("총 공부 시간(시간)", 1, 10, 3, step=1)
    st.markdown("---")
    st.markdown("### 🎲 재미 기능")
    luck_btn = st.button("오늘의 학습 운세 뽑기 ✨")
    confetti = st.checkbox("집중 세션 시작 시 풍선/눈 효과", value=True)

# ---------- 헤더 ----------
st.markdown('<div class="big-title">MBTI 맞춤 학습 컨설팅 웹앱</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">당신의 성향에 딱 맞는 공부 전략을 추천해드려요! 😊</div>', unsafe_allow_html=True)

# 축하/운세
if luck_btn:
    fortunes = [
        "지금 시작하면 초집중 모드 ON! 🚀", "오답이 보물로 바뀌는 날 💎",
        "친구에게 설명하면 이해도 2배 📢", "짧고 굵게! 스프린트가 효율 최고 🏃",
        "물 많이 마시기! 뇌가 좋아해요 💧", "핵심만 콕! 요약이 신의 한 수 🎯"
    ]
    st.success("🧿 오늘의 운세: " + random.choice(fortunes))
    st.balloons()

# ---------- MBTI 카드 ----------
info = MBTI_INFO.get(mbti, None)
cols = st.columns([1.2, 1, 1])

with cols[0]:
    st.markdown(f"""<div class='card'>
    <span class='badge'>유형</span>
    <h2 style='margin: .2rem 0 0;'>{mbti} · {info['name'] if info else '학습형'}</h2>
    <div class='highlight'>📌 이 유형에게 맞춘 핵심 전략을 아래에서 확인하세요!</div>
    </div>""", unsafe_allow_html=True)

with cols[1]:
    st.markdown("<div class='card'><b>🌟 강점(Study Superpowers)</b><br></div>", unsafe_allow_html=True)
    if info:
        for s in info["strengths"]:
            st.markdown(f"- ✅ {s}")

with cols[2]:
    st.markdown("<div class='card'><b>🧩 약점(주의 포인트)</b><br></div>", unsafe_allow_html=True)
    if info:
        for w in info["weaknesses"]:
            st.markdown(f"- ⚠️ {w}")

st.markdown("")

# ---------- 추천 학습법 ----------
st.markdown("### 🧠 맞춤 공부 방법 & 루틴 제안")
if info:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    for m in info["methods"]:
        st.markdown(f"• {m}")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**🔧 추천 도구/앱**")
    st.markdown(", ".join([f"`{t}`" for t in info["tools"]]))
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- 포모도로 기반 세션 플래너 ----------
st.markdown("### 🗓️ 포모도로 세션 플래너 (자동 생성)")
total_minutes = total_hours * 60
cycle = focus_min + break_min
num_cycles = int(np.floor(total_minutes / cycle))
start_time = datetime.now().replace(second=0, microsecond=0)
schedule = []
for i in range(num_cycles):
    s = start_time + timedelta(minutes=i*cycle)
    e = s + timedelta(minutes=focus_min)
    schedule.append({
        "세션": i+1,
        "집중 시작": s.strftime("%H:%M"),
        "집중 종료": e.strftime("%H:%M"),
        "휴식": f"{break_min}분"
    })

df = pd.DataFrame(schedule)
if len(df) == 0:
    st.info("설정값으로 생성 가능한 세션이 없어요. 슬라이더를 조정해보세요! 🙂")
else:
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 일정 CSV 다운로드", data=csv, file_name=f"pomodoro_{mbti}.csv", mime="text/csv")
    if confetti:
        st.toast("집중 세션 준비 완료! 파이팅 💪")
        if random.random() < 0.5:
            st.balloons()
        else:
            st.snow()

# ---------- 학습 체크리스트 ----------
st.markdown("### ✅ 오늘의 체크리스트 (클릭하여 체크)")
with st.form("checklist"):
    c1 = st.checkbox("핵심 개념 3개 요약하기 ✍️")
    c2 = st.checkbox("활성 회상(Active Recall) 20문제 풀기 🧠")
    c3 = st.checkbox("오답노트에 '왜 틀렸는지' 한 줄 쓰기 🪄")
    c4 = st.checkbox("5분 정리 & 내일 첫 할 일 정하기 🗒️")
    submitted = st.form_submit_button("저장")

if submitted:
    done = sum([c1, c2, c3, c4])
    st.success(f"체크리스트 {done}/4 완료! 멋져요 👏")
    if done == 4:
        st.balloons()

# ---------- 유형별 보너스 팁 ----------
st.markdown("### 🎁 유형별 보너스 팁")
bonus = {
    "P(감각 S)": "시각 자료(도식/도표/색상)를 적극 활용해요.",
    "N(직관 N)": "아이디어는 인박스에 모아 한 번에 분류하세요.",
    "T(사고 T)": "근거-반례-결론 구조로 메모하면 명료해져요.",
    "F(감정 F)": "셀프 칭찬 로그로 동기와 회복탄력성을 챙겨요.",
    "J(판단 J)": "Time-box로 일정 고정, 완벽 대신 완료!",
    "P(인식 P)": "짧은 스프린트 + 보상 루프로 재미를 유지!"
}
colb = st.columns(3)
for i, (k, v) in enumerate(bonus.items()):
    with colb[i%3]:
        st.markdown(f"<div class='card'><b>• {k}</b><br>{v}</div>", unsafe_allow_html=True)

# ---------- 푸터 ----------
st.markdown("---")
st.caption("© 2025 MBTI 학습 컨설팅 • 재미 있게, 똑똑하게, 꾸준하게 🎈")
