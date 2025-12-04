import streamlit as st
import pandas as pd
import io
import random # <-- 랜덤 기능을 위해 추가

# ------------------------------------------------
# 1. 경쟁 강도 및 난이도 판정 함수
# ------------------------------------------------
def get_difficulty_grade(document_count, search_volume):
    """총 문서 수와 검색량을 기반으로 경쟁 난이도 등급을 계산합니다."""
    if search_volume > 0:
        score = document_count / search_volume
    else:
        return "데이터 부족", "검색량 0", 0.0

    if score <= 5.0:
        grade = "🥇 황금 키워드"
        description = "매우 낮음"
    elif score <= 15.0:
        grade = "🥈 양호한 키워드"
        description = "보통"
    elif score <= 30.0:
        grade = "🥉 주의 필요 키워드"
        description = "치열"
    else:
        grade = "🚨 레드 오션"
        description = "매우 높음"
        
    return grade, description, round(score, 2)

# ------------------------------------------------
# 2. 최적 제목 및 키워드 조합 추천 함수 (랜덤 조합 적용)
# ------------------------------------------------
def recommend_title(keyword, grade):
    """키워드와 경쟁 등급에 따라 랜덤 조합된 제목 템플릿을 추천합니다."""

    # 템플릿에 들어갈 다양한 구문 리스트 정의
    success_phrases = ["실패 없는 비법", "황금 레시피 공개", "누구나 100% 성공", "숨겨진 비법 노하우"]
    problem_phrases = ["비린내 완벽 제거", "감칠맛 내는 법", "최대 1년 보관법", "초보도 뚝딱 만드는 법"]
    power_words = ["완벽", "궁극의", "역대급", "단 10분"]
    numbers = [3, 5, 7, 9, 10]
    
    st.header(f"3. 최적 키워드 ({keyword}) 제목 전략")

    if '황금' in grade or '양호' in grade:
        st.markdown("### ✨ 추천 제목 조합 3가지:")
        
        # 1. 황금 키워드용 (성공/비법 강조)
        template_1 = (
            f"✅ **{keyword}** "
            f"{random.choice(success_phrases)} {random.choice(numbers)}가지 ({random.choice(numbers)}분 완성)"
        )
        # 2. 양호 키워드용 (문제 해결 강조)
        template_2 = (
            f"🔥 **{keyword}** 핵심 정리 | "
            f"{random.choice(problem_phrases)} {random.choice(power_words)} 레시피"
        )
        # 3. 흥미 유발형 (궁극/완벽 강조)
        template_3 = (
            f"💡 **{keyword}** 이것만 알면 끝 | {random.choice(power_words)} 쉽고 완벽한 맛"
        )

        st.markdown(f"* 1. {template_1}")
        st.markdown(f"* 2. {template_2}")
        st.markdown(f"* 3. {template_3}")
        
    else:
        st.info("💡 **활용 전략:** 경쟁이 높습니다. 제목 추천보다는 키워드를 더 쪼개서 분석하는 데 집중하세요.")


# ------------------------------------------------
# 3. 데이터 다운로드 버튼 생성 함수
# ------------------------------------------------
@st.cache_data
def convert_df_to_csv(df):
    """분석 결과를 CSV로 변환합니다."""
    # 한글 인코딩 문제 해결을 위해 'utf-8-sig' 사용
    return df.to_csv(index=False, encoding='utf-8-sig')


# ------------------------------------------------
# 4. 웹페이지 레이아웃 설정 (Streamlit UI)
# ------------------------------------------------
st.set_page_config(page_title="궁극의 키워드 통합 분석기", layout="wide")

st.title("🏆 궁극의 키워드 분석 통합 툴")
st.caption("다중 키워드 일괄 분석 및 경쟁 포화도 자동 판정")

# 입력 폼
with st.form("ultimate_keyword_input_form"):
    st.header("1. 블랙키위 데이터 일괄 입력")

    st.markdown("""
        **[사용 가이드]**
        1. 블랙키위에서 분석할 롱테일 키워드 목록을 수집합니다.
        2. 각 키워드의 **키워드명, 월간 검색량, 총 문서 수**를 쉼표(,) 또는 탭으로 구분하여 아래 텍스트 상자에 붙여넣으세요.
        3. **각 키워드 데이터는 한 줄에 하나씩** 입력해야 합니다.
        
        **입력 예시:**
        ```
        묵은지고등어조림 레시피, 2220, 6470
        고등어조림 황금레시피, 4500, 73000
        백종원 고등어조림, 18000, 320000
        ```
    """)
    
    # 다중 키워드 데이터 입력 필드
    keyword_data_input = st.text_area(
        "다중 키워드 데이터 (키워드명, 검색량, 문서수 순)", 
        height=200,
        placeholder="키워드명, 검색량, 문서수\n예: 묵은지고등어조림 레시피, 2220, 6470"
    )
    
    submitted = st.form_submit_button("통합 분석 시작")

# ------------------------------------------------
# 5. 분석 실행 및 결과 출력
# ------------------------------------------------
if submitted and keyword_data_input:
    # 텍스트 데이터를 DataFrame으로 변환
    data = []
    # 탭 또는 쉼표 구분자 처리
    lines = keyword_data_input.strip().split('\n')
    
    for line in lines:
        # 먼저 쉼표로 분리 시도, 실패 시 탭으로 분리 시도
        parts = [p.strip() for p in line.split(',') if p.strip()]
        if len(parts) != 3:
            parts = [p.strip() for p in line.split('\t') if p.strip()] # 탭으로 분리 시도
            
        if len(parts) == 3:
            try:
                keyword = parts[0]
                search_volume = int(parts[1])
                document_count = int(parts[2])
                
                # 경쟁 분석 실행
                grade, desc, score = get_difficulty_grade(document_count, search_volume)
                
                data.append({
                    '키워드': keyword,
                    '검색량': search_volume,
                    '문서수': document_count,
                    '난이도 점수 (D/C)': score,
                    '최종 등급': grade,
                    '난이도': desc
                })
            except ValueError:
                st.error(f"'{line}' 데이터를 숫자로 변환할 수 없습니다. 검색량과 문서수는 숫자로 입력해 주세요.")
                continue
        else:
            st.warning(f"'{line}' 데이터 형식이 올바르지 않습니다. '키워드명, 검색량, 문서수' 형식이어야 합니다.")


    if data:
        df = pd.DataFrame(data)
        # 난이도 점수를 기준으로 오름차순 정렬 (낮을수록 황금 키워드)
        df_sorted = df.sort_values(by='난이도 점수 (D/C)', ascending=True).reset_index(drop=True)

        st.divider()
        st.header("2. 다중 키워드 분석 결과 (난이도 오름차순 정렬)")

        st.dataframe(df_sorted.style.highlight_min(subset=['난이도 점수 (D/C)'], color='lightgreen', axis=0), use_container_width=True)
        
        # 다운로드 버튼
        csv = convert_df_to_csv(df_sorted)
        st.download_button(
            label="분석 결과 CSV 다운로드",
            data=csv,
            file_name=f'키워드_분석_결과_{pd.Timestamp.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
        )

        st.markdown("---")
        
        # 3. 최적 제목 추천 (가장 점수가 낮은 키워드에 대해)
        best_keyword = df_sorted.iloc[0]
        
        st.metric(
            label="가장 유리한 키워드 (점수)", 
            value=f"{best_keyword['키워드']} ({best_keyword['난이도 점수 (D/C)']})", 
            delta=best_keyword['최종 등급']
        )
        
        # 최적 키워드에 대한 제목 추천 기능 호출 (랜덤 조합 적용됨)
        recommend_title(best_keyword['키워드'], best_keyword['최종 등급'])

    else:
        st.error("분석할 유효한 데이터가 없습니다. 입력 형식을 확인해 주세요.")