# ASPICE Process Manager

ASPICE V-model 기반 자동차 소프트웨어 개발 프로세스 관리 도구입니다.
A desktop GUI tool for managing automotive software development processes based on the ASPICE V-model.

## Features / 주요 기능

### Core / 핵심 기능
- **OEM Configuration** - OEM별 프로세스 커스텀 설정 (HKMC, Volkswagen, GM 기본 탑재)
- **Development Phase Management** - OEM별 개발 단계 관리 (HKMC: Mcar/P1/P2/Pilot/SOP, VW: A~C-Muster/SOP, GM: DV/PV/PP/MP)
- **Phase Inheritance** - 이전 Phase의 Approved 문서/체크리스트/추적성 자동 상속
- **Complete & Advance** - Phase 완료 후 다음 단계 자동 전환
- **V-Model Visualization** - SWE.1~SWE.6 V자 다이어그램 (V-model 쌍 + 순차적 추적성)
- **Sequential Traceability** - SWE.1→SWE.2→SWE.3 순차적 도출(derives) 추적

### Document Management / 문서 관리
- **Rich Content Editor** - 마크다운 에디터로 문서 본문 직접 작성
- **Auto Skeleton Loading** - 문서 생성 시 SWE 단계별 스켈레톤 템플릿 자동 로드
- **14 Document Templates** - SRS, SAD, SDD, 시험계획/보고서, 추적매트릭스, 릴리스노트 등
- **Document Status Workflow** - Draft → In Review → Approved 상태 관리
- **Document Version History** - 저장 시 자동 스냅샷, 이전 버전 조회
- **Auto ID Generation** - 요구사항 ID 자동 채번 (SWE1-REQ-001 형식)
- **Document Export** - MD/HTML 내보내기

### ASPICE Evidence / ASPICE 증빙
- **Review Records** - 리뷰 회의록 (참석자, 지적사항, 조치항목, 결정사항)
- **Test Results** - 시험 결과 데이터 (Pass/Fail, Statement/Branch/MC-DC 커버리지)
- **File Attachments** - 외부 파일 첨부 (시험 로그, 커버리지 리포트 등)
- **Checklist** - 단계별 산출물 체크리스트 (N/A 제외 기능 포함)
- **ASPICE Compliance Report** - HTML 증빙 리포트 (갭 분석, V-model 추적성 포함)

### UX / 사용자 경험
- **ASPICE Beginner Guide** - 초보자용 한국어/영어 가이드 패널
- **Workflow Warning** - SWE 단계 순서 미준수 시 경고
- **Dashboard Charts** - 파이 차트, 바 차트, 게이지
- **Deadline Alerts** - 마감일 임박/지연 마일스톤 알림
- **Search** - 문서/체크리스트 통합 검색
- **Dark Mode** - 라이트/다크 테마
- **Backup/Restore** - DB 백업, JSON 내보내기/가져오기
- **Reset Demo Data** - 데모 프로젝트 초기화

## Demo Projects / 데모 프로젝트

| OEM | Project | Phases | Status |
|-----|---------|--------|--------|
| HKMC | 조향 시스템 (Steering) | Mcar (100% 완료) → P1 (진행중) | ASPICE 모범 사례 |
| Volkswagen | BRAKE System | A-Muster (완료) → B-Muster (진행중) | Phase 상속 예시 |
| GM | Navigation System | DV (시작) | 초기 단계 |

## Installation / 설치

```bash
pip install PyQt5 PyYAML
python3 main.py
```

## Project Structure / 프로젝트 구조

```
├── main.py                    # 앱 진입점
├── VERSION                    # 버전 (0.6.0)
├── config/default_oem_configs/  # OEM YAML 설정
├── templates/                 # 14개 문서 템플릿
├── src/
│   ├── models/     (10개)    # DB 모델 (OEM, Project, Phase, Stage, Document, ...)
│   ├── services/   (12개)    # 비즈니스 로직
│   ├── views/      (21개)    # GUI 뷰
│   ├── widgets/    (6개)     # 커스텀 위젯
│   └── utils/      (3개)     # 상수, 스타일, YAML
└── tests/          (5개)     # 테스트
```

## Testing / 테스트

```bash
pip install pytest
python3 -m pytest tests/ -v
```

## ASPICE Coverage / ASPICE 커버리지

| Process Area | Coverage | Description |
|---|---|---|
| SWE.1 Requirements | ✅ Full | 요구사항 문서, 추적성, 리뷰 |
| SWE.2 Architecture | ✅ Full | 아키텍처 설계, 인터페이스 |
| SWE.3 Detailed Design | ✅ Full | 상세 설계, 코딩 가이드라인 |
| SWE.4 Unit Verification | ✅ Full | 단위 시험, 커버리지 기록 |
| SWE.5 Integration Test | ✅ Full | 통합 시험, 리소스 측정 |
| SWE.6 Qualification Test | ✅ Full | 적격성 시험, 릴리스 기준 |
| V-Model Traceability | ✅ Full | 쌍 + 순차 추적성 |
| Phase Management | ✅ Full | OEM별 Phase, 상속 |
| Evidence Management | ✅ Full | 리뷰, 시험결과, 첨부 |

## DB Location / DB 위치
- Mac: `~/.aspice_manager/aspice_manager.db`
- Windows: `%USERPROFILE%\.aspice_manager\aspice_manager.db`

## License
MIT License
