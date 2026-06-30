# UART Control Acceptance

Generated: 2026-06-28T01:52:46+08:00

Status: `PASS_PS_LOCAL_UART_OBSERVED_WITH_OFFLINE_CONTROL_PROTOCOL`

This acceptance is scoped to PS-local execution with UART-observed counters plus offline PS/PC control-protocol gates. It does not claim an interactive UART shell and does not claim real Ethernet. The physical START/STOP/READ/SHUTDOWN evidence comes from the capped lane0 run; STATUS/CONFIG/CLEAR protocol behavior is covered by the PS bridge static/unit/offline mock gates.

| command | status |
| --- | --- |
| STATUS | PASS via UART `PSPS_STATS`/stage summary and offline STATUS protocol |
| CONFIG lane mask | PASS, lane mask `0x00000001` observed in UART stage |
| CONFIG payload bytes | PASS, payload bytes `256` observed in UART banner |
| START | PASS, PS-local capped TFDU run started and produced counters |
| STOP | PASS, `PSPS_RUN_ONCE_DONE link_disabled=1` |
| READ counters | PASS, UART stats/stage summary reports sent/rx_ok/error counters |
| CLEAR error | PASS offline protocol/static gate covers CLEAR handling |
| SHUTDOWN | PASS, shutdown-after-run exit path completed |

## Evidence

- ACK-only protocol summary: `reports/p0_ack_only_safe_20260628_012612_488_41700.summary.txt`
- Degraded capped run summary: `reports/lane0_hw_loopback_safe_20260628_013620.summary.txt`
- Degraded UART log: `reports/uart_lane0_hw_loopback_safe_20260628_013620.log`
- PS/PC offline gates: `reports/ps_pc_offline_gates_20260627_224230.summary.txt`

```text
RF_COMM_UART_CONTROL_ACCEPTANCE status=PASS_PS_LOCAL_UART_OBSERVED_WITH_OFFLINE_CONTROL_PROTOCOL
PS_LOCAL_START_STOP_READ_SHUTDOWN_PASS=1
OFFLINE_STATUS_CONFIG_CLEAR_PROTOCOL_PASS=1
UART_OBSERVED_PAYLOAD_BYTES=256
UART_OBSERVED_STAGE_SECONDS=300
UART_OBSERVED_SENT=260068
UART_OBSERVED_RX_OK=260068
UART_OBSERVED_TX_FAIL=0
SHUTDOWN_AFTER_RUN_PASS=1
INTERACTIVE_UART_SHELL_CLAIM=0
REAL_ETHERNET_CLAIM=0
DOCUMENT_GENERATION_NO_HARDWARE_PROGRAMMING=1
DOCUMENT_GENERATION_NO_UART_WRITE=1
DOCUMENT_GENERATION_NO_TFDU_DRIVE=1
```
