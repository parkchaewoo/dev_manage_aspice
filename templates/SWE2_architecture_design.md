# Software Architecture Design (SAD)
# 소프트웨어 아키텍처 설계서

---
<!-- GUIDE: SWE.1 요구사항을 기반으로 소프트웨어의 전체 구조를 설계합니다 -->

| Field / 항목 | Value / 값 |
|---|---|
| Project Name / 프로젝트명 | {project_name} |
| OEM | {oem_name} |
| Document ID | {document_id} |
| Version | 0.1 |
| Date | {date} |
| Author | |
| Status | Draft |

## Revision History / 개정 이력
| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 0.1 | {date} | | Initial draft |

## Input Artifacts / 입력 산출물
| Artifact | Source |
|---|---|
| Software Requirements Specification (SWE.1) | SWE.1 |
| System Architecture | Systems Engineering |
| HW Interface Specification | HW Team |

## Output Artifacts / 출력 산출물
| Artifact | Target |
|---|---|
| SW Architecture (this) | SWE.3 Detailed Design |
| Interface Design | SWE.5 Integration Test |

---

## 1. Architecture Overview / 아키텍처 개요

### 1.1 AUTOSAR Layer Structure
```
┌───────────────────────────────────────┐
│       Application Layer (SWC)         │
│  [SensorSWC] [ControlSWC] [DiagSWC]  │
├───────────────────────────────────────┤
│       Runtime Environment (RTE)       │
├───────────────────────────────────────┤
│       Basic Software (BSW)            │
│  [COM] [OS] [DEM] [NvM] [CanIf]     │
├───────────────────────────────────────┤
│       MCAL                            │
│  [ADC] [SPI] [CAN] [PWM] [WDG]      │
├───────────────────────────────────────┤
│       Hardware (MCU)                  │
└───────────────────────────────────────┘
```

### 1.2 Component Diagram
```
[Sensor] → [SensorInput] → [ControlLogic] → [ActuatorOutput] → [Motor]
                                  ↑
[CAN Bus] → [CommManager] ────────┘
                                  ↓
              [SafetyMonitor] ← [DiagManager] → [NVM]
```

---

## 2. Component Decomposition / 컴포넌트 분해
<!-- GUIDE: 각 컴포넌트의 책임과 ASIL을 명확히 정의하세요 -->

| Component | Responsibility / 책임 | ASIL | Input | Output |
|---|---|---|---|---|
| SensorInput | 센서 읽기, 필터링, 유효성 검사 | B | ADC/SPI raw | Filtered values |
| ControlLogic | 제어 알고리즘 (PID), 토크 계산 | B | Sensor values | Torque command |
| ActuatorOutput | 모터 PWM 구동, 전류 제어 | B | Torque cmd | PWM duty |
| SafetyMonitor | 고장 감지, 안전 상태 관리 | D | All status | Safety state |
| DiagManager | DTC, UDS 진단 서비스 | QM | Faults | DTC records |
| CommManager | CAN 송수신, 신호 파싱 | A | CAN frames | Parsed signals |
| NvmManager | NVM 읽기/쓰기 | QM | Data req | Stored data |

---

## 3. Interface Specification / 인터페이스 사양

| Signal | Source | Target | Type | Range | Unit | Rate |
|---|---|---|---|---|---|---|
| SteeringAngle_Raw | SensorInput | ControlLogic | FLOAT32 | ±720.0 | deg | 5ms |
| VehicleSpeed | CommManager | ControlLogic | FLOAT32 | 0~300 | km/h | 20ms |
| TargetTorque | ControlLogic | ActuatorOutput | FLOAT32 | ±12.0 | Nm | 5ms |
| MotorCurrent | ActuatorOutput | SafetyMonitor | FLOAT32 | 0~80 | A | 5ms |
| SafetyState | SafetyMonitor | ControlLogic | ENUM | NORMAL/DEGRADED/SAFE | - | 5ms |
| FaultActive | SafetyMonitor | DiagManager | UINT32 | Bitmask | - | 10ms |

---

## 4. Dynamic Behavior / 동적 거동

### 4.1 State Machine

| Current State | Event | Next State | Action |
|---|---|---|---|
| INIT | Init complete | NORMAL | Enable control |
| NORMAL | Safety fault | DEGRADED | Reduce torque 50% |
| NORMAL | Critical fault | SAFE_STATE | Torque=0, open relay |
| DEGRADED | Fault cleared | NORMAL | Restore full torque |
| SAFE_STATE | Power cycle | INIT | Re-initialize |

### 4.2 Task Configuration

| Task | Priority | Cycle | Modules | Stack |
|---|---|---|---|---|
| Task_5ms | High | 5ms | Sensor, Control, Actuator | 1024B |
| Task_10ms | Medium | 10ms | Safety, Comm | 512B |
| Task_100ms | Low | 100ms | Diag, NVM | 512B |

---

## 5. Resource Budget / 리소스 예산

| Component | RAM (B) | ROM (B) | CPU (%) |
|---|---|---|---|
| SensorInput | 1,024 | 4,096 | 5% |
| ControlLogic | 2,048 | 8,192 | 15% |
| ActuatorOutput | 512 | 2,048 | 8% |
| SafetyMonitor | 1,024 | 6,144 | 10% |
| DiagManager | 2,048 | 12,288 | 5% |
| CommManager | 1,536 | 4,096 | 8% |
| NvmManager | 512 | 2,048 | 2% |
| OS/BSW | 4,096 | 32,768 | 7% |
| **Total** | **12,800** | **71,680** | **60%** |
| **Budget (70%/80%/70%)** | **45,056** | **204,800** | **70%** |

---

## 6. Error Handling Architecture / 에러 처리

| Error | Detection | Response | Recovery |
|---|---|---|---|
| Sensor range error | Bounds check | Use last valid (3 cycles) | Auto-recover |
| CAN loss | Timeout >100ms | Use safe defaults | Auto on reception |
| CPU overload | Watchdog timeout | MCU reset | Full re-init |
| NVM corruption | CRC check | Use defaults | NVM restore |
| Motor overcurrent | HW comparator + SW | Disable motor | Thermal cooldown |

---

## 7. Traceability / 추적성

### 7.1 SWE.1 Requirements → Architecture
| SWE.1 Req | Architecture Element | Coverage |
|---|---|---|
| SWE1-REQ-001 | SensorInput | Full |
| SWE1-REQ-002 | ControlLogic + ActuatorOutput | Full |
| SWE1-REQ-003 | SafetyMonitor | Full |
| SWE1-REQ-004 | DiagManager + NvmManager | Full |
| SWE1-REQ-005 | CommManager | Full |

### 7.2 Architecture → SWE.5 Integration Test
| Architecture Element | SWE.5 Test | Description |
|---|---|---|
| Sensor→Control chain | IT-001 | Data flow verification |
| Control→Actuator | IT-002 | Torque command chain |
| CAN→Control | IT-003 | Signal integration |
| Safety→All | IT-004 | Safety state propagation |

---

## 8. Review Criteria / 검토 기준
| # | Criteria / 기준 | Check |
|---|---|---|
| 1 | All SWE.1 requirements mapped | ☐ |
| 2 | Interfaces fully specified | ☐ |
| 3 | Resource budget within limits | ☐ |
| 4 | Safety architecture ASIL-consistent | ☐ |
| 5 | State machine complete | ☐ |
| 6 | Error handling defined | ☐ |
| 7 | Task schedulability verified | ☐ |
| 8 | Traceability to SWE.1/SWE.5 complete | ☐ |

---
*Generated by ASPICE Process Manager*
