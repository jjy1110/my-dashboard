import pandas as pd  # 판다스 라이브러리 불러오기 (표 데이터를 다루는 도구)

# CSV 파일을 읽어서 df(데이터프레임, 엑셀 표 같은 것)에 담기
df = pd.read_csv("sales_sample.csv")

# 1. 행과 열의 개수 출력 (df.shape는 (행 수, 열 수)를 돌려줌)
print("1. 행, 열 개수:", df.shape)
print()  # 빈 줄 한 칸 띄우기

# 2. 열 이름과 자료형 출력 (dtype: 숫자(int64, float64), 글자(object), 날짜 등)
print("2. 열 이름과 자료형")
print(df.dtypes)
print()

# 3. 열별 빈칸(결측치, 값이 비어 있는 칸) 개수 출력
print("3. 열별 빈칸 개수")
print(df.isna().sum())  # isna(): 빈칸이면 True, sum(): 열별로 True 개수를 더함
print()

# 4. 숫자 열의 요약 통계 출력 (개수, 평균, 표준편차, 최솟값, 사분위수, 최댓값)
print("4. 숫자 열 요약")
print(df.describe())  # 숫자 열만 골라서 요약해 줌
print()

# 5. 서울 지역에서 매출이 10만 원 이상인 주문 몇 건인지 출력
seoul_big = df[(df["region"] == "서울") & (df["sales"] >= 100000)]  # 조건에 맞는 행만 골라 담기
print("5. 서울 & 매출 10만 원 이상 주문 건수:", len(seoul_big), "건")  # len(): 골라낸 행의 개수
print()

# 6. 월별 매출 합계 출력
df["month"] = df["date"].str[:7]  # date 글자의 앞 7글자(예: 2026-01)만 잘라 month 열 새로 만들기
monthly = df.groupby("month")["sales"].sum()  # month별로 묶어서 sales를 더하기
print("6. 월별 매출 합계")
print(monthly)
print()

# 7. 카테고리별 매출 합계 출력
category = df.groupby("category")["sales"].sum()  # category별로 묶어서 sales를 더하기
print("7. 카테고리별 매출 합계")
print(category)
