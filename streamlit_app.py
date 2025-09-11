# 필요한 라이브러리 임포트
import os
import json
import requests
import streamlit as st
from datetime import datetime
import json

# ====================================
# 페이지 설정
# ====================================
# Streamlit 페이지 설정
st.set_page_config(
    page_title="YouTube 인기 동영상",  # 브라우저 탭 제목
    page_icon="🎬",                    # 브라우저 탭 아이콘
    layout="wide"                      # 넓은 화면 레이아웃
)

# ====================================
# 환경 변수 로드
# ====================================
from dotenv import load_dotenv
load_dotenv()  # .env 파일에서 환경 변수 로드

# ====================================
# 유틸리티 함수들
# ====================================
@st.cache_data  # API 키를 캐시하여 성능 향상
def get_youtube_api_key():
    """
    환경 변수에서 YouTube API 키를 가져오는 함수
    
    Returns:
        str: YouTube API 키
        
    Raises:
        SystemExit: API 키가 없을 경우 애플리케이션 종료
    """
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        st.error("YouTube API 키가 설정되지 않았습니다. .env 파일에 YOUTUBE_API_KEY를 추가해주세요.")
        st.stop()  # API 키가 없으면 애플리케이션 중지
    return api_key

@st.cache_data  # 자주 호출되는 함수이므로 캐싱 적용
def format_view_count(view_count):
    """
    조회수를 한국식 형식으로 포맷팅하는 함수
    
    Args:
        view_count (str or int): 포맷팅할 조회수
        
    Returns:
        str: 포맷팅된 조회수 (예: '1.2만회', '1억 2,345만회')
    """
    try:
        count = int(view_count)
        # 1억 이상인 경우
        if count >= 100000000:
            # 1억 이상 1억 1만 미만: '1억회'로 표시
            # 1억 1만 이상: '1억 1,234만회'로 표시
            return f"{count//100000000}억{(count%100000000)//10000:,}만회" if count%100000000 >= 10000 else f"{count//100000000}억회"
        # 1만 이상 1억 미만
        elif count >= 10000:
            return f"{count//10000:,}만회"
        # 1만 미만
        else:
            return f"{count:,}회"
    except (ValueError, TypeError):
        return "조회수 정보 없음"

def format_duration(duration_str):
    """
    YouTube duration을 읽기 쉬운 형태로 변환
    """
    if not duration_str:
        return ""
    
    # PT4M13S 형태를 4:13 형태로 변환
    import re
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration_str)
    
    if match:
        hours, minutes, seconds = match.groups()
        hours = int(hours) if hours else 0
        minutes = int(minutes) if minutes else 0
        seconds = int(seconds) if seconds else 0
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    return ""

def get_relative_time(published_at):
    """
    게시일을 상대적 시간으로 변환
    """
    try:
        from datetime import datetime
        published = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        now = datetime.now(published.tzinfo)
        diff = now - published
        
        if diff.days > 0:
            return f"{diff.days}일 전"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}시간 전"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}분 전"
        else:
            return "방금 전"
    except:
        return ""

# ====================================
# YouTube API 연동 함수
# ====================================
@st.cache_data(ttl=300, show_spinner=False)  # 5분간 캐시 유지, 로딩 스피너 비활성화
def get_popular_videos(api_key, max_results=30, region_code='KR', order='mostPopular'):
    """
    YouTube API를 통해 인기 동영상 목록을 가져오는 함수
    
    Args:
        api_key (str): YouTube Data API 키
        max_results (int): 가져올 동영상 수 (기본값: 30)
        region_code (str): 지역 코드 (기본값: 'KR' - 한국)
        order (str): 정렬 기준 ('mostPopular', 'date', 'viewCount', 'rating')
        
    Returns:
        list: 동영상 정보가 담긴 딕셔너리의 리스트
    """
    try:
        if order == 'mostPopular':
            # YouTube Data API v3 endpoint for most popular videos
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                'part': 'snippet,statistics,contentDetails',
                'chart': 'mostPopular',
                'regionCode': region_code,
                'maxResults': max_results,
                'key': api_key
            }
        else:
            # For other sorting options, use search with popular keywords
            search_queries = {
                'date': 'music OR gaming OR news OR entertainment',
                'viewCount': 'trending OR viral OR popular',
                'rating': 'best OR top OR amazing'
            }
            
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'type': 'video',
                'regionCode': region_code,
                'maxResults': max_results,
                'order': order,
                'q': search_queries.get(order, 'popular'),
                'key': api_key
            }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'items' not in data or len(data['items']) == 0:
            st.error(f"YouTube API에서 데이터를 가져올 수 없습니다. 응답: {data}")
            return []
        
        videos = []
        for item in data['items']:
            if order == 'mostPopular':
                video = {
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'channel': item['snippet']['channelTitle'],
                    'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                    'thumbnail_high': item['snippet']['thumbnails'].get('high', {}).get('url', item['snippet']['thumbnails']['medium']['url']),
                    'view_count': item['statistics'].get('viewCount', '0'),
                    'like_count': item['statistics'].get('likeCount', '0'),
                    'comment_count': item['statistics'].get('commentCount', '0'),
                    'published_at': item['snippet']['publishedAt'],
                    'duration': item.get('contentDetails', {}).get('duration', ''),
                    'description': item['snippet'].get('description', '')[:200] + '...' if item['snippet'].get('description', '') else '',
                    'url': f"https://www.youtube.com/watch?v={item['id']}"
                }
            else:
                # For search results, we need to get video statistics separately
                video_id = item['id']['videoId']
                video = {
                    'id': video_id,
                    'title': item['snippet']['title'],
                    'channel': item['snippet']['channelTitle'],
                    'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                    'thumbnail_high': item['snippet']['thumbnails'].get('high', {}).get('url', item['snippet']['thumbnails']['medium']['url']),
                    'view_count': '0',  # Will be updated below
                    'like_count': '0',
                    'comment_count': '0',
                    'published_at': item['snippet']['publishedAt'],
                    'duration': '',
                    'description': item['snippet'].get('description', '')[:200] + '...' if item['snippet'].get('description', '') else '',
                    'url': f"https://www.youtube.com/watch?v={video_id}"
                }
            videos.append(video)
        
        # Get statistics for search results
        if order != 'mostPopular' and videos:
            try:
                video_ids = [video['id'] for video in videos]
                stats_url = "https://www.googleapis.com/youtube/v3/videos"
                stats_params = {
                    'part': 'statistics,contentDetails',
                    'id': ','.join(video_ids),
                    'key': api_key
                }
                stats_response = requests.get(stats_url, params=stats_params, timeout=10)
                if stats_response.status_code == 200:
                    stats_data = stats_response.json()
                    if 'items' in stats_data:
                        stats_dict = {item['id']: item for item in stats_data['items']}
                        for video in videos:
                            if video['id'] in stats_dict:
                                stats = stats_dict[video['id']].get('statistics', {})
                                video['view_count'] = stats.get('viewCount', '0')
                                video['like_count'] = stats.get('likeCount', '0')
                                video['comment_count'] = stats.get('commentCount', '0')
                                video['duration'] = stats_dict[video['id']].get('contentDetails', {}).get('duration', '')
            except Exception as e:
                st.warning(f"조회수 정보를 가져오는 중 오류가 발생했습니다: {str(e)}")
        
        return videos
        
    except requests.exceptions.RequestException as e:
        st.error(f"네트워크 오류가 발생했습니다: {str(e)}")
        return []
    except json.JSONDecodeError:
        st.error("YouTube API 응답을 처리할 수 없습니다.")
        return []
    except Exception as e:
        st.error(f"예상치 못한 오류가 발생했습니다: {str(e)}")
        return []

# ====================================
# UI/UX 관련 함수
# ====================================
def set_custom_css():
    """향상된 스타일링"""
    st.markdown("""
    <style>
        /* 전체 앱 스타일 */
        .main > div {
            padding-top: 2rem;
        }
        
        /* 제목 스타일 */
        .main-title {
            background: linear-gradient(90deg, #FF0000, #FF4444);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            text-align: center;
            color: #888;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        
        /* 비디오 카드 스타일 */
        .video-card {
            background: linear-gradient(145deg, #2a2a2a, #1a1a1a);
            border-radius: 16px;
            padding: 16px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
            border: 1px solid #333;
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        
        .video-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(255,0,0,0.2);
            border-color: #FF4444;
        }
        
        /* 썸네일 스타일 */
        .thumbnail-container {
            position: relative;
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 12px;
        }
        
        .duration-badge {
            position: absolute;
            bottom: 8px;
            right: 8px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        /* 제목 스타일 */
        .video-title {
            color: #FFFFFF;
            font-size: 1.1rem;
            font-weight: 600;
            line-height: 1.4;
            margin-bottom: 8px;
            text-decoration: none;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .video-title:hover {
            color: #4CAF50;
            text-decoration: none;
        }
        
        /* 채널명 스타일 */
        .channel-name {
            color: #BBBBBB;
            font-size: 0.95rem;
            margin-bottom: 8px;
            font-weight: 500;
        }
        
        /* 통계 정보 스타일 */
        .video-stats {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
            margin-top: auto;
            padding-top: 8px;
        }
        
        .stat-item {
            color: #999;
            font-size: 0.82rem;
            display: flex;
            align-items: center;
            gap: 3px;
            background: rgba(255,255,255,0.05);
            padding: 2px 6px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        /* 카테고리 필터 */
        .category-filter {
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .category-btn {
            background: #333;
            color: white;
            border: 1px solid #555;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .category-btn:hover, .category-btn.active {
            background: #FF4444;
            border-color: #FF4444;
        }
        
        /* 반응형 디자인 */
        @media (max-width: 768px) {
            .main-title {
                font-size: 2rem;
            }
            
            .video-card {
                margin-bottom: 16px;
            }
            
            .video-stats {
                flex-direction: column;
                align-items: flex-start;
                gap: 4px;
            }
        }
        
        /* 로딩 애니메이션 */
        .loading-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
        }
        
        /* 스크롤바 스타일 */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #1a1a1a;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #333;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        
        /* 버튼 스타일 개선 */
        .stButton > button {
            background: linear-gradient(90deg, #FF4444, #FF0000);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255,68,68,0.4);
        }
        
        /* 사이드바 스타일 */
        .stSidebar {
            background: linear-gradient(180deg, #1a1a1a, #2a2a2a);
        }
        
        /* 사이드바 텍스트 색상 강제 설정 */
        .stSidebar .stMarkdown, 
        .stSidebar .stMarkdown p,
        .stSidebar .stMarkdown h1,
        .stSidebar .stMarkdown h2,
        .stSidebar .stMarkdown h3,
        .stSidebar label,
        .stSidebar .stSelectbox label,
        .stSidebar .stSlider label,
        .stSidebar div[data-testid="stMarkdownContainer"] p {
            color: #FFFFFF !important;
        }
        
        /* 셀렉트박스 드롭다운 텍스트 */
        .stSidebar .stSelectbox > div > div {
            color: #FFFFFF !important;
            background-color: #333 !important;
        }
        
        /* 슬라이더 값 텍스트 */
        .stSidebar .stSlider > div > div > div {
            color: #FFFFFF !important;
        }
        
        /* 메트릭 카드 스타일 */
        .metric-card {
            background: linear-gradient(145deg, #2a2a2a, #1a1a1a);
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid #333;
            text-align: center;
        }
        
        .metric-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #4CAF50;
        }
        
        .metric-label {
            color: #888;
            font-size: 0.9rem;
        }
    </style>
    """, unsafe_allow_html=True)

def create_video_card(video, rank=None):
    """개선된 비디오 카드 생성"""
    duration = format_duration(video['duration'])
    relative_time = get_relative_time(video['published_at'])
    
    # 제목 길이 제한
    title = video['title']
    if len(title) > 60:
        title = title[:60] + "..."
    
    # 채널명 길이 제한
    channel = video['channel']
    if len(channel) > 25:
        channel = channel[:25] + "..."
    
    return f"""
    <div class="video-card">
        <div class="thumbnail-container">
            <img src="{video['thumbnail_high']}" 
                 style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px;" 
                 loading="lazy">
            {f'<div class="duration-badge">{duration}</div>' if duration else ''}
            {f'<div class="duration-badge" style="top: 8px; right: 8px; bottom: auto; background: #FF4444;">#{rank}</div>' if rank else ''}
        </div>
        
        <a href="{video['url']}" target="_blank" class="video-title">
            {title}
        </a>
        
        <div class="channel-name">
            📺 {channel}
        </div>
        
        <div class="video-stats">
            <div class="stat-item">
                <span>👁️</span>
                <span>{format_view_count(video['view_count'])}</span>
            </div>
            <div class="stat-item">
                <span>👍</span>
                <span>{format_view_count(video['like_count'])}</span>
            </div>
            <div class="stat-item">
                <span>💬</span>
                <span>{format_view_count(video['comment_count'])}</span>
            </div>
            {f'<div class="stat-item"><span>🕐</span><span>{relative_time}</span></div>' if relative_time else ''}
        </div>
    </div>
    """

# ====================================
# 메인 애플리케이션
# ====================================
def main():
    """
    Streamlit 메인 애플리케이션 함수
    
    사용자 인터페이스를 구성하고 이벤트를 처리합니다.
    """
    # 커스텀 CSS 적용
    set_custom_css()
    
    # 헤더 영역
    st.markdown("""
    <h1 class="main-title">🎬 YouTube 인기 동영상</h1>
    <p class="subtitle">실시간으로 업데이트되는 인기 동영상을 확인하세요</p>
    """, unsafe_allow_html=True)
    
    # ==============================
    # 사이드바 설정
    # ==============================
    st.sidebar.markdown("### 🔧 설정")
    
    # 국가 선택 옵션
    countries = {
        'KR': '🇰🇷 한국',  # 대한민국
        'US': '🇺🇸 미국',  # 미국
        'JP': '🇯🇵 일본',  # 일본
        'GB': '🇬🇧 영국',  # 영국
        'DE': '🇩🇪 독일',  # 독일
        'FR': '🇫🇷 프랑스', # 프랑스
        'CA': '🇨🇦 캐나다', # 캐나다
        'AU': '🇦🇺 호주'   # 호주
    }
    
    selected_country = st.sidebar.selectbox(
        "📍 국가 선택",
        options=list(countries.keys()),
        format_func=lambda x: countries[x],
        index=0
    )
    
    # Sort order selection
    sort_options = {
        'mostPopular': '📈 인기순',
        'date': '📅 최신순',
        'viewCount': '👁️ 조회수순',
        'rating': '⭐ 평점순'
    }
    
    selected_order = st.sidebar.selectbox(
        "🔄 정렬 방식",
        options=list(sort_options.keys()),
        format_func=lambda x: sort_options[x],
        index=0
    )
    
    # Number of videos
    max_results = st.sidebar.slider(
        "📺 동영상 개수",
        min_value=10,
        max_value=50,
        value=30,
        step=5
    )
    
    # 레이아웃 선택
    layout_options = {
        3: "📱 모바일 (3열)",
        4: "💻 데스크톱 (4열)",
        2: "📺 대형 화면 (2열)"
    }
    
    selected_layout = st.sidebar.selectbox(
        "🖥️ 레이아웃",
        options=list(layout_options.keys()),
        format_func=lambda x: layout_options[x],
        index=1
    )
    
    st.sidebar.markdown("---")
    
    # Refresh button with cache clearing
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔄 새로고침", type="primary", use_container_width=True):
            # 캐시를 지우고 새로운 데이터를 가져오기 위해 캐시 키를 변경
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        if st.button("❤️ 즐겨찾기", use_container_width=True):
            st.success("즐겨찾기에 추가됨!")
    
    # API 호출 매개변수 표시 (디버깅용)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 현재 설정")
    st.sidebar.markdown(f"**국가:** {countries[selected_country]}")
    st.sidebar.markdown(f"**정렬:** {sort_options[selected_order]}")
    st.sidebar.markdown(f"**개수:** {max_results}개")
    st.sidebar.markdown(f"**레이아웃:** {layout_options[selected_layout]}")
    
    # 업데이트 시간 표시
    st.sidebar.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">마지막 업데이트</div>
        <div style="color: #4CAF50; font-size: 0.9rem;">
            {datetime.now().strftime('%H:%M:%S')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get API key
    try:
        api_key = get_youtube_api_key()
    except:
        st.stop()
    
    # 현재 설정 표시
    st.info(f"📍 **{countries[selected_country]}** | 🔄 **{sort_options[selected_order]}** | 📺 **{max_results}개 동영상** | 🖥️ **{layout_options[selected_layout]}**")
    
    # Fetch videos with progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("동영상 데이터를 가져오는 중...")
    progress_bar.progress(25)
    
    videos = get_popular_videos(api_key, max_results, selected_country, selected_order)
    
    progress_bar.progress(75)
    status_text.text("동영상 목록을 준비하는 중...")
    
    if not videos:
        progress_bar.empty()
        status_text.empty()
        st.warning("🚫 동영상을 불러올 수 없습니다. 잠시 후 다시 시도해주세요.")
        return
    
    progress_bar.progress(100)
    status_text.text("완료!")
    
    # 잠시 후 프로그레스 바 제거
    import time
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()
    
    # ==============================
    # 통계 정보 표시
    # ==============================
    col1, col2, col3, col4 = st.columns(4)
    
    total_views = sum(int(video['view_count']) for video in videos if video['view_count'].isdigit())
    total_likes = sum(int(video['like_count']) for video in videos if video['like_count'].isdigit())
    total_comments = sum(int(video['comment_count']) for video in videos if video['comment_count'].isdigit())
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(videos)}</div>
            <div class="metric-label">총 동영상</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{format_view_count(str(total_views))}</div>
            <div class="metric-label">총 조회수</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{format_view_count(str(total_likes))}</div>
            <div class="metric-label">총 좋아요</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{format_view_count(str(total_comments))}</div>
            <div class="metric-label">총 댓글</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==============================
    # 동영상 목록 표시
    # ==============================
    st.markdown(f"### 📺 인기 동영상 Top {len(videos)}")
    
    # 검색 기능 추가
    search_term = st.text_input("🔍 동영상 검색", placeholder="제목이나 채널명으로 검색하세요...")
    
    # 검색 필터링
    if search_term:
        filtered_videos = [
            video for video in videos 
            if search_term.lower() in video['title'].lower() or 
               search_term.lower() in video['channel'].lower()
        ]
        if filtered_videos:
            st.success(f"🎯 '{search_term}'에 대한 검색 결과: {len(filtered_videos)}개")
        else:
            st.warning(f"🚫 '{search_term}'에 대한 검색 결과가 없습니다.")
    else:
        filtered_videos = videos
    
    # 반응형 그리드 레이아웃 생성
    cols = st.columns(selected_layout)
    
    for idx, video in enumerate(filtered_videos):
        col = cols[idx % selected_layout]
        
        with col:
            # 순위 표시 (검색 시에는 표시하지 않음)
            rank = idx + 1 if not search_term else None
            
            # 카드 스타일 컨테이너
            with st.container():
                # 썸네일 이미지
                st.image(video['thumbnail_high'], use_container_width=True)
                
                # 순위 배지 (있는 경우)
                if rank:
                    st.markdown(f"<div style='text-align: center; background: #FF4444; color: white; padding: 2px 8px; border-radius: 12px; margin: 5px 0; font-size: 0.8rem; font-weight: bold;'>#{rank}</div>", unsafe_allow_html=True)
                
                # 제목 처리
                title = video['title']
                if len(title) > 50:
                    title = title[:47] + "..."
                
                # 제목 링크
                st.markdown(f"**[{title}]({video['url']})**")
                
                # 채널명
                channel = video['channel']
                if len(channel) > 25:
                    channel = channel[:22] + "..."
                st.markdown(f"📺 *{channel}*")
                
                # 통계 정보 처리
                view_count = int(video['view_count']) if video['view_count'].isdigit() else 0
                like_count = int(video['like_count']) if video['like_count'].isdigit() else 0
                comment_count = int(video['comment_count']) if video['comment_count'].isdigit() else 0
                relative_time = get_relative_time(video['published_at'])
                
                # 비현실적인 데이터 필터링
                if like_count > view_count and view_count > 0:
                    like_count = 0
                
                # 상대 시간 처리
                if relative_time and "일 전" in relative_time:
                    try:
                        days = int(relative_time.split("일")[0])
                        if days > 365:
                            relative_time = f"{days // 365}년 전"
                    except:
                        pass
                
                # 통계 정보를 간단한 텍스트로 표시
                stats_parts = []
                stats_parts.append(f"👁️ {format_view_count(str(view_count))}")
                
                if like_count > 0:
                    stats_parts.append(f"👍 {format_view_count(str(like_count))}")
                
                if comment_count > 0:
                    stats_parts.append(f"💬 {format_view_count(str(comment_count))}")
                
                if relative_time:
                    stats_parts.append(f"🕐 {relative_time}")
                
                # 통계 정보 표시
                stats_text = " | ".join(stats_parts)
                st.markdown(f"<small style='color: #888;'>{stats_text}</small>", unsafe_allow_html=True)
                
                # 구분선
                st.markdown("---")
    
    # ==============================
    # 푸터 영역
    # ==============================
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    
    # 통계 및 정보
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📊 데이터 소스**
        - YouTube Data API v3
        - 실시간 업데이트
        - 지역별 인기 동영상
        """)
    
    with col2:
        st.markdown("""
        **🛠️ 주요 기능**
        - 반응형 디자인
        - 다양한 정렬 옵션
        - 검색 및 필터링
        """)
    
    with col3:
        st.markdown("""
        **🎨 사용자 경험**
        - 다크 모드 디자인
        - 부드러운 애니메이션
        - 모바일 최적화
        """)
    
    # 푸터
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; color: #666; border-top: 1px solid #333; margin-top: 2rem;">
        <p style="margin: 0; font-size: 1.1rem;">
            ✨ <strong>YouTube 인기 동영상</strong>으로 최신 트렌드를 놓치지 마세요! ✨
        </p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
            Streamlit ❤️ YouTube Data API v3로 제작 | © 2024 All rights reserved
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()