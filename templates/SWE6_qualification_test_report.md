# Software Qualification Test Report
# 소프트웨어 적격성 테스트 보고서

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
| SW Release Version / SW 릴리스 버전 | {sw_release_version} |
| ECU Part Number / ECU 부품번호 | {ecu_part_number} |
| Classification / 보안등급 | {classification} |

---

## Revision History / 개정 이력

| Version / 버전 | Date / 날짜 | Author / 작성자 | Description / 설명 |
|---|---|---|---|
| {version} | {date} | {author} | {change_description} |

---

## 1. Introduction / 서론

### 1.1 Purpose / 목적

This document reports the results of software qualification testing (SWE.6) for {project_name} developed for {oem_name}. It demonstrates that the software meets all specified requirements and is ready for release.

본 문서는 {oem_name}을 위해 개발된 {project_name}의 소프트웨어 적격성 테스트 (SWE.6) 결과를 보고합니다. 소프트웨어가 모든 명시된 요구사항을 충족하고 릴리스 준비가 되었음을 입증합니다.

### 1.2 Scope / 범위

{scope_description}

### 1.3 References / 참고 문서

| ID | Document / 문서 | Version / 버전 |
|---|---|---|
| [REF-01] | Software Requirements Specification (SWE.1) / SRS | |
| [REF-02] | Qualification Test Plan / 적격성 테스트 계획서 | |
| [REF-03] | Integration Test Report (SWE.5) / 통합 테스트 보고서 | |
| [REF-04] | {oem_name} Release Criteria / 릴리스 기준 | |
| | | |

---

## 2. Test Environment / 테스트 환경

### 2.1 Tools and Infrastructure / 도구 및 인프라

| Item / 항목 | Description / 설명 | Version / 버전 |
|---|---|---|
| Target ECU Hardware / 대상 ECU 하드웨어 | {target_ecu_hw} | |
| HIL Bench / HIL 벤치 | {hil_bench} | |
| Vehicle Network / 차량 네트워크 | {vehicle_network_setup} | |
| Test Automation Tool / 테스트 자동화 도구 | {test_automation} | |
| Measurement Tool / 측정 도구 | {measurement_tool} | |
| Diagnostic Tool / 진단 도구 | {diagnostic_tool} | |

### 2.2 Software Under Test / 테스트 대상 소프트웨어

| Parameter / 매개변수 | Value / 값 |
|---|---|
| SW Version / SW 버전 | {sw_release_version} |
| Calibration Version / 캘리브레이션 버전 | {calibration_version} |
| Bootloader Version / 부트로더 버전 | {bootloader_version} |
| BSW Version / BSW 버전 | {bsw_version} |
| Build Date / 빌드 날짜 | {build_date} |
| ECU Part Number / ECU 부품번호 | {ecu_part_number} |
| Checksum / 체크섬 | {checksum} |

---

## 3. Qualification Test Execution Summary / 적격성 테스트 실행 요약

### 3.1 Overall Results / 전체 결과

| Metric / 메트릭 | Value / 값 |
|---|---|
| Total Test Cases / 전체 테스트 케이스 | {total_test_cases} |
| Passed / 통과 | {passed_count} |
| Failed / 실패 | {failed_count} |
| Blocked / 차단 | {blocked_count} |
| Not Executed / 미실행 | {not_executed_count} |
| Pass Rate / 통과율 | {pass_rate}% |
| Requirements Covered / 요구사항 커버 | {requirements_covered} / {total_requirements} |
| Requirement Coverage / 요구사항 커버리지 | {requirement_coverage}% |

### 3.2 Results by Requirement Category / 요구사항 범주별 결과

| Category / 범주 | Requirements / 요구사항 | Tested / 테스트됨 | Passed / 통과 | Failed / 실패 | Coverage / 커버리지 |
|---|---|---|---|---|---|
| Functional / 기능 | | | | | % |
| Performance / 성능 | | | | | % |
| Safety / 안전 | | | | | % |
| Diagnostic / 진단 | | | | | % |
| Communication / 통신 | | | | | % |
| Robustness / 견고성 | | | | | % |
| **Total / 합계** | | | | | **%** |

---

## 4. Functional Qualification Results / 기능 적격성 결과

### 4.1 Functional Test Results / 기능 테스트 결과

| Req ID / 요구사항 ID | Requirement / 요구사항 | Test Case ID / 테스트 케이스 ID | Test Description / 테스트 설명 | Result / 결과 |
|---|---|---|---|---|
| SWR-F-001 | | TC-QT-F-001 | | PASS/FAIL |
| SWR-F-002 | | TC-QT-F-002 | | PASS/FAIL |
| | | | | |

---

## 5. Non-Functional Qualification Results / 비기능 적격성 결과

### 5.1 Performance Test Results / 성능 테스트 결과

| Req ID / 요구사항 ID | Metric / 메트릭 | Target / 목표 | Measured / 측정값 | Unit / 단위 | Result / 결과 |
|---|---|---|---|---|---|
| SWR-P-001 | | | | ms/% | PASS/FAIL |
| | | | | | |

### 5.2 Resource Consumption / 리소스 소비

| Resource / 리소스 | Budget / 예산 | Actual / 실제 | Margin (%) / 여유 | Status / 상태 |
|---|---|---|---|---|
| ROM | KB | KB | % | PASS/FAIL |
| RAM | KB | KB | % | PASS/FAIL |
| CPU Load (avg) / CPU 부하 (평균) | % | % | % | PASS/FAIL |
| CPU Load (peak) / CPU 부하 (최대) | % | % | % | PASS/FAIL |
| Stack Usage / 스택 사용량 | Bytes | Bytes | % | PASS/FAIL |

### 5.3 Timing Verification / 타이밍 검증

| Function / 기능 | Required / 요구 | Measured / 측정값 | Unit / 단위 | Result / 결과 |
|---|---|---|---|---|
| | | | ms | PASS/FAIL |
| | | | ms | PASS/FAIL |

### 5.4 Safety Qualification Results / 안전 적격성 결과

| Req ID / 요구사항 ID | Safety Mechanism / 안전 메커니즘 | ASIL | Test Case ID / 테스트 케이스 ID | Result / 결과 |
|---|---|---|---|---|
| SWR-S-001 | | | TC-QT-S-001 | PASS/FAIL |
| | | | | |

---

## 6. Diagnostic Qualification Results / 진단 적격성 결과

### 6.1 DTC Verification / DTC 검증

| DTC | Description / 설명 | Detection Tested / 검출 테스트 | Healing Tested / 치유 테스트 | Result / 결과 |
|---|---|---|---|---|
| | | YES/NO | YES/NO | PASS/FAIL |
| | | | | |

### 6.2 UDS Service Verification / UDS 서비스 검증

| Service ID / 서비스 ID | Sub-Function / 서브 기능 | Test Case ID / 테스트 케이스 ID | Result / 결과 |
|---|---|---|---|
| 0x10 | Diagnostic Session Control | | PASS/FAIL |
| 0x11 | ECU Reset | | PASS/FAIL |
| 0x22 | Read Data By Identifier | | PASS/FAIL |
| 0x27 | Security Access | | PASS/FAIL |
| 0x2E | Write Data By Identifier | | PASS/FAIL |
| 0x31 | Routine Control | | PASS/FAIL |
| | | | |

---

## 7. Communication Qualification Results / 통신 적격성 결과

### 7.1 Network Management / 네트워크 관리

| Test / 테스트 | Description / 설명 | Result / 결과 |
|---|---|---|
| NM Startup / NM 시작 | | PASS/FAIL |
| NM Shutdown / NM 종료 | | PASS/FAIL |
| Bus-Off Recovery / Bus-Off 복구 | | PASS/FAIL |
| | | |

### 7.2 Signal Verification / 신호 검증

| Signal / 신호 | Message / 메시지 | Direction / 방향 | Cycle (ms) / 주기 | Result / 결과 |
|---|---|---|---|---|
| | | TX/RX | | PASS/FAIL |
| | | | | |

---

## 8. Defect Summary / 결함 요약

### 8.1 Defects Found During Qualification / 적격성 중 발견된 결함

| Defect ID / 결함 ID | Req ID / 요구사항 ID | Severity / 심각도 | Description / 설명 | Status / 상태 | Resolution / 해결 |
|---|---|---|---|---|---|
| DEF-QT-001 | | Critical/Major/Minor | | Open/Closed | |
| | | | | | |

### 8.2 Known Issues at Release / 릴리스 시 알려진 이슈

| Issue ID / 이슈 ID | Description / 설명 | Impact / 영향 | Workaround / 우회방법 | Planned Fix / 수정 예정 |
|---|---|---|---|---|
| | | | | |

### 8.3 Defect Statistics / 결함 통계

| Severity / 심각도 | Found / 발견 | Resolved / 해결 | Open / 미해결 | Deferred / 보류 |
|---|---|---|---|---|
| Critical / 치명적 | | | | |
| Major / 주요 | | | | |
| Minor / 경미 | | | | |
| **Total / 합계** | | | | |

---

## 9. Traceability / 추적성

### 9.1 Requirements Coverage Matrix / 요구사항 커버리지 매트릭스

Full traceability from software requirements (SWE.1) to qualification test results (SWE.6).

소프트웨어 요구사항 (SWE.1)에서 적격성 테스트 결과 (SWE.6)까지의 전체 추적성.

| SW Req ID / SW 요구사항 ID | Req Title / 요구사항 제목 | Test Case ID / 테스트 케이스 ID | Result / 결과 | Verdict / 판정 |
|---|---|---|---|---|
| SWR-F-001 | | TC-QT-F-001 | | PASS/FAIL |
| SWR-F-002 | | TC-QT-F-002 | | PASS/FAIL |
| SWR-P-001 | | TC-QT-P-001 | | PASS/FAIL |
| SWR-S-001 | | TC-QT-S-001 | | PASS/FAIL |
| | | | | |

### 9.2 Upstream Traceability from SWE.1 / SWE.1 상위 추적성

Each qualification test case validates at least one software requirement (SWE.1).

각 적격성 테스트 케이스는 최소 하나의 소프트웨어 요구사항 (SWE.1)을 검증합니다.

| Total Requirements / 전체 요구사항 | Covered / 커버됨 | Not Covered / 미커버 | Coverage / 커버리지 |
|---|---|---|---|
| {total_requirements} | {covered_requirements} | {uncovered_requirements} | {coverage_percentage}% |

### 9.3 Relationship to SWE.5 / SWE.5 관계

Qualification testing is performed on the fully integrated software verified in SWE.5.

적격성 테스트는 SWE.5에서 검증된 완전히 통합된 소프트웨어에 대해 수행됩니다.

| Integration Test Status / 통합 테스트 상태 | Build Version / 빌드 버전 | Qualification Ready / 적격성 준비 |
|---|---|---|
| {integration_test_status} | {build_version} | YES/NO |

### 9.4 Full V-Model Traceability Summary / 전체 V-모델 추적성 요약

| Left Side (Development) / 좌측 (개발) | Right Side (Verification) / 우측 (검증) | Link / 연결 | Status / 상태 |
|---|---|---|---|
| SWE.1 Software Requirements / 소프트웨어 요구사항 | SWE.6 Qualification Test / 적격성 테스트 | Validates | |
| SWE.2 Architecture / 아키텍처 | SWE.5 Integration Test / 통합 테스트 | Verifies | |
| SWE.3 Detailed Design / 상세 설계 | SWE.4 Unit Test / 유닛 테스트 | Verifies | |

---

## 10. Release Decision / 릴리스 결정

### 10.1 Release Criteria Checklist / 릴리스 기준 체크리스트

| Criteria / 기준 | Result / 결과 | Status / 상태 |
|---|---|---|
| All qualification test cases executed / 전체 적격성 테스트 케이스 실행 | | PASS/FAIL |
| Requirement coverage = 100% / 요구사항 커버리지 = 100% | | PASS/FAIL |
| All functional tests passed / 전체 기능 테스트 통과 | | PASS/FAIL |
| All safety tests passed / 전체 안전 테스트 통과 | | PASS/FAIL |
| Performance targets met / 성능 목표 달성 | | PASS/FAIL |
| Resource budgets met / 리소스 예산 달성 | | PASS/FAIL |
| No open critical/major defects / 미해결 치명적/주요 결함 없음 | | PASS/FAIL |
| All OEM release gate criteria satisfied / 모든 OEM 릴리스 게이트 기준 충족 | | PASS/FAIL |
| **Overall Release Decision / 전체 릴리스 결정** | | **APPROVED / REJECTED** |

### 10.2 Release Approval / 릴리스 승인

| Role / 역할 | Name / 이름 | Date / 날짜 | Signature / 서명 |
|---|---|---|---|
| SW Project Lead / SW 프로젝트 리드 | {sw_project_lead} | | |
| Quality Manager / 품질 관리자 | {quality_manager} | | |
| Customer Representative / 고객 대표 | {customer_representative} | | |

---

## 11. Appendix / 부록

### 11.1 Related ASPICE Stages / 관련 ASPICE 단계

| Stage / 단계 | Relationship / 관계 | Document / 문서 |
|---|---|---|
| SWE.1 | Qualification tests validate requirements / 적격성 테스트가 요구사항을 검증 | SRS |
| SWE.2 | Qualification builds on verified architecture / 적격성이 검증된 아키텍처를 기반으로 함 | SAD |
| SWE.5 | Qualification uses fully integrated SW / 적격성이 완전히 통합된 SW를 사용 | ITR |

### 11.2 Test Execution Log / 테스트 실행 로그

{test_execution_log_reference}

### 11.3 Open Issues / 미결 사항

| ID | Description / 설명 | Owner / 담당자 | Due Date / 기한 |
|---|---|---|---|
| | | | |
