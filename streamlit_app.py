import streamlit as st
import json
from fact_check import run_full_factcheck_pipeline_v3
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

st.set_page_config(
    page_title="주식 뉴스 팩트체크",
    page_icon="📊",
    layout="wide"
)   

st.title("📊 주식 뉴스 팩트체크")
st.markdown("---")

# 사이드바
with st.sidebar:
    st.header("설정")
    api_key = os.getenv("CLOVASTUDIO_API_KEY")
    if api_key:
        st.success("✅ API 키 로드됨 (.env)")
    else:
        st.error("❌ API 키를 찾을 수 없습니다")

# 메인 입력
col1, col2 = st.columns([4, 1])

with col1:
    claim = st.text_area(
        "검증할 뉴스 기사 또는 주장을 입력하세요:",
        height=150,
        placeholder="예: 12일 장중 코스피가 7999를 기록하며 전고점을 새로 썼다..."
    )

with col2:
    st.write("")
    st.write("")
    run_button = st.button("팩트체크 시작", use_container_width=True)

# 팩트체크 실행
if run_button and claim.strip():
    with st.spinner("팩트체크 진행 중..."):
        try:
            result = run_full_factcheck_pipeline_v3(claim)

            # 결과 탭
            tab1, tab2, tab3, tab4 = st.tabs(["결과", "라우팅", "상세분석", "원본데이터"])

            # 탭1: 최종 결과
            with tab1:
                fact_check = result.get("fact_check", {})

                # 팩트체크 결과
                fc_result = fact_check.get("fact_check_result", "UNKNOWN")

                if fc_result == "TRUE":
                    st.success(f"✅ 판정: {fc_result}")
                elif fc_result == "FALSE":
                    st.error(f"❌ 판정: {fc_result}")
                elif fc_result == "PARTLY_TRUE":
                    st.warning(f"⚠️ 판정: {fc_result}")
                else:
                    st.info(f"❓ 판정: {fc_result}")

                st.markdown("### 판정 이유")
                st.write(fact_check.get("reason", "정보 없음"))

                # 비교 정보
                comparisons = fact_check.get("comparisons", [])
                if comparisons:
                    st.markdown("### 수치 비교")
                    for idx, comp in enumerate(comparisons, 1):
                        with st.expander(f"{idx}. {comp.get('target', '항목')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Claim 값", comp.get("claim_value", "N/A"))
                                st.metric("계산값", comp.get("calculated_value", "N/A"))
                            with col2:
                                st.metric("기준값", comp.get("base_value", "N/A"))
                                st.metric("현재값", comp.get("current_value", "N/A"))
                            st.metric("차이", f"{comp.get('difference', 'N/A')}",
                                    delta_color="off")
                            st.write(f"일치 여부: {'✅ 일치' if comp.get('matched') else '❌ 불일치'}")

                # 매칭된 공시
                matched_disclosures = fact_check.get("matched_disclosures", [])
                if matched_disclosures:
                    st.markdown("### 매칭된 공시")
                    for idx, disclosure in enumerate(matched_disclosures, 1):
                        with st.expander(f"{idx}. {disclosure.get('report_name', 'N/A')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**기업명**: {disclosure.get('corp_name', 'N/A')}")
                                st.write(f"**종목코드**: {disclosure.get('stock_code', 'N/A')}")
                                st.write(f"**접수일자**: {disclosure.get('receipt_date', 'N/A')}")
                            with col2:
                                st.write(f"**접수번호**: {disclosure.get('receipt_no', 'N/A')}")
                                st.write(f"**키워드 점수**: {disclosure.get('keyword_score', 'N/A')}")
                                st.write(f"**매칭 키워드**: {', '.join(disclosure.get('matched_keywords', []))}")

            # 탭2: 라우팅 결과
            with tab2:
                router_result = result.get("router_result", {})
                if router_result:
                    st.json(router_result)
                else:
                    st.info("라우팅 결과가 없습니다.")

            # 탭3: 상세분석
            with tab3:
                detail_result = result.get("detail_result", {})
                if detail_result:
                    st.json(detail_result)
                else:
                    st.info("상세분석 결과가 없습니다.")

            # 탭4: 원본데이터
            with tab4:
                api_result = result.get("api_result", {})
                calculated_result = result.get("calculated_result", {})

                st.markdown("### API 응답")
                if api_result:
                    st.json(api_result)
                else:
                    st.info("API 응답이 없습니다.")

                st.markdown("### 계산 결과")
                if calculated_result:
                    st.json(calculated_result)
                else:
                    st.info("계산 결과가 없습니다.")

        except Exception as e:
            st.error(f"❌ 오류 발생: {str(e)}")

elif run_button:
    st.warning("⚠️ 검증할 뉴스를 입력하세요.")

# 예시
st.markdown("---")
st.markdown("### 💡 사용 예시")
examples = [
    "12일 장중 한 때 '7999'을 찍으며 전고점을 새로 썼던 코스피가 하락 전환하며 약세 마감했다. 이날 코스피는 전일 대비 179.09포인트(2.29%) 내린 7643.15에 장을 마쳤다.",
    "SK하이닉스가 142억 원 규모의 자기주식 처분을 결정했습니다.",
    "한화엔진은 3541억 원 규모의 선박용 엔진 공급계약을 체결했습니다."
]

for i, example in enumerate(examples):
    st.caption(f"예시 {i+1}: {example[:60]}...")