# 폰트 사용 가이드

## 개요

이 게임은 **영어와 한글을 자동으로 감지**하여 적절한 폰트를 사용합니다:
- **영어**: 피코파크 스타일의 기본 폰트 사용 (깔끔하고 레트로 느낌)
- **한글**: 굵고 선명한 한글 폰트 사용

## 외부 폰트 파일 사용 방법

### 1. 폰트 파일 준비
1. 한글 폰트 파일(.ttf)을 다운로드합니다
   - 권장: 나눔고딕 Bold (https://hangeul.naver.com/2017/nanum)

### 2. 폰트 파일 설치
```
프로젝트 루트/
  └── fonts/
      ├── NanumGothic-Bold.ttf  (권장)
      └── NanumGothic.ttf
```

### 3. 자동 감지
게임이 실행될 때 자동으로 `fonts` 폴더에서 폰트 파일을 찾습니다.

## 폰트 우선순위

### 1순위: 외부 폰트 파일 (프로젝트/fonts/)
- `NanumGothic-Bold.ttf` ⭐ 권장
- `NanumGothic.ttf`
- `NanumBarunGothic-Bold.ttf`
- `NotoSansKR-Bold.ttf`

### 2순위: 시스템 폰트

**macOS:**
- AppleGothic
- NanumGothic Bold
- Apple SD Gothic Neo

**Windows:**
- Malgun Gothic Bold (맑은 고딕)
- NanumGothic Bold

**Linux:**
- NanumGothic Bold
- Noto Sans CJK KR Bold

### 3순위: 기본 폰트
- 시스템 폰트를 찾을 수 없을 때 사용 (한글이 깨질 수 있음)

## 크로스 플랫폼 확인

✅ **Windows**: 
- 맑은 고딕 자동 사용 (폰트 파일 없어도 작동)
- 외부 폰트 파일 추가 시 동일 폰트 보장

✅ **macOS**:
- AppleGothic 자동 사용 (폰트 파일 없어도 작동)
- 외부 폰트 파일 추가 시 동일 폰트 보장

## 작동 방식

게임은 텍스트를 렌더링할 때 자동으로:
1. 텍스트에 한글이 포함되어 있는지 확인
2. 한글이 있으면 → 한글 폰트 사용
3. 영어만 있으면 → 피코파크 스타일 기본 폰트 사용

## 예시

```python
# 한글 텍스트 → 자동으로 한글 폰트 사용
draw_text_center(screen, "정말 종료하시겠습니까?", font, ...)

# 영어 텍스트 → 자동으로 기본 폰트 사용 (피코파크 스타일)
draw_text_center(screen, "GAME START", font, ...)

# 버튼도 자동 감지
button = Button(100, 100, 200, 50, "게임 시작")  # 한글 폰트
button = Button(100, 100, 200, 50, "START")      # 기본 폰트
```

## 문제 해결

### 한글이 깨질 때
1. `fonts` 폴더에 `NanumGothic-Bold.ttf` 파일 추가
2. 또는 시스템에 나눔고딕 폰트 설치

### 폰트가 너무 얇을 때
- Bold 버전의 폰트 파일 사용 (예: `NanumGothic-Bold.ttf`)

### 버튼 텍스트가 밖으로 나갈 때
- 버튼 크기 조정 또는 폰트 크기 조정

