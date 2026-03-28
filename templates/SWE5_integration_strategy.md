# Integration Strategy
# 통합 전략 문서

---

<!-- GUIDE: 이 문서는 소프트웨어 통합 전략, 빌드 순서, HIL/SIL 설정을 정의합니다. -->
<!-- GUIDE: This document defines SW integration strategy, build sequence, and HIL/SIL setup. -->

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
본 문서는 {project_name} 프로젝트의 소프트웨어 통합 전략을 정의합니다.
This document defines the software integration strategy for the {project_name} project.

### 1.2 Integration Scope / 통합 범위
- Application SW Components (ASW) / 응용 소프트웨어 컴포넌트
- Basic Software (BSW) Integration / 기본 소프트웨어 통합
- AUTOSAR RTE Configuration / AUTOSAR RTE 구성
- Calibration Data / 캘리브레이션 데이터

---

## 2. Integration Approach / 통합 접근 방식

### 2.1 Integration Strategy / 통합 전략

| Aspect / 측면 | Description / 설명 |
|---|---|
| Strategy Type / 전략 유형 | Incremental Bottom-Up / 점진적 상향식 |
| Integration Levels / 통합 수준 | SWC → Cluster → Full SW → HW Integration |
| Automation / 자동화 | CI/CD pipeline with automated build and test |
| Configuration Management / 형상 관리 | Git-based, tagged releases |

### 2.2 Integration Levels / 통합 수준

| Level / 수준 | Description / 설명 | Environment / 환경 | Verification / 검증 |
|---|---|---|---|
| Level 1: SWC Integration | 개별 SWC 통합 | SIL (PC) | Interface test |
| Level 2: Cluster Integration | SWC 클러스터 통합 | SIL (PC) | Functional test |
| Level 3: Full SW Integration | 전체 SW 통합 (ASW + BSW) | SIL + PIL | System-level test |
| Level 4: HW-SW Integration | HW-SW 통합 | HIL / Target HW | HW interface test |

---

## 3. Build Sequence / 빌드 순서

### 3.1 Integration Order / 통합 순서

| Step | Component / 컴포넌트 | Dependencies / 의존성 | Level | Milestone |
|---|---|---|---|---|
| 1 | BSW + MCAL + OS | None | L3 | BSW Baseline |
| 2 | RTE Generation | BSW | L3 | RTE Ready |
| 3 | SWC_SensorProc | RTE | L1 | Sensor Ready |
| 4 | SWC_TorqueCalc | SWC_SensorProc | L1 | Calc Ready |
| 5 | SWC_SafetyMonitor | SWC_SensorProc | L1 | Safety Ready |
| 6 | SWC_MotorCtrl | SWC_TorqueCalc, SWC_SafetyMonitor | L2 | Control Cluster |
| 7 | SWC_Diagnostics | SWC_SensorProc, NvM | L2 | Diag Cluster |
| 8 | SWC_Communication | All SWCs | L2 | Comm Ready |
| 9 | Full SW Build | All components | L3 | SW Release Candidate |
| 10 | HW-SW Integration | Full SW + Target HW | L4 | HW Integration Done |

---

## 4. SIL Environment / SIL 환경

### 4.1 SIL Configuration / SIL 구성

| Component / 구성요소 | Tool / 도구 | Version | Purpose / 용도 |
|---|---|---|---|
| Compiler (Host) | GCC / MSVC | - | Host compilation |
| Compiler (Target) | HighTec / GreenHills | - | Cross compilation |
| Simulation Framework | MATLAB/Simulink | R2023b | Plant model simulation |
| Virtual ECU | vECU / Silver | - | SW execution on PC |
| CAN Simulation | CANoe / BusMaster | - | CAN bus simulation |

### 4.2 SIL Test Scope / SIL 시험 범위

| Test Type / 시험 유형 | Description / 설명 | Automation |
|---|---|---|
| Interface Test | SWC 간 데이터 교환 검증 | Automated |
| Functional Test | 기능 요구사항 검증 | Automated |
| Timing Test | 실행 시간 측정 (approximate) | Automated |
| Regression Test | 변경 후 기존 기능 검증 | CI/CD |

---

## 5. HIL Environment / HIL 환경

### 5.1 HIL Configuration / HIL 구성

| Component / 구성요소 | Specification / 사양 | Purpose / 용도 |
|---|---|---|
| HIL System | dSPACE SCALEXIO / ETAS LABCAR | Real-time simulation |
| Target ECU | Production ECU | SW execution |
| Load Box | Sensor/Actuator simulation | HW interface simulation |
| CAN Interface | Vector VN1610 / PEAK PCAN | CAN communication |
| Power Supply | 9-16V programmable | Voltage variation test |
| Debugger | Lauterbach TRACE32 / iSYSTEM | On-target debugging |

### 5.2 HIL Test Scope / HIL 시험 범위

| Test Type / 시험 유형 | Description / 설명 | Priority |
|---|---|---|
| HW Interface Test | 센서/액추에이터 인터페이스 검증 | High |
| CAN Communication Test | CAN 메시지 송수신 검증 | High |
| Timing Verification | 실시간 타이밍 검증 | High |
| Fault Injection Test | 고장 주입 시험 | Critical |
| Power Supply Test | 전원 변동 시험 | Medium |

---

## 6. Integration Schedule / 통합 일정

| Phase / 단계 | Start Date | End Date | Deliverable / 산출물 |
|---|---|---|---|
| SIL Environment Setup | | | SIL ready |
| Level 1-2 Integration | | | SWC clusters verified |
| Level 3 Integration | | | Full SW build verified |
| HIL Environment Setup | | | HIL ready |
| Level 4 Integration | | | HW-SW integration verified |
| Integration Test Report | | | Final report |

---

## 7. Risk Management / 위험 관리

| Risk / 위험 | Impact / 영향 | Probability | Mitigation / 완화 |
|---|---|---|---|
| BSW delivery delay / BSW 납품 지연 | High | Medium | Early BSW stub creation |
| HIL equipment unavailable / HIL 장비 미가용 | High | Low | SIL-first approach |
| Interface mismatch / 인터페이스 불일치 | Medium | Medium | Early interface review |
| Build system failure / 빌드 시스템 장애 | Medium | Low | Redundant CI server |

---

## 8. Review Criteria / 검토 기준

| # | Criteria / 기준 | Check |
|---|---|---|
| 1 | Integration order considers dependencies / 통합 순서가 의존성 고려 | ☐ |
| 2 | SIL and HIL environments specified / SIL 및 HIL 환경 명세됨 | ☐ |
| 3 | Build sequence is feasible / 빌드 순서가 실현 가능 | ☐ |
| 4 | All SWCs included in integration scope / 모든 SWC가 통합 범위에 포함 | ☐ |
| 5 | Risk mitigation plans defined / 위험 완화 계획 정의됨 | ☐ |
| 6 | Schedule aligned with project milestones / 일정이 프로젝트 마일스톤과 정렬 | ☐ |
| 7 | CI/CD pipeline defined / CI/CD 파이프라인 정의됨 | ☐ |
| 8 | Compliant with {oem_name} integration requirements / OEM 통합 요구사항 준수 | ☐ |

---

## 9. Review History / 검토 이력

| Date / 날짜 | Reviewer / 검토자 | Result / 결과 | Comments / 비고 |
|---|---|---|---|
| | | Approved / Rejected | |

---

*Generated by ASPICE Process Manager*
