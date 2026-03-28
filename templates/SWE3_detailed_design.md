# Software Detailed Design Document (SDD)
# 소프트웨어 상세 설계서

---
<!-- GUIDE: SWE.2 아키텍처를 기반으로 각 모듈의 상세 설계와 코드를 기술합니다 -->

| Field / 항목 | Value / 값 |
|---|---|
| Project Name | {project_name} |
| OEM | {oem_name} |
| Document ID | {document_id} |
| Version | 0.1 |
| Date | {date} |
| Author | |
| Status | Draft |

## Input Artifacts / 입력 산출물
| Artifact | Source |
|---|---|
| SW Architecture Design (SWE.2) | SWE.2 |
| Coding Guidelines (MISRA-C) | Quality |

## Output Artifacts / 출력 산출물
| Artifact | Target |
|---|---|
| Detailed Design (this) + Source Code | SWE.4 Unit Verification |

---

## 1. Module Design / 모듈 설계

### 1.1 ControlLogic Module / 제어 로직 모듈
- **Purpose / 목적**: EPS 보조 토크 계산 (PID 제어)
- **ASIL**: B
- **Dependencies**: SensorInput, CommManager

### 1.2 SensorInput Module / 센서 입력 모듈
- **Purpose**: 센서 데이터 읽기, 필터링, 유효성 검사
- **ASIL**: B

### 1.3 SafetyMonitor Module / 안전 감시 모듈
- **Purpose**: 시스템 감시, 고장 감지, 안전 상태 관리
- **ASIL**: D

---

## 2. Function Specification / 함수 사양
<!-- GUIDE: 각 함수의 입력, 출력, 사전/사후 조건을 명시하세요 -->

| Function | Input | Output | PreCondition | PostCondition |
|---|---|---|---|---|
| CalcAssistTorque() | angle, speed, mode | torque (Nm) | Sensors valid | -12.0 ≤ torque ≤ 12.0 |
| ReadSteeringAngle() | - | angle (deg) | ADC initialized | -720 ≤ angle ≤ 720 |
| CheckSensorValidity() | raw_value, range | is_valid (bool) | - | fault flag updated |
| UpdateSafetyState() | fault_mask | new_state | All monitors run | State transition logged |
| WriteDtc() | dtc_code, status | success (bool) | NVM ready | DTC stored in NVM |
| FilterSensorValue() | raw, prev_filtered | filtered | Filter initialized | Noise reduced |

---

## 3. Algorithm Description / 알고리즘 기술
<!-- GUIDE: 핵심 알고리즘을 의사코드로 기술하세요 -->

### 3.1 PID Controller / PID 제어기

```pseudo
FUNCTION CalcAssistTorque(steering_angle, vehicle_speed, target_angle):
    // Calculate error
    error = target_angle - steering_angle

    // PID gains (speed-dependent)
    Kp = LookupTable_Kp(vehicle_speed)
    Ki = LookupTable_Ki(vehicle_speed)
    Kd = LookupTable_Kd(vehicle_speed)

    // PID calculation
    P_term = Kp * error
    I_term = I_term_prev + Ki * error * dt    // dt = 5ms
    D_term = Kd * (error - error_prev) / dt

    // Anti-windup for integral term
    IF I_term > I_MAX THEN I_term = I_MAX
    IF I_term < I_MIN THEN I_term = I_MIN

    // Calculate output torque
    torque = P_term + I_term + D_term

    // Output limiting
    IF torque > TORQUE_MAX THEN torque = TORQUE_MAX    // 12.0 Nm
    IF torque < TORQUE_MIN THEN torque = TORQUE_MIN    // -12.0 Nm

    // Safety check
    IF safety_state != NORMAL THEN
        torque = torque * degradation_factor    // 0.5 for DEGRADED, 0.0 for SAFE

    // Update previous values
    error_prev = error
    I_term_prev = I_term

    RETURN torque
END FUNCTION
```

### 3.2 Sensor Filter (Low-Pass) / 센서 필터

```pseudo
FUNCTION FilterSensorValue(raw_value, prev_filtered):
    alpha = 0.3    // Filter coefficient (0 < alpha < 1)
    filtered = alpha * raw_value + (1 - alpha) * prev_filtered
    RETURN filtered
END FUNCTION
```

---

## 4. Data Dictionary / 데이터 사전

| Variable | Type | Range | Unit | Init Value | Description |
|---|---|---|---|---|---|
| g_steeringAngle | FLOAT32 | -720.0 ~ 720.0 | deg | 0.0 | Filtered steering angle |
| g_vehicleSpeed | FLOAT32 | 0 ~ 300.0 | km/h | 0.0 | Vehicle speed from CAN |
| g_targetTorque | FLOAT32 | -12.0 ~ 12.0 | Nm | 0.0 | Calculated assist torque |
| g_motorCurrent | FLOAT32 | 0 ~ 80.0 | A | 0.0 | Measured motor current |
| g_safetyState | UINT8 | 0~3 | enum | 0 (INIT) | Current safety state |
| g_faultMask | UINT32 | 0x0~0xFFFFFFFF | bitmask | 0x0 | Active fault flags |
| g_pidIntegral | FLOAT32 | -100.0 ~ 100.0 | - | 0.0 | PID integral accumulator |
| g_pidErrorPrev | FLOAT32 | -720.0 ~ 720.0 | deg | 0.0 | Previous PID error |
| g_sensorFailCnt | UINT16 | 0 ~ 65535 | count | 0 | Consecutive sensor fail |

---

## 5. State Machine / 상태 머신 전이 테이블

| State ID | State Name | Entry Action | During Action | Exit Action |
|---|---|---|---|---|
| 0 | INIT | Initialize all modules | Self-test | Enable watchdog |
| 1 | NORMAL | Enable full torque | PID control loop | Store last values |
| 2 | DEGRADED | Reduce max torque 50% | Limited control | Log transition |
| 3 | SAFE_STATE | Set torque=0 | Monitor recovery | - |

---

## 6. MISRA-C Compliance / MISRA-C 준수
<!-- GUIDE: MISRA-C:2012 규칙 준수 여부를 확인하세요 -->

| Rule | Category | Description | Status |
|---|---|---|---|
| Rule 1.3 | Required | No undefined/unspecified behavior | ☐ Compliant |
| Rule 10.1 | Required | Operands shall not be of inappropriate essential type | ☐ Compliant |
| Rule 11.3 | Required | Cast between pointer to object and integral type | ☐ Compliant |
| Rule 14.3 | Required | Controlling expression shall not be invariant | ☐ Compliant |
| Rule 17.7 | Required | Return value of non-void function shall be used | ☐ Compliant |
| Rule 21.3 | Required | Memory allocation functions shall not be used | ☐ Compliant |

---

## 7. NVM Data Layout / NVM 데이터 배치

| Block ID | Name | Size (B) | Content | CRC |
|---|---|---|---|---|
| NVM_BLK_01 | Calibration Data | 256 | PID gains, lookup tables | CRC32 |
| NVM_BLK_02 | DTC Storage | 512 | Up to 32 DTCs | CRC16 |
| NVM_BLK_03 | Runtime Data | 64 | Operating hours, counters | CRC16 |

---

## 8. Traceability / 추적성

| SWE.2 Component | SWE.3 Module/Function | SWE.4 Unit Test |
|---|---|---|
| ControlLogic | CalcAssistTorque() | UT-001~005 |
| SensorInput | ReadSteeringAngle(), FilterSensorValue() | UT-006~010 |
| SafetyMonitor | UpdateSafetyState(), CheckSensorValidity() | UT-011~015 |
| ActuatorOutput | SetMotorPWM(), ControlCurrent() | UT-016~018 |

---

## 9. Review Criteria / 검토 기준
| # | Criteria | Check |
|---|---|---|
| 1 | All SWE.2 components have detailed designs | ☐ |
| 2 | Algorithm pseudocode complete and correct | ☐ |
| 3 | Data dictionary complete (all global variables) | ☐ |
| 4 | MISRA-C compliance checklist reviewed | ☐ |
| 5 | Function pre/post conditions defined | ☐ |
| 6 | NVM layout documented | ☐ |
| 7 | Traceability to SWE.2 and SWE.4 complete | ☐ |

---
*Generated by ASPICE Process Manager*
