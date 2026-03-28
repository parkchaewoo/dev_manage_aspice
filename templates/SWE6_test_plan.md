# Qualification Test Plan
# 적격성 시험 계획서

---

<!-- GUIDE: 이 문서는 SWE.6 적격성 시험의 범위, 환경, 합격/불합격 기준을 정의합니다. -->
<!-- GUIDE: This document defines qualification test scope, environment, and pass/fail criteria for SWE.6. -->

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
본 문서는 {project_name} 프로젝트의 적격성 시험 계획을 정의합니다.
This document defines the qualification test plan for the {project_name} project.

적격성 시험은 소프트웨어가 SWE.1에서 정의된 요구사항을 충족하는지 검증합니다.
Qualification testing verifies that the software meets requirements defined in SWE.1.

### 1.2 Test Scope / 시험 범위

| Category / 분류 | In Scope / 범위 내 | Out of Scope / 범위 외 |
|---|---|---|
| Functional Requirements | All SWE.1 requirements | HW-only requirements |
| Non-Functional Requirements | Performance, timing | Environmental tests |
| Safety Requirements | All ASIL requirements | HW safety mechanisms |
| Interface Requirements | CAN, sensor, actuator | Physical layer tests |

---

## 2. Test Environment / 시험 환경

### 2.1 Hardware Configuration / 하드웨어 구성

| Component / 구성요소 | Specification / 사양 | Quantity / 수량 |
|---|---|---|
| Target ECU | Production sample (ES2+) | 2 |
| HIL System | dSPACE SCALEXIO / ETAS LABCAR | 1 |
| CAN Interface | Vector VN1610 | 2 |
| Power Supply | Programmable 6-18V, 20A | 1 |
| Load Box | Project-specific sensor/actuator sim | 1 |
| Data Logger | Vector GL4000 / ETAS ES600 | 1 |

### 2.2 Software Configuration / 소프트웨어 구성

| Tool / 도구 | Version | Purpose / 용도 |
|---|---|---|
| CANoe / CANalyzer | - | Test execution and CAN analysis |
| MATLAB/Simulink | R2023b | Plant model and test automation |
| Python | 3.11+ | Test script automation |
| Test Management | DOORS / Polarion / Jira | Test case management |

---

## 3. Test Cases / 시험 케이스

### 3.1 Test Case Summary / 시험 케이스 요약

| Requirement Category | Total Cases | Automated | Manual | Priority |
|---|---|---|---|---|
| Functional Requirements / 기능 요구사항 | 25 | 20 | 5 | High |
| Non-Functional Requirements / 비기능 요구사항 | 10 | 8 | 2 | Medium |
| Safety Requirements / 안전 요구사항 | 15 | 10 | 5 | Critical |
| Interface Requirements / 인터페이스 요구사항 | 12 | 10 | 2 | High |
| **Total / 합계** | **62** | **48** | **14** | |

### 3.2 Test Case List / 시험 케이스 목록

| Test ID | SWE.1 Req ID | Description / 설명 | Type | Priority | Pass Criteria / 합격 기준 |
|---|---|---|---|---|---|
| QT-001 | SWE1-REQ-001 | Steering angle input range test / 조향각 입력 범위 시험 | Auto | High | Value within +-720 deg, accuracy +-0.5 deg |
| QT-002 | SWE1-REQ-002 | Torque output accuracy test / 토크 출력 정확도 시험 | Auto | High | Torque within 0-12 Nm, accuracy +-0.1 Nm |
| QT-003 | SWE1-REQ-003 | Safety response time test / 안전 응답 시간 시험 | Auto | Critical | Response < 10ms to safe state |
| QT-004 | SWE1-REQ-004 | DTC storage verification / DTC 저장 검증 | Auto | Medium | DTC stored in NVM within 100ms |
| QT-005 | SWE1-REQ-005 | CAN communication cycle test / CAN 통신 주기 시험 | Auto | High | Message cycle 20ms +-2ms |
| | | (시험 케이스를 추가하세요 / Add test cases) | | | |

---

## 4. Pass/Fail Criteria / 합격/불합격 기준

### 4.1 Overall Pass Criteria / 전체 합격 기준

| # | Criteria / 기준 | Target / 목표 |
|---|---|---|
| 1 | Test case pass rate / 시험 케이스 합격률 | ≥ 95% |
| 2 | Critical test cases passed / 심각 시험 케이스 합격 | 100% |
| 3 | Safety test cases passed / 안전 시험 케이스 합격 | 100% |
| 4 | No critical defects open / 심각 결함 미해결 없음 | 0 |
| 5 | Requirement coverage / 요구사항 커버리지 | 100% |

### 4.2 Individual Test Pass Criteria / 개별 시험 합격 기준

| Test Type / 시험 유형 | Pass Criteria / 합격 기준 |
|---|---|
| Functional Test | Actual result matches expected result within tolerance |
| Timing Test | Measured time within specified limit |
| Safety Test | Safe state reached within specified time |
| Interface Test | All signals within specified range and accuracy |

---

## 5. Test Schedule / 시험 일정

| Phase / 단계 | Start Date | End Date | Deliverable / 산출물 |
|---|---|---|---|
| Test Plan Review / 시험 계획 검토 | | | Approved test plan |
| Test Case Development / 시험 케이스 개발 | | | Test specifications |
| Test Environment Validation / 시험 환경 검증 | | | Validated environment |
| Test Execution Round 1 / 시험 실행 1차 | | | Preliminary results |
| Defect Fix & Retest / 결함 수정 및 재시험 | | | Updated results |
| Test Execution Round 2 / 시험 실행 2차 | | | Final results |
| Test Report / 시험 보고서 | | | Final test report |

---

## 6. Defect Management / 결함 관리

| Severity / 심각도 | Response Time / 대응 시간 | Resolution Target / 해결 목표 |
|---|---|---|
| Critical / 심각 | Immediate / 즉시 | Before release |
| Major / 주요 | 1 business day | Before release |
| Minor / 경미 | 3 business days | Next release acceptable |
| Improvement / 개선 | As planned | Next release |

---

## 7. Review Criteria / 검토 기준

| # | Criteria / 기준 | Check |
|---|---|---|
| 1 | All SWE.1 requirements have test cases / 모든 SWE.1 요구사항에 시험 케이스 존재 | ☐ |
| 2 | Test environment matches production config / 시험 환경이 양산 구성과 일치 | ☐ |
| 3 | Pass/fail criteria clearly defined / 합격/불합격 기준 명확히 정의됨 | ☐ |
| 4 | Safety tests cover all ASIL requirements / 안전 시험이 모든 ASIL 요구사항 커버 | ☐ |
| 5 | Schedule allows for retest cycles / 일정에 재시험 주기 포함 | ☐ |
| 6 | Compliant with {oem_name} qualification requirements / OEM 적격성 요구사항 준수 | ☐ |
| 7 | Test automation strategy defined / 시험 자동화 전략 정의됨 | ☐ |
| 8 | Defect management process defined / 결함 관리 프로세스 정의됨 | ☐ |

---

## 8. Review History / 검토 이력

| Date / 날짜 | Reviewer / 검토자 | Result / 결과 | Comments / 비고 |
|---|---|---|---|
| | | Approved / Rejected | |

---

*Generated by ASPICE Process Manager*
