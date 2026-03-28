# Unit Test Plan
# 단위 시험 계획서

---

<!-- GUIDE: 이 문서는 SWE.4 단위 시험의 전략, 도구, 커버리지 목표, 일정을 정의합니다. -->
<!-- GUIDE: This document defines unit test strategy, tools, coverage targets, and schedule for SWE.4. -->

| Field / 항목 | Value / 값 |
|---|---|
| Project Name / 프로젝트명 | {project_name} |
| OEM | {oem_name} |
| Document ID / 문서 ID | {document_id} |
| Version / 버전 | 0.1 |
| Date / 작성일 | {date} |
| Author / 작성자 | |
| Reviewer / 검토자 | |
| Approval / 승인자 | |
| Status / 상태 | Draft |
| Classification / 기밀등급 | Confidential |

---

## Revision History / 개정 이력

| Version | Date | Author | Description / 설명 |
|---------|------|--------|-------------------|
| 0.1 | {date} | | Initial draft / 초안 작성 |
| | | | |

---

## 1. Introduction / 소개

### 1.1 Purpose / 목적
본 문서는 {project_name} 프로젝트의 단위 시험 계획을 정의합니다.
This document defines the unit test plan for the {project_name} project.

### 1.2 Scope / 범위
- All software components defined in SWE.3 detailed design
- 모든 SWE.3 상세 설계에 정의된 소프트웨어 컴포넌트

### 1.3 References / 참조 문서

| ID | Document / 문서 | Version |
|---|---|---|
| REF-01 | SWE.3 Detailed Design Document | |
| REF-02 | {oem_name} Test Standard | |
| REF-03 | ISO 26262-6 Clause 9 (Unit Testing) | 2018 |

---

## 2. Test Strategy / 시험 전략

### 2.1 Test Approach / 시험 접근 방식

| Aspect / 측면 | Description / 설명 |
|---|---|
| Test Level / 시험 수준 | Unit (Function/Module level) / 단위 (함수/모듈 수준) |
| Test Type / 시험 유형 | White-box + Black-box / 화이트박스 + 블랙박스 |
| Test Basis / 시험 기준 | SWE.3 Detailed Design / SWE.3 상세 설계 |
| Test Environment / 시험 환경 | Host PC (x86) + Target (if needed) |
| Execution Method / 실행 방법 | Automated (CI/CD pipeline) / 자동화 |

### 2.2 Test Techniques / 시험 기법

| Technique / 기법 | Description / 설명 | Application / 적용 |
|---|---|---|
| Equivalence Partitioning | 동치 분할 | All input parameters |
| Boundary Value Analysis | 경계값 분석 | Numeric inputs |
| Statement Coverage | 구문 커버리지 | All functions |
| Branch/Decision Coverage | 분기 커버리지 | All functions |
| MC/DC Coverage | MC/DC 커버리지 | ASIL B-D functions |
| Error Guessing | 오류 추측 | Complex logic |

---

## 3. Test Tools / 시험 도구

| Tool / 도구 | Version | Purpose / 용도 | License |
|---|---|---|---|
| Google Test / Unity | - | Test framework / 시험 프레임워크 | OSS |
| Cantata / VectorCAST | - | Unit test execution / 단위 시험 실행 | Commercial |
| gcov / lcov | - | Code coverage measurement / 코드 커버리지 측정 | OSS |
| CMock / fff | - | Mock/Stub generation / Mock/Stub 생성 | OSS |
| Jenkins / GitLab CI | - | CI/CD automation / CI/CD 자동화 | - |

---

## 4. Coverage Targets / 커버리지 목표

| ASIL Level | Statement | Branch/Decision | MC/DC | Function |
|---|---|---|---|---|
| QM | ≥ 80% | ≥ 70% | N/A | 100% |
| ASIL A | ≥ 90% | ≥ 80% | N/A | 100% |
| ASIL B | ≥ 95% | ≥ 90% | ≥ 80% | 100% |
| ASIL C | ≥ 95% | ≥ 95% | ≥ 90% | 100% |
| ASIL D | 100% | 100% | ≥ 95% | 100% |

---

## 5. Test Scope / 시험 범위

### 5.1 Modules to Test / 시험 대상 모듈

| Module / 모듈 | ASIL | Functions | Priority | Assigned To |
|---|---|---|---|---|
| SWC_SensorProc | B | 24 | High | |
| SWC_TorqueCalc | B | 18 | High | |
| SWC_SafetyMonitor | D | 32 | Critical | |
| SWC_MotorCtrl | B | 20 | High | |
| SWC_Diagnostics | QM | 28 | Medium | |
| SWC_Communication | A | 14 | Medium | |

### 5.2 Out of Scope / 시험 범위 외

| Item / 항목 | Reason / 사유 |
|---|---|
| AUTOSAR BSW modules | Tested by BSW supplier |
| Third-party libraries | Qualified separately |
| Hardware drivers (MCAL) | Tested at integration level |

---

## 6. Test Schedule / 시험 일정

| Phase / 단계 | Start Date / 시작일 | End Date / 종료일 | Deliverable / 산출물 |
|---|---|---|---|
| Test Plan Review / 시험 계획 검토 | | | Approved test plan |
| Test Case Design / 시험 케이스 설계 | | | Test specifications |
| Test Environment Setup / 시험 환경 구축 | | | Configured environment |
| Test Execution / 시험 실행 | | | Test results |
| Coverage Analysis / 커버리지 분석 | | | Coverage report |
| Test Report / 시험 보고서 | | | Final test report |

---

## 7. Entry/Exit Criteria / 시작/종료 기준

### 7.1 Entry Criteria / 시작 기준

| # | Criteria / 기준 | Check |
|---|---|---|
| 1 | SWE.3 detailed design approved / SWE.3 상세 설계 승인됨 | ☐ |
| 2 | Test environment ready / 시험 환경 준비됨 | ☐ |
| 3 | Source code compiled without errors / 소스코드 컴파일 오류 없음 | ☐ |
| 4 | Test plan approved / 시험 계획 승인됨 | ☐ |

### 7.2 Exit Criteria / 종료 기준

| # | Criteria / 기준 | Check |
|---|---|---|
| 1 | All planned test cases executed / 모든 계획된 시험 케이스 실행됨 | ☐ |
| 2 | Coverage targets met / 커버리지 목표 달성 | ☐ |
| 3 | No critical defects open / 심각 결함 미해결 없음 | ☐ |
| 4 | Test report reviewed and approved / 시험 보고서 검토 및 승인됨 | ☐ |

---

## 8. Review Criteria / 검토 기준

| # | Criteria / 기준 | Check |
|---|---|---|
| 1 | All modules in scope identified / 모든 시험 대상 모듈 식별됨 | ☐ |
| 2 | Coverage targets defined per ASIL level / ASIL 수준별 커버리지 목표 정의됨 | ☐ |
| 3 | Test tools qualified / 시험 도구 자격 확인됨 | ☐ |
| 4 | Schedule is realistic / 일정이 현실적임 | ☐ |
| 5 | Entry/exit criteria defined / 시작/종료 기준 정의됨 | ☐ |
| 6 | Compliant with {oem_name} test requirements / OEM 시험 요구사항 준수 | ☐ |

---

## 9. Review History / 검토 이력

| Date / 날짜 | Reviewer / 검토자 | Result / 결과 | Comments / 비고 |
|---|---|---|---|
| | | Approved / Rejected | |

---

*Generated by ASPICE Process Manager*
