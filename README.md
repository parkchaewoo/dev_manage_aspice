# ASPICE Process Manager

ASPICE V-model 기반 자동차 소프트웨어 개발 프로세스 관리 도구입니다.
A desktop GUI tool for managing automotive software development processes based on the ASPICE V-model.

## Features / 주요 기능

- **OEM Custom Configuration** - OEM별 프로세스 커스텀 설정 (HKMC, Volkswagen, GM 기본 탑재)
- **V-Model Visualization** - SWE.1~SWE.6 단계를 V자 다이어그램으로 시각화
- **Document Management** - 단계별 문서 생성, 상태 추적 (Draft → In Review → Approved)
- **Traceability** - 문서 간 추적성 링크 관리 (두께/색상으로 추적 양 시각화)
- **Traceability Matrix** - 단계/문서 수준 교차 참조 매트릭스
- **ASPICE Guide** - 초보자용 한국어/영어 가이드 패널
- **Skeleton Documents** - 단계별 예시 문서 템플릿 자동 생성
- **Checklist** - 단계별 산출물 체크리스트
- **Schedule** - 마일스톤 타임라인 관리
- **Document Export** - MD/HTML 문서 내보내기, 프로젝트 보고서 생성
- **Search** - 문서/요구사항/체크리스트 통합 검색
- **Backup/Restore** - 데이터 백업 및 복원 (DB/JSON)
- **Dark Mode** - 라이트/다크 테마 지원
- **Dashboard Charts** - 파이 차트, 바 차트, 게이지로 진행률 시각화
- **Deadline Alerts** - 마감일 임박/지연 알림

## Demo Projects / 데모 프로젝트

앱 최초 실행 시 3개의 데모 프로젝트가 자동 생성됩니다:
1. **HKMC > 조향 시스템** (Steering System)
2. **Volkswagen > BRAKE 시스템** (Brake System)
3. **GM > Navigation System** (네비게이션)

## Installation / 설치

```bash
# 의존성 설치
pip install PyQt5 PyYAML

# 실행
python3 main.py
```

## Project Structure / 프로젝트 구조

```
├── main.py                    # 앱 진입점
├── VERSION                    # 버전 파일
├── config/default_oem_configs/  # OEM YAML 설정 (HKMC, VW, GM)
├── templates/                 # SWE1~6 스켈레톤 문서
├── src/
│   ├── models/               # SQLite 데이터 모델 (7개)
│   ├── services/             # 비즈니스 로직 (8개)
│   ├── views/                # GUI 뷰 (13개)
│   ├── widgets/              # 커스텀 위젯 (6개)
│   └── utils/                # 유틸리티 (상수, 스타일, YAML)
└── tests/                    # 테스트 (30+개)
```

## Testing / 테스트

```bash
pip install pytest
python3 -m pytest tests/ -v
```

## Technology Stack / 기술 스택

- **Python 3.11** + **PyQt5** (Desktop GUI)
- **SQLite3** (Local Database)
- **PyYAML** (OEM Configuration)

## ASPICE V-Model

```
    SWE.1 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ SWE.6
        \                           /
         SWE.2 ─ ─ ─ ─ ─ ─ SWE.5
             \                 /
              SWE.3 ─ ─ SWE.4
```

| Stage | Development / 개발 | Verification / 검증 |
|-------|-------------------|-------------------|
| Level 1 | SWE.1 요구사항 분석 | SWE.6 적격성 시험 |
| Level 2 | SWE.2 아키텍처 설계 | SWE.5 통합 시험 |
| Level 3 | SWE.3 상세 설계/구현 | SWE.4 단위 검증 |

## License

MIT License
