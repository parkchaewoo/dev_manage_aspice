# Software Integration Test Report
# 소프트웨어 통합 테스트 보고서

---

| Field / 항목 | Value / 값 |
|---|---|
| Project Name / 프로젝트명 | {project_name} |
| OEM | {oem_name} |
| Document ID / 문서 ID | {document_id} |
| Version / 버전 | {version} |
| Date / 날짜 | {date} |
| Author / 작성자 | {author} |
| Reviewer / 검토자 | {reviewer} |
| Approver / 승인자 | {approver} |
| Status / 상태 | {status} |
| Build Version / 빌드 버전 | {build_version} |
| Classification / 보안등급 | {classification} |

---

## Revision History / 개정 이력

| Version / 버전 | Date / 날짜 | Author / 작성자 | Description / 설명 |
|---|---|---|---|
| {version} | {date} | {author} | {change_description} |

---

## 1. Introduction / 서론

### 1.1 Purpose / 목적

This document reports the results of software integration and integration testing (SWE.5) for {project_name} developed for {oem_name}. It covers the incremental integration of software components and verification of their interactions.

본 문서는 {oem_name}을 위해 개발된 {project_name}의 소프트웨어 통합 및 통합 테스트 (SWE.5) 결과를 보고합니다. 소프트웨어 컴포넌트의 단계적 통합과 상호작용 검증을 다룹니다.

### 1.2 Scope / 범위

{scope_description}

### 1.3 References / 참고 문서

| ID | Document / 문서 | Version / 버전 |
|---|---|---|
| [REF-01] | Software Architecture Description (SWE.2) / SAD | |
| [REF-02] | Integration Test Plan / 통합 테스트 계획서 | |
| [REF-03] | Unit Test Report (SWE.4) / 유닛 테스트 보고서 | |
| | | |

---

## 2. Test Environment / 테스트 환경

### 2.1 Tools and Infrastructure / 도구 및 인프라

| Item / 항목 | Description / 설명 | Version / 버전 |
|---|---|---|
| SIL Environment / SIL 환경 | {sil_environment} | |
| HIL Environment / HIL 환경 | {hil_environment} | |
| HIL Bench / HIL 벤치 | {hil_bench} | |
| Debugger / 디버거 | {debugger} | |
| Bus Analyzer / 버스 분석기 | {bus_analyzer} | |
| Test Automation / 테스트 자동화 | {test_automation_tool} | |
| Target ECU / 대상 ECU | {target_ecu} | |

### 2.2 Test Configuration / 테스트 구성

| Parameter / 매개변수 | Value / 값 |
|---|---|
| Software Build / 소프트웨어 빌드 | {build_version} |
| Calibration Dataset / 캘리브레이션 데이터셋 | {calibration_version} |
| BSW Configuration / BSW 구성 | {bsw_config_version} |
| Vehicle Network Simulation / 차량 네트워크 시뮬레이션 | {network_simulation} |

---

## 3. Integration Build Summary / 통합 빌드 요약

### 3.1 Integration Sequence / 통합 순서

| Build Step / 빌드 단계 | Components Integrated / 통합된 컴포넌트 | Date / 날짜 | Result / 결과 |
|---|---|---|---|
| Step 1 / 단계 1 | BSW + RTE | | PASS/FAIL |
| Step 2 / 단계 2 | + Core ASW Components | | PASS/FAIL |
| Step 3 / 단계 3 | + Diagnostic Services | | PASS/FAIL |
| Step 4 / 단계 4 | + Communication Stack | | PASS/FAIL |
| Step 5 / 단계 5 | Full Integration / 전체 통합 | | PASS/FAIL |
| | | | |

### 3.2 Build Metrics / 빌드 메트릭

| Metric / 메트릭 | Value / 값 | Budget / 예산 | Status / 상태 |
|---|---|---|---|
| ROM Usage / ROM 사용량 | KB | KB | PASS/FAIL |
| RAM Usage / RAM 사용량 | KB | KB | PASS/FAIL |
| Stack Usage / 스택 사용량 | Bytes | Bytes | PASS/FAIL |
| CPU Load (avg) / CPU 부하 (평균) | % | % | PASS/FAIL |
| CPU Load (peak) / CPU 부하 (최대) | % | % | PASS/FAIL |

---

## 4. Test Execution Summary / 테스트 실행 요약

### 4.1 Overall Results / 전체 결과

| Metric / 메트릭 | Value / 값 |
|---|---|
| Total Test Cases / 전체 테스트 케이스 | {total_test_cases} |
| Passed / 통과 | {passed_count} |
| Failed / 실패 | {failed_count} |
| Blocked / 차단 | {blocked_count} |
| Not Executed / 미실행 | {not_executed_count} |
| Pass Rate / 통과율 | {pass_rate}% |

### 4.2 Results by Test Category / 테스트 범주별 결과

| Category / 범주 | Total / 전체 | Passed / 통과 | Failed / 실패 | Pass Rate / 통과율 |
|---|---|---|---|---|
| Interface Tests / 인터페이스 테스트 | | | | % |
| Data Flow Tests / 데이터 흐름 테스트 | | | | % |
| Communication Tests / 통신 테스트 | | | | % |
| Diagnostic Tests / 진단 테스트 | | | | % |
| Timing Tests / 타이밍 테스트 | | | | % |
| Resource Tests / 리소스 테스트 | | | | % |
| **Total / 합계** | | | | **%** |

### 4.3 Results by Integration Step / 통합 단계별 결과

| Integration Step / 통합 단계 | Total / 전체 | Passed / 통과 | Failed / 실패 | Pass Rate / 통과율 |
|---|---|---|---|---|
| Step 1: BSW + RTE | | | | % |
| Step 2: Core ASW | | | | % |
| Step 3: Diagnostics | | | | % |
| Step 4: Communication | | | | % |
| Step 5: Full Integration | | | | % |

---

## 5. Interface Verification Results / 인터페이스 검증 결과

### 5.1 Internal Interface Tests / 내부 인터페이스 테스트

| Interface ID / 인터페이스 ID | Source / 소스 | Target / 대상 | Test Case ID / 테스트 케이스 ID | Result / 결과 |
|---|---|---|---|---|
| IF-INT-001 | SWC-001 | SWC-002 | TC-INT-001 | PASS/FAIL |
| | | | | |

### 5.2 External Interface Tests / 외부 인터페이스 테스트

| Interface ID / 인터페이스 ID | Protocol / 프로토콜 | Test Case ID / 테스트 케이스 ID | Description / 설명 | Result / 결과 |
|---|---|---|---|---|
| IF-EXT-001 | CAN | TC-EXT-001 | | PASS/FAIL |
| IF-EXT-002 | LIN | TC-EXT-002 | | PASS/FAIL |
| | | | | |

---

## 6. Communication Test Results / 통신 테스트 결과

### 6.1 CAN Communication / CAN 통신

| Message / 메시지 | ID | Direction / 방향 | Cycle (ms) / 주기 | Test Result / 테스트 결과 | Notes / 비고 |
|---|---|---|---|---|---|
| | | TX/RX | | PASS/FAIL | |
| | | | | | |

### 6.2 Diagnostic Communication / 진단 통신

| Service ID / 서비스 ID | Description / 설명 | Test Case ID / 테스트 케이스 ID | Result / 결과 |
|---|---|---|---|
| 0x22 | Read Data By Identifier | | PASS/FAIL |
| 0x2E | Write Data By Identifier | | PASS/FAIL |
| 0x19 | Read DTC Information | | PASS/FAIL |
| 0x14 | Clear DTC Information | | PASS/FAIL |
| | | | |

---

## 7. Defect Summary / 결함 요약

### 7.1 Defects Found / 발견된 결함

| Defect ID / 결함 ID | Integration Step / 통합 단계 | Severity / 심각도 | Description / 설명 | Root Cause / 근본 원인 | Status / 상태 |
|---|---|---|---|---|---|
| DEF-INT-001 | | Critical/Major/Minor | | | Open/Closed |
| | | | | | |

### 7.2 Defect Statistics / 결함 통계

| Severity / 심각도 | Found / 발견 | Resolved / 해결 | Open / 미해결 |
|---|---|---|---|
| Critical / 치명적 | | | |
| Major / 주요 | | | |
| Minor / 경미 | | | |
| **Total / 합계** | | | |

---

## 8. Traceability / 추적성

### 8.1 Upstream Traceability from SWE.2 / SWE.2 상위 추적성

Each integration test case shall trace back to an architecture interface or component interaction (SWE.2).

각 통합 테스트 케이스는 아키텍처 인터페이스 또는 컴포넌트 상호작용 (SWE.2)으로 역추적되어야 합니다.

| Architecture Element / 아키텍처 요소 | Interface ID / 인터페이스 ID | Test Case ID / 테스트 케이스 ID | Result / 결과 |
|---|---|---|---|
| SWC-001 <-> SWC-002 | IF-INT-001 | TC-INT-001 | |
| | | | |

### 8.2 Relationship to SWE.4 / SWE.4 관계

Integration testing builds upon unit-verified components (SWE.4). All units shall have passed unit verification before integration.

통합 테스트는 유닛 검증된 컴포넌트 (SWE.4)를 기반으로 합니다. 모든 유닛은 통합 전에 유닛 검증을 통과해야 합니다.

| Component / 컴포넌트 | Unit Test Status / 유닛 테스트 상태 | Integration Ready / 통합 준비 |
|---|---|---|
| SWC-001 | | YES/NO |
| SWC-002 | | YES/NO |
| | | |

### 8.3 Downstream Traceability to SWE.6 / SWE.6 하위 추적성

Successfully integrated software proceeds to qualification testing (SWE.6).

성공적으로 통합된 소프트웨어는 적격성 테스트 (SWE.6)로 진행됩니다.

---

## 9. Conclusion and Recommendations / 결론 및 권고

### 9.1 Test Verdict / 테스트 판정

| Criteria / 기준 | Result / 결과 | Status / 상태 |
|---|---|---|
| All integration steps completed / 전체 통합 단계 완료 | | PASS/FAIL |
| All test cases executed / 전체 테스트 케이스 실행 | | PASS/FAIL |
| Pass rate ≥ 100% / 통과율 ≥ 100% | | PASS/FAIL |
| No open critical defects / 미해결 치명적 결함 없음 | | PASS/FAIL |
| Resource budgets met / 리소스 예산 달성 | | PASS/FAIL |
| **Overall Verdict / 전체 판정** | | **PASS/FAIL** |

### 9.2 Recommendations / 권고 사항

{recommendations}

---

## 10. Appendix / 부록

### 10.1 Related ASPICE Stages / 관련 ASPICE 단계

| Stage / 단계 | Relationship / 관계 | Document / 문서 |
|---|---|---|
| SWE.2 | Integration tests verify architecture / 통합 테스트가 아키텍처를 검증 | SAD |
| SWE.4 | Unit-verified components are input / 유닛 검증된 컴포넌트가 입력 | UTR |
| SWE.6 | Integrated SW proceeds to qualification / 통합된 SW가 적격성으로 진행 | QTR |

### 10.2 Open Issues / 미결 사항

| ID | Description / 설명 | Owner / 담당자 | Due Date / 기한 |
|---|---|---|---|
| | | | |
