import streamlit as st
import requests
import os
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="YouTube 인기 동영상",
    page_icon="🎬",
    layout="wide"
)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def get_youtube_api_key():
    """Get YouTube API key from environment variables"""
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        st.error("YouTube API 키가 설정되지 않았습니다. .env 파일에 YOUTUBE_API_KEY를 추가해주세요.")
        st.stop()
    return api_key

def format_view_count(view_count):
    """Format view count to Korean format"""
    try:
        count = int(view_count)
        if count >= 100000000:  # 1억 이상
            return f"{count//100000000}억{(count%100000000)//10000:,}만회" if count%100000000 >= 10000 else f"{count//100000000}억회"
        elif count >= 10000:  # 1만 이상
            return f"{count//10000:,}만회"
        else:
            return f"{count:,}회"
    except:
        return "조회수 정보 없음"

def get_popular_videos(api_key, max_results=30, region_code='KR', order='viewCount'):
    """Fetch popular videos from YouTube API"""
    try:
        if order == 'mostPopular':
            # YouTube Data API v3 endpoint for most popular videos
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                'part': 'snippet,statistics',
                'chart': 'mostPopular',
                'regionCode': region_code,
                'maxResults': max_results,
                'key': api_key
            }
        else:
            # YouTube Data API v3 endpoint for search with ordering
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'type': 'video',
                'regionCode': region_code,
                'maxResults': max_results,
                'order': order,
                'key': api_key
            }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'items' not in data:
            st.error("YouTube API에서 데이터를 가져올 수 없습니다.")
            return []
        
        videos = []
        for item in data['items']:
            if order == 'mostPopular':
                video = {
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'channel': item['snippet']['channelTitle'],
                    'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                    'view_count': item['statistics'].get('viewCount', '0'),
                    'published_at': item['snippet']['publishedAt'],
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
                    'view_count': '0',  # Will be updated below
                    'published_at': item['snippet']['publishedAt'],
                    'url': f"https://www.youtube.com/watch?v={video_id}"
                }
            videos.append(video)
        
        # Get statistics for search results
        if order != 'mostPopular' and videos:
            video_ids = [video['id'] for video in videos]
            stats_url = "https://www.googleapis.com/youtube/v3/videos"
            stats_params = {
                'part': 'statistics',
                'id': ','.join(video_ids),
                'key': api_key
            }
            stats_response = requests.get(stats_url, params=stats_params, timeout=10)
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                stats_dict = {item['id']: item['statistics'] for item in stats_data.get('items', [])}
                for video in videos:
                    if video['id'] in stats_dict:
                        video['view_count'] = stats_dict[video['id']].get('viewCount', '0')
        
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

def main():
    """Main Streamlit app"""
    
    # Header
    st.title("🎬 YouTube 인기 동영상")
    st.markdown("---")
    
    # Sidebar for filters
    st.sidebar.header("🔧 설정")
    
    # Country selection
    countries = {
        'KR': '🇰🇷 한국',
        'US': '🇺🇸 미국', 
        'JP': '🇯🇵 일본',
        'GB': '🇬🇧 영국',
        'DE': '🇩🇪 독일',
        'FR': '🇫🇷 프랑스',
        'CA': '🇨🇦 캐나다',
        'AU': '🇦🇺 호주'
    }
    
    selected_country = st.sidebar.selectbox(
        "국가 선택",
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
        "정렬 방식",
        options=list(sort_options.keys()),
        format_func=lambda x: sort_options[x],
        index=0
    )
    
    # Number of videos
    max_results = st.sidebar.slider(
        "동영상 개수",
        min_value=10,
        max_value=50,
        value=30,
        step=5
    )
    
    # Refresh button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 새로고침", type="primary"):
            st.rerun()
    
    with col2:
        st.markdown(f"**업데이트:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get API key
    try:
        api_key = get_youtube_api_key()
    except:
        st.stop()
    
    # Display current settings
    st.info(f"📍 **{countries[selected_country]}** | 🔄 **{sort_options[selected_order]}** | 📺 **{max_results}개 동영상**")
    
    # Fetch videos
    with st.spinner("동영상을 불러오는 중..."):
        videos = get_popular_videos(api_key, max_results, selected_country, selected_order)
    
    if not videos:
        st.warning("동영상을 불러올 수 없습니다. 잠시 후 다시 시도해주세요.")
        return
    
    # Display videos
    st.subheader(f"📺 인기 동영상 {len(videos)}개")
    
    # Create columns for responsive layout
    cols = st.columns(3)
    
    for idx, video in enumerate(videos):
        col = cols[idx % 3]
        
        with col:
            # Video card
            st.markdown(f"""
            <div style="
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
            """, unsafe_allow_html=True)
            
            # Thumbnail
            st.image(video['thumbnail'], use_container_width=True)
            
            # Title (clickable)
            st.markdown(f"**[{video['title'][:50]}{'...' if len(video['title']) > 50 else ''}]({video['url']})**")
            
            # Channel and view count
            st.markdown(f"📺 **{video['channel']}**")
            st.markdown(f"👁️ **{format_view_count(video['view_count'])}**")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit and YouTube Data API v3")

if __name__ == "__main__":
    main()
