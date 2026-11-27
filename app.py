import os  # 파일 경로를 만들기 위한 기본 도구 (이 줄만 기본 제공 도구)
import streamlit as st  # 스트림릿 라이브러리 불러오기
import pandas as pd  # 판다스 라이브러리 불러오기 (표 데이터 다루기)

# 페이지 설정: 반드시 다른 st 명령보다 먼저 와야 한다. layout="wide"는 화면을 넓게 쓴다.
st.set_page_config(page_title="우리 회사 매출 현황", layout="wide")

REQUIRED_COLUMNS = ["date", "region", "category", "sales", "quantity"]  # 꼭 있어야 하는 열 이름 목록
# app.py와 같은 폴더에 있는 sales_sample.csv의 전체 경로 (어느 폴더에서 실행해도 같은 파일을 찾는다)
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sales_sample.csv")


# 캐시: 이 함수는 처음 한 번만 실행되고, 결과를 기억해서 다음부터는 파일을 다시 읽지 않는다
@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)  # CSV 파일을 읽어서 돌려준다 (파일이 없으면 오류가 난다)


# 사이드바 제목과 페이지 제목은 파일에 문제가 있어도 항상 보이게 먼저 그린다
st.sidebar.header("조건 선택")  # 사이드바 제목
st.title("우리 가게 매출")  # 페이지 큰 제목
st.caption("2026년 10월까지의 자료입니다")  # 제목 아래 설명 글

# ---------- 1단계: 파일이 있는지 확인 ----------
try:
    raw = load_data()  # 파일을 읽어 raw에 담는다
except FileNotFoundError:  # 파일이 없을 때 실행되는 부분
    st.warning("데이터 파일(sales_sample.csv)을 찾을 수 없습니다. 파일 이름이 정확한지, app.py와 같은 폴더에 있는지 확인해 보세요.")
    st.stop()  # 여기서 멈춘다

# ---------- 2단계: 필요한 열이 모두 있는지 확인 ----------
missing_cols = [col for col in REQUIRED_COLUMNS if col not in raw.columns]  # 없는 열 이름만 골라 담기
if missing_cols:  # 없는 열이 하나라도 있으면
    st.warning(f"필요한 열이 없습니다: {', '.join(missing_cols)}. CSV 파일의 열 이름을 확인해 주세요.")  # 없는 열 이름을 쉼표로 이어서 표시
    st.stop()  # 여기서 멈춘다

# ---------- 3단계: 데이터가 비었는지, 날짜 형식이 맞는지 확인 ----------
if raw.empty:  # 행이 하나도 없으면
    st.warning("데이터 파일에 주문 내용이 없습니다. CSV 파일에 데이터를 채워 주세요.")
    st.stop()

df = raw.copy()  # 원본(캐시된 데이터)을 건드리지 않도록 복사본을 만든다
try:
    df["date"] = pd.to_datetime(df["date"])  # date 열을 날짜 형식으로 바꾼다
except (ValueError, TypeError):  # 날짜로 바꿀 수 없는 글이 섞여 있으면
    st.warning("date 열의 날짜 형식을 읽을 수 없습니다. 날짜를 2026-01-01 형식으로 고쳐 주세요.")
    st.stop()

# ---------- 사이드바: 조건 선택 ----------
# 지역 선택: 여러 개를 고를 수 있고, 처음에는 전체가 선택되어 있다
region_options = sorted(df["region"].unique())  # 지역 이름 목록 (가나다순)
selected_regions = st.sidebar.multiselect("지역", options=region_options, default=region_options)  # default=region_options: 기본은 전체

# 카테고리 선택: 드롭다운에서 하나를 고르고, 맨 앞의 '전체'가 기본값이다
category_options = ["전체"] + sorted(df["category"].unique())  # '전체' 항목을 맨 앞에 추가
selected_category = st.sidebar.selectbox("카테고리", options=category_options)  # 드롭다운 상자

# 기간 선택: 슬라이더의 양 끝을 움직여서 시작일과 종료일을 고른다
min_date = df["date"].min().date()  # 데이터에서 가장 이른 날짜 (.date()는 날짜만 남김)
max_date = df["date"].max().date()  # 데이터에서 가장 늦은 날짜
selected_period = st.sidebar.slider(
    "기간",
    min_value=min_date,  # 슬라이더 왼쪽 끝 최솟값
    max_value=max_date,  # 슬라이더 오른쪽 끝 최댓값
    value=(min_date, max_date),  # 처음에는 전체 기간을 선택
)

# ---------- 조건대로 데이터 걸러내기 ----------
mask = df["region"].isin(selected_regions)  # 지역이 선택한 목록에 들어 있는 행만 True
if selected_category != "전체":  # 카테고리가 '전체'가 아닐 때만 카테고리 조건을 더한다
    mask = mask & (df["category"] == selected_category)  # 두 조건을 '그리고(&)'로 합친다
start, end = selected_period  # 슬라이더에서 고른 시작일과 종료일을 나눠 담는다
mask = mask & (df["date"] >= pd.Timestamp(start)) & (df["date"] <= pd.Timestamp(end))  # 기간 안에 드는 행만 True
filtered = df[mask]  # True인 행만 골라서 filtered에 담는다 (이후 모든 화면은 filtered를 쓴다)

# 필터 아래에 선택 건수와 전체 건수를 보여준다
st.sidebar.write(f"선택 조건: {len(filtered):,}건 / 전체 {len(df):,}건")  # 쉼표 형식으로 건수 표시

# ---------- 4단계: 조건에 맞는 데이터가 0건인지 확인 ----------
if filtered.empty:  # 걸러낸 표가 비어 있으면
    st.warning("선택한 조건에 맞는 데이터가 0건입니다. 사이드바에서 지역을 더 넣거나, 카테고리를 '전체'로 바꾸거나, 기간을 넓혀 보세요.")
    st.stop()  # 지표·그래프·표는 그리지 않고 멈춘다

# ---------- 본문: 탭 ----------
# 본문을 '요약'과 '상세 데이터' 두 개의 탭으로 나눈다
tab_summary, tab_detail = st.tabs(["요약", "상세 데이터"])

# '요약' 탭 내용
with tab_summary:
    # 핵심 숫자 3개 계산 (모두 filtered 기준)
    total_sales = filtered["sales"].sum()  # 총 매출: 합계
    order_count = len(filtered)  # 주문 건수: 행 개수
    avg_sales = filtered["sales"].mean()  # 평균 주문액

    # 화면을 3칸으로 나눠서 숫자 3개를 가로로 나란히 보여준다
    col1, col2, col3 = st.columns(3)
    col1.metric("총 매출", f"{total_sales:,}원")  # 쉼표를 찍고 뒤에 '원'을 붙인다
    col2.metric("주문 건수", f"{order_count:,}건")  # 쉼표를 찍고 뒤에 '건'을 붙인다
    col3.metric("평균 주문액", f"{avg_sales:,.0f}원")  # 소수점 없이 반올림해서 보여준다

    # 월별 매출 추이 (선 그래프)
    st.subheader("월별 매출 추이")  # 그래프 소제목
    monthly = filtered.groupby(filtered["date"].dt.strftime("%Y-%m"))["sales"].sum()  # 날짜를 '2026-01' 형태로 바꾼 뒤 월별 합계
    st.line_chart(monthly)  # 선 그래프로 그리기

    # 지역별 매출 (막대 그래프, 큰 순서대로)
    st.subheader("지역별 매출 (큰 순서)")  # 그래프 소제목
    region_sales = filtered.groupby("region")["sales"].sum().sort_values(ascending=False)  # 지역별 합계를 큰 값부터 정렬
    # 막대 그래프는 이름 순서대로 그려지므로, 이름 앞에 '1위', '2위'... 를 붙여서 큰 순서가 그대로 보이게 한다
    region_sales.index = [f"{rank}위 {name}" for rank, name in enumerate(region_sales.index, start=1)]  # enumerate: 1부터 순위 번호 매기기
    st.bar_chart(region_sales)  # 막대 그래프로 그리기

# '상세 데이터' 탭 내용
with tab_detail:
    # 걸러낸 데이터를 표로 보여준다
    st.dataframe(
        filtered,  # 보여줄 표 (filtered 사용)
        use_container_width=True,  # 표의 폭을 화면 폭에 맞춘다
        hide_index=True,  # 왼쪽의 행 번호를 숨긴다
    )
