# 사운드 파일 안내

이 폴더에 BGM과 효과음 파일을 넣으면 자동으로 게임에 적용됩니다.

## 폴더 구조

- `bgm/`: 배경음악 파일을 넣으세요

  - 지원 형식: .ogg, .wav, .mp3
  - 첫 번째 파일이 자동으로 재생됩니다

- `sfx/`: 효과음 파일을 넣으세요
  - 지원 형식: .ogg, .wav, .mp3
  - 파일명(확장자 제외)으로 재생할 수 있습니다
  - 예: `enter.ogg` → `sound_manager.play_sfx('enter')`
  - 예: `itempickup.wav` → `sound_manager.play_sfx('itempickup')`

## 사용 예시

게임에서 사용되는 효과음:

- `enter`: 버튼 클릭, 문 열림 등
- `itempickup`: 아이템 획득 시

필요에 따라 추가 효과음을 넣고 코드에서 `sound_manager.play_sfx('파일명')`으로 호출하세요.
