import streamlit as st
import pandas as pd
import pydeck as pdk

# 세션 상태 초기화
if "ID" not in st.session_state:
    st.session_state["ID"] = "None"

ID = st.session_state["ID"]
with st.sidebar:
    st.caption(f'{ID}님 접속중')

# 페이지 제목
st.title("🏥전국 병원 위치 및 진료과목 분석")
st.markdown("병원의 위치를 지도에 표시하고, 수용 가능 인원에 따라 마커 크기를 조절합니다.")

# CSV 파일 로드
data = pd.read_csv("hospital_data.csv")
data = data.dropna()
data['진료과목'] = data['진료과목'].str.strip()

# 새로운 열 추가: 지역 정보 추출 (서울, 부산 등)
data['지역'] = data['병원명'].apply(lambda x: x[:2])  # 병원명 앞 두 글자를 지역명으로 추출

# 사이드바에서 진료 과목 선택
selected_dept = st.sidebar.selectbox("진료 과목을 선택하세요:", ["전체"] + sorted(data['진료과목'].unique()))

# 진료 과목 필터링
if selected_dept != "전체":
    filtered_data = data[data['진료과목'] == selected_dept]
else:
    filtered_data = data

# 진료 과목별 병원 수 시각화 (Streamlit 내장 차트 사용)
st.subheader("진료 과목별 병원 수")
dept_counts = data['진료과목'].value_counts()
st.bar_chart(dept_counts)

# 새롭게 추가된 그래프: 지역별 수용 인원 총합
st.subheader("지역별 수용 인원 총합")
if selected_dept == "전체":
    region_capacity = data.groupby('지역')['수용인원'].sum().sort_values()
else:
    region_capacity = filtered_data.groupby('지역')['수용인원'].sum().sort_values()

# 지역별 수용 인원 막대 그래프 표시
st.bar_chart(region_capacity)

# 병원 수용 인원에 따라 마커 크기 조절 (마커 크기 증가)
filtered_data['마커크기'] = filtered_data['수용인원'] / filtered_data['수용인원'].max() * 3000

# 병원 위치 지도 시각화 (순서를 뒤로 이동)
st.subheader(f"병원 위치 지도 ({selected_dept} 진료과목)")
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/streets-v11',
    initial_view_state=pdk.ViewState(
        latitude=filtered_data['위도'].mean(),
        longitude=filtered_data['경도'].mean(),
        zoom=10,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=filtered_data,
            get_position=['경도', '위도'],
            get_color='[200, 30, 0, 160]',
            get_radius='마커크기',
            pickable=True,
            tooltip={"text": "{병원명}\n진료 과목: {진료과목}\n수용 인원: {수용인원}"}
        )
    ]
))