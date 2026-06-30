# S05 Rotation Deferred

Generated: 2026-06-28T01:52:46+08:00

status = DEFERRED_NO_ROTATION_FIXTURE
reason = 当前无法移动硬件，无法进入真实旋转环境
not_failed = true
replacement_evidence = stationary capped baseline + rotating offline model
promotion_condition = 可移动硬件并具备旋转工装后重新执行 S05_rotation_fixture_acceptance_plan

## Evidence

- Rotating offline model: `reports/rotating_autoroute_offline_evidence_current.md`
- External preconditions: `reports/external_preconditions_current.md`

```text
RF_COMM_S05_ROTATION_DEFERRED status=DEFERRED_NO_ROTATION_FIXTURE
ROTATION_MODEL_AVAILABLE=1
REAL_ROTATION_PASS=0
NOT_FAILED=1
NO_HARDWARE_PROGRAMMING=1
NO_UART_WRITE=1
NO_TFDU_DRIVE=1
```
