# KGU_python_programming_project
# DUMB N DUMBERS 

간단한 플랫폼 퍼즐을 파이썬과 Pygame으로 구현을 목표로 하는 프로젝트입니다.  
플레이어가 열쇠를 획득해 문을 열고, 스테이지를 클리어하는 방식입니다.

## 프로젝트 구조

`game/` 폴더에 실행 및 모듈 파일이 정리되어 있습니다.

- `game/main.py` – 게임 루프와 상태 전환, UI를 담당하는 메인 스크립트
- `game/config.py` – 화면 크기, FPS, 색상 등 공통 설정
- `game/entities.py` – `Player`, `KeyObj`, `Door` 등 게임 오브젝트
- `game/stages.py` – 스테이지별 플랫폼 데이터와 오브젝트 초기화
- `game/ui.py` – 버튼, 슬라이더, 텍스트 렌더링 유틸

## 실행 방법

1. Python 3.10 이상과 `pygame`이 설치되어 있어야 합니다.
   ```bash
   pip install pygame
   ```
2. 프로젝트 루트에서 아래 명령으로 실행합니다.
   ```bash
   python game/07main.py
   ```

## 조작법

- 방향키 ←/→ : 이동
- 방향키 ↑ : 점프
- 방향키 ↓ : 문 앞에서 상호작용
- ESC : 게임 ↔ 옵션 화면 전환 (다른 화면에서는 메인 메뉴로 이동)

##라이선스