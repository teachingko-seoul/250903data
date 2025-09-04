아래 파일 두 개를 같은 폴더에 넣고, 스트림릿 클라우드(또는 로컬)에서 실행하세요.

---

## app.py

```python
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from io import StringIO

st.set_page_config(page_title="국가별 MBTI 뷰어", page_icon="🧭", layout="wide")

# -----------------------------
# 데이터 로드
# -----------------------------
@st.cache_data(show_spinner=False)
def load_data(path: str = "countries.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    # 기본 검증
    if "Country" not in df.columns:
        raise ValueError("CSV에 'Country' 컬럼이 없습니다.")
    # 숫자/비숫자 분리
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(num_cols) == 0:
        raise ValueError("수치형 MBTI 컬럼이 없습니다.")
    return df

@st.cache_data(show_spinner=False)
def aggregate_to_16types(df: pd.DataFrame) -> pd.DataFrame:
    """32개(A/T 포함) MBTI 컬럼을 16개 유형으로 합산(A+T)."""
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # base type 추출: "INTJ-A" -> "INTJ"
    def base_type(col: str) -> str:
        return col.split("-")[0] if "-" in col else col
    mapping = {col: base_type(col) for col in num_cols}
    base_types = sorted(set(mapping.values()))
    out = pd.DataFrame({"Country": df["Country"]})
    for t in base_types:
        cols = [c for c, b in mapping.items() if b == t]
        out[t] = df[cols].sum(axis=1)
    return out

@st.cache_data(show_spinner=False)
def get_country_vector(df: pd.DataFrame, country: str, mode: str) -> pd.Series:
    """선택한 국가의 분포 벡터 반환.
    mode='16'이면 16유형(A+T), mode='32'이면 원본 32변이.
    """
    if mode == "16":
        agg = aggregate_to_16types(df)
        row = agg.loc[agg["Country"] == country]
        vec = row.drop(columns=["Country"]).iloc[0]
    else:
        row = df.loc[df["Country"] == country]
        vec = row.drop(columns=["Country"]).iloc[0]
    return vec

# -----------------------------
# 사이드바: 데이터 선택
# -----------------------------
st.sidebar.title("설정")
use_uploaded = st.sidebar.toggle("CSV 업로드 사용(선택)", value=False, help="기본적으로 저장소의 countries.csv를 사용합니다. 업로드 시 해당 파일을 사용합니다.")

if use_uploaded:
    up = st.sidebar.file_uploader("countries.csv 업로드", type=["csv"])
    if up is not None:
        data = pd.read_csv(up)
    else:
        st.sidebar.info("파일을 업로드하세요. 업로드 전까지 기본 파일을 사용합니다.")
        data = load_data()
else:
    data = load_data()

# 국가 선택
countries = sorted(data["Country"].astype(str).unique().tolist())
selected_country = st.sidebar.selectbox("국가 선택", countries, index=0)

# 보기 모드
mode = st.sidebar.radio("보기 단위", ["16유형(A+T)", "32변이(A/T)"], index=0, horizontal=False)
mode_key = "16" if mode.startswith("16") else "32"

# 정규화 옵션
normalize = st.sidebar.toggle(
    "합계 1.0으로 재척도(권장)",
    value=True,
    help="각 국가 벡터 합이 1.0이 되도록 재척도합니다. 소수점 오차나 원천 데이터 편차를 보정합니다."
)

# Top-N 필터
vec_len = 16 if mode_key == "16" else data.select_dtypes(include=[np.number]).shape[1]
show_topn = st.sidebar.slider("상위 N만 보기", min_value=3, max_value=vec_len, value=min(16, vec_len))

# -----------------------------
# 본문: 헤더
# -----------------------------
st.title("국가별 MBTI 분포 뷰어")
st.caption("국가를 선택하면 MBTI 분포를 내림차순으로 정렬해 차트와 표로 보여줍니다.")

# 국가 벡터 계산
vec = get_country_vector(data, selected_country, mode_key)
vec = vec.astype(float)

# 정규화(옵션)
vec_sum = float(vec.sum())
if normalize and vec_sum != 0:
    vec = vec / vec_sum

# 정렬 및 Top-N
vec_sorted = vec.sort_values(ascending=False)
vec_top = vec_sorted.head(show_topn)

# 표 준비
df_display = pd.DataFrame({"Type": vec_top.index, "Share": vec_top.values})
# 퍼센트 포맷용 컬럼
df_display["Share (%)"] = (df_display["Share"] * 100).round(2)

# -----------------------------
# 상단 요약 카드
# -----------------------------
col1, col2, col3 = st.columns([1,1,1])
col1.metric("선택 국가", selected_country)
col2.metric("합계(표시 값)", f"{vec_top.sum():.4f}")
col3.metric("원본 합계", f"{vec_sum:.4f}")

# -----------------------------
# 차트
# -----------------------------
base = alt.Chart(df_display).encode(
    x=alt.X("Share:Q", title="비중"),
    y=alt.Y("Type:N", sort='-x', title="유형"),
)
bar = base.mark_bar().properties(height=max(320, 22 * len(df_display)), width=720)
text = base.mark_text(align='left', dx=4).encode(text=alt.Text("Share (%)"))

st.subheader(f"{selected_country} — {'16유형(A+T)' if mode_key=='16' else '32변이(A/T)'} 분포 (내림차순)")
st.altair_chart(bar + text, use_container_width=True)

# -----------------------------
# 표와 다운로드
# -----------------------------
st.subheader("데이터 테이블")
st.dataframe(
    df_display[["Type", "Share", "Share (%)"]],
    use_container_width=True,
    hide_index=True
)

csv_buf = StringIO()
df_out = df_sorted = vec_sorted.reset_index()
df_out.columns = ["Type", "Share"]
if normalize:
    df_out["Note"] = "normalized to sum=1"

df_out.to_csv(csv_buf, index=False)
st.download_button(
    label="이 국가의 전체 분포 CSV 다운로드",
    data=csv_buf.getvalue().encode("utf-8"),
    file_name=f"{selected_country.replace(' ', '_')}_MBTI_distribution_{'16' if mode_key=='16' else '32'}.csv",
    mime="text/csv"
)

st.caption("Tip: 좌측 사이드바에서 보기 단위(16/32), 정규화, Top-N을 조절해보세요.")
```

---

## requirements.txt

```txt
streamlit>=1.31
pandas>=2.0
numpy>=1.26
altair>=5.0
```
