# 🎬 YouTube 인기 동영상

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.7+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![YouTube API](https://img.shields.io/badge/YouTube_API-FF0000?logo=youtube&logoColor=white)](https://developers.google.com/youtube/v3)

> 실시간으로 업데이트되는 YouTube 인기 동영상을 확인할 수 있는 웹 애플리케이션입니다. 다크 모드와 반응형 디자인으로 어떤 기기에서나 쾌적하게 이용하실 수 있습니다.

## ✨ 주요 기능

- 🌍 **국가별 인기 동영상** - 한국, 미국, 일본 등 다양한 국가의 인기 동영상 확인
- 🔍 **다양한 정렬 옵션** - 인기순, 최신순, 조회수순, 평점순으로 정렬
- 🎨 **개선된 다크 모드** - 가독성 향상을 위한 최적화된 다크 테마
- 📊 **상세 통계** - 총 조회수, 좋아요 수, 댓글 수 등 종합 통계 제공
- 🔎 **검색 기능** - 제목이나 채널명으로 원하는 동영상 검색
- 🖥️ **반응형 레이아웃** - 2~4열 그리드로 다양한 화면 크기에 최적화
- ⏱️ **실시간 업데이트** - 마지막 업데이트 시간 표시 및 수동 새로고침
- 📱 **모바일 최적화** - 모바일 기기에서도 쾌적한 사용 경험
- 🔄 **즉각적인 새로고침** - 캐시 초기화 기능으로 항상 최신 데이터 유지

## 🖥️ 데모

[![Demo Video](https://img.youtube.com/vi/YOUR_VIDEO_ID/0.jpg)](https://youtu.be/YOUR_VIDEO_ID)

> 데모 영상을 보려면 이미지를 클릭하세요.

## 🚀 시작하기

### 필수 조건

- Python 3.7 이상
- YouTube Data API v3 키

### 설치 방법

1. 저장소 클론
   ```bash
   git clone https://github.com/yourusername/Youtube_Program25.git
   cd Youtube_Program25
   ```

2. 가상 환경 생성 및 활성화 (권장)
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```

4. 환경 변수 설정
   - `.env` 파일을 생성하고 YouTube API 키를 설정하세요.
   ```env
   YOUTUBE_API_KEY=여기에_당신의_API_키를_입력하세요
   ```

### 실행 방법

```bash
streamlit run streamlit_app.py
```

## 🛠️ 사용 방법

1. 왼쪽 사이드바에서 원하는 국가를 선택하세요.
2. 정렬 방식을 선택하세요 (인기순, 최신순, 조회수순, 평점순).
3. 표시할 동영상의 개수를 조정하세요 (10~50개).
4. 원하는 레이아웃을 선택하세요 (2~4열).
5. 검색창을 사용하여 특정 동영상이나 채널을 찾아보세요.
6. 새로고침 버튼으로 최신 정보를 즉시 업데이트하세요.
7. 각 동영상 카드를 클릭하면 YouTube에서 바로 시청할 수 있습니다.

## 🎨 UI/UX 개선 사항

### 개선된 비디오 카드
- **모던한 카드 디자인**: 부드러운 그림자와 둥근 모서리로 세련된 디자인
- **호버 효과**: 마우스 오버 시 미세한 애니메이션과 그림자 강조
- **통계 배지**: 조회수, 좋아요, 댓글 수를 깔끔한 배지로 표시
- **상대적 시간 표시**: '방금 전', '5분 전' 등 직관적인 시간 표기

### 사용자 경험
- **즉각적인 피드백**: 버튼 클릭 및 상호작용 시 즉각적인 시각적 피드백
- **로딩 상태 표시**: 데이터 로딩 중 진행 상황을 명확히 표시
- **반응형 디자인**: 데스크톱, 태블릿, 모바일 등 모든 기기에서 최적화된 레이아웃
- **접근성 향상**: 색상 대비 개선 및 키보드 네비게이션 지원

### 사이드바 개선
- **현재 설정 표시**: 선택한 국가, 정렬 방식 등 현재 설정을 한눈에 확인
- **직관적인 컨트롤**: 사용하기 쉬운 슬라이더와 드롭다운 메뉴
- **빠른 새로고침**: 캐시 초기화 기능으로 항상 최신 데이터 유지

## 🛠 기술 스택

### 핵심 기술
- **프론트엔드**: [Streamlit](https://streamlit.io/)
- **백엔드**: [Python](https://www.python.org/)
- **API**: [YouTube Data API v3](https://developers.google.com/youtube/v3)

### 주요 라이브러리
- **데이터 처리**: pandas, numpy
- **HTTP 요청**: requests
- **환경 변수 관리**: python-dotenv
- **날짜/시간 처리**: datetime, pytz

### 스타일링
- **CSS3**: 커스텀 스타일링 및 애니메이션
- **반응형 디자인**: 미디어 쿼리를 활용한 다양한 화면 크기 대응
- **다크 모드**: 사용자 친화적인 다크 테마

### 성능 최적화
- **캐싱**: 자주 사용되는 데이터 캐싱으로 성능 향상
- **지연 로딩**: 이미지 및 리소스의 지연 로딩
- **비동기 처리**: 네트워크 요청의 비동기 처리로 반응성 향상

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📱 모바일 지원

이 애플리케이션은 모바일 기기에서도 완벽하게 작동하도록 최적화되었습니다.

### 모바일에서의 주요 기능
- **터치 최적화**: 버튼과 컨트롤이 터치에 최적화됨
- **반응형 레이아웃**: 세로/가로 모드 모두 지원
- **빠른 로딩**: 모바일 네트워크 환경을 고려한 최적화
- **오프라인 지원**: 일부 기능은 오프라인에서도 작동

## 🤝 기여

기여는 언제나 환영합니다! 버그 리포트나 기능 요청은 이슈를 통해 제출해 주세요.

1. 이 저장소를 포크하세요.
2. 기능 브랜치를 만드세요 (`git checkout -b feature/AmazingFeature`).
3. 변경사항을 커밋하세요 (`git commit -m 'Add some AmazingFeature'`).
4. 브랜치에 푸시하세요 (`git push origin feature/AmazingFeature`).
5. 풀 리퀘스트를 오픈하세요.

## 📧 연락처

프로젝트 관련 문의사항이 있으시면 아래로 연락주세요:

- 이메일: your.email@example.com
- GitHub: [@yourusername](https://github.com/yourusername)

---

<div align="center">
  <sub>만든이: Your Name</sub>
</div>