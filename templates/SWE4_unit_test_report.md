# Unit Test Report
# 유닛 테스트 보고서

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
| Test Tool / 테스트 도구 | {test_tool} |
| Classification / 보안등급 | {classification} |

---

## Revision History / 개정 이력

| Version / 버전 | Date / 날짜 | Author / 작성자 | Description / 설명 |
|---|---|---|---|
| {version} | {date} | {author} | {change_description} |

---

## 1. Introduction / 서론

### 1.1 Purpose / 목적

This document reports the results of unit verification (SWE.4) for {project_name} developed for {oem_name}. It provides test execution results, coverage metrics, and defect summary for all tested software units.

본 문서는 {oem_name}을 위해 개발된 {project_name}의 유닛 검증 (SWE.4) 결과를 보고합니다. 테스트된 모든 소프트웨어 유닛에 대한 테스트 실행 결과, 커버리지 메트릭 및 결함 요약을 제공합니다.

### 1.2 Scope / 범위

{scope_description}

### 1.3 References / 참고 문서

| ID | Document / 문서 | Version / 버전 |
|---|---|---|
| [REF-01] | Software Detailed Design Document (SWE.3) / SDD | |
| [REF-02] | Unit Test Plan / 유닛 테스트 계획서 | |
| [REF-03] | Unit Test Case Specification / 유닛 테스트 케이스 명세서 | |
| | | |

---

## 2. Test Environment / 테스트 환경

### 2.1 Tools and Infrastructure / 도구 및 인프라

| Item / 항목 | Description / 설명 | Version / 버전 |
|---|---|---|
| Test Framework / 테스트 프레임워크 | {test_framework} | |
| Compiler / 컴파일러 | {compiler} | |
| Coverage Tool / 커버리지 도구 | {coverage_tool} | |
| Static Analysis Tool / 정적 분석 도구 | {static_analysis_tool} | |
| CI/CD Pipeline / CI/CD 파이프라인 | {ci_cd_tool} | |
| Target Platform / 대상 플랫폼 | {target_platform} | |

### 2.2 Test Configuration / 테스트 구성

| Parameter / 매개변수 | Value / 값 |
|---|---|
| Optimization Level / 최적화 레벨 | {optimization_level} |
| Stub Strategy / 스텁 전략 | {stub_strategy} |
| Mock Framework / 모킹 프레임워크 | {mock_framework} |

---

## 3. Test Execution Summary / 테스트 실행 요약

### 3.1 Overall Results / 전체 결과

| Metric / 메트릭 | Value / 값 |
|---|---|
| Total Test Cases / 전체 테스트 케이스 | {total_test_cases} |
| Passed / 통과 | {passed_count} |
| Failed / 실패 | {failed_count} |
| Blocked / 차단 | {blocked_count} |
| Not Executed / 미실행 | {not_executed_count} |
| Pass Rate / 통과율 | {pass_rate}% |
| Test Execution Date / 테스트 실행 날짜 | {execution_date} |

### 3.2 Results by Unit / 유닛별 결과

| Unit ID / 유닛 ID | Unit Name / 유닛명 | Total / 전체 | Passed / 통과 | Failed / 실패 | Blocked / 차단 | Pass Rate / 통과율 |
|---|---|---|---|---|---|---|
| UNIT-001 | | | | | | % |
| UNIT-002 | | | | | | % |
| UNIT-003 | | | | | | % |
| **Total / 합계** | | | | | | **%** |

### 3.3 Results by Test Category / 테스트 범주별 결과

| Category / 범주 | Total / 전체 | Passed / 통과 | Failed / 실패 | Pass Rate / 통과율 |
|---|---|---|---|---|
| Normal Operation / 정상 동작 | | | | % |
| Boundary Values / 경계값 | | | | % |
| Error Handling / 에러 처리 | | | | % |
| Robustness / 견고성 | | | | % |
| **Total / 합계** | | | | **%** |

---

## 4. Coverage Results / 커버리지 결과

### 4.1 Overall Coverage / 전체 커버리지

| Coverage Type / 커버리지 유형 | Achieved / 달성 (%) | Target / 목표 (%) | Status / 상태 |
|---|---|---|---|
| Statement Coverage / 구문 커버리지 | | 80 | PASS/FAIL |
| Branch Coverage / 분기 커버리지 | | 70 | PASS/FAIL |
| MC/DC Coverage (safety-critical) / MC/DC 커버리지 (안전 필수) | | 100 | PASS/FAIL |
| Function Coverage / 함수 커버리지 | | 100 | PASS/FAIL |

### 4.2 Coverage by Unit / 유닛별 커버리지

| Unit ID / 유닛 ID | Unit Name / 유닛명 | Statement (%) / 구문 | Branch (%) / 분기 | MC/DC (%) | Status / 상태 |
|---|---|---|---|---|---|
| UNIT-001 | | | | | |
| UNIT-002 | | | | | |
| UNIT-003 | | | | | |
| **Average / 평균** | | | | | |

### 4.3 Coverage Gaps and Justification / 커버리지 미달 및 근거

| Unit ID / 유닛 ID | Gap Type / 미달 유형 | Uncovered Code / 미커버 코드 | Justification / 근거 |
|---|---|---|---|
| | | | |

---

## 5. Test Case Details / 테스트 케이스 상세

### 5.1 Test Case Results for UNIT-001 / UNIT-001 테스트 케이스 결과

| Test Case ID / 테스트 케이스 ID | Description / 설명 | Input / 입력 | Expected / 예상 | Actual / 실제 | Result / 결과 |
|---|---|---|---|---|---|
| TC-UNIT001-001 | | | | | PASS/FAIL |
| TC-UNIT001-002 | | | | | PASS/FAIL |
| | | | | | |

---

## 6. Defect Summary / 결함 요약

### 6.1 Defects Found / 발견된 결함

| Defect ID / 결함 ID | Unit / 유닛 | Severity / 심각도 | Description / 설명 | Status / 상태 | Resolution / 해결 |
|---|---|---|---|---|---|
| DEF-001 | | Critical/Major/Minor | | Open/Closed | |
| | | | | | |

### 6.2 Defect Statistics / 결함 통계

| Severity / 심각도 | Found / 발견 | Resolved / 해결 | Open / 미해결 |
|---|---|---|---|
| Critical / 치명적 | | | |
| Major / 주요 | | | |
| Minor / 경미 | | | |
| **Total / 합계** | | | |

---

## 7. Traceability / 추적성

### 7.1 Upstream Traceability from SWE.3 / SWE.3 상위 추적성

Each unit test case shall trace back to a detailed design unit (SWE.3).

각 유닛 테스트 케이스는 상세 설계 유닛 (SWE.3)으로 역추적되어야 합니다.

| Unit ID / 유닛 ID | Test Case IDs / 테스트 케이스 ID | Coverage Status / 커버리지 상태 |
|---|---|---|
| UNIT-001 | TC-UNIT001-001, TC-UNIT001-002 | |
| UNIT-002 | | |
| | | |

### 7.2 Upstream Traceability from SWE.1 / SWE.1 상위 추적성

| SW Req ID / SW 요구사항 ID | Unit ID / 유닛 ID | Test Case ID / 테스트 케이스 ID | Result / 결과 |
|---|---|---|---|
| SWR-F-001 | UNIT-001 | TC-UNIT001-001 | |
| | | | |

### 7.3 Relationship to SWE.5 / SWE.5 관계

Units verified here are subsequently integrated and tested at the integration level (SWE.5).

여기서 검증된 유닛은 이후 통합 레벨 (SWE.5)에서 통합되어 테스트됩니다.

---

## 8. Conclusion and Recommendations / 결론 및 권고

### 8.1 Test Verdict / 테스트 판정

| Criteria / 기준 | Result / 결과 | Status / 상태 |
|---|---|---|
| All test cases executed / 전체 테스트 케이스 실행 | | PASS/FAIL |
| Pass rate ≥ 100% / 통과율 ≥ 100% | | PASS/FAIL |
| Coverage targets met / 커버리지 목표 달성 | | PASS/FAIL |
| No open critical defects / 미해결 치명적 결함 없음 | | PASS/FAIL |
| **Overall Verdict / 전체 판정** | | **PASS/FAIL** |

### 8.2 Recommendations / 권고 사항

{recommendations}

---

## 9. Appendix / 부록

### 9.1 Related ASPICE Stages / 관련 ASPICE 단계

| Stage / 단계 | Relationship / 관계 | Document / 문서 |
|---|---|---|
| SWE.3 | Unit tests verify detailed design / 유닛 테스트가 상세 설계를 검증 | SDD |
| SWE.1 | Unit tests contribute to requirement verification / 유닛 테스트가 요구사항 검증에 기여 | SRS |
| SWE.5 | Verified units feed into integration / 검증된 유닛이 통합에 투입됨 | ITR |

### 9.2 Open Issues / 미결 사항

| ID | Description / 설명 | Owner / 담당자 | Due Date / 기한 |
|---|---|---|---|
| | | | |
