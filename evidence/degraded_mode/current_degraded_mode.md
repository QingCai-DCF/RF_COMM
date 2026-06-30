# Current Degraded Mode

Generated: 2026-06-28T01:52:46+08:00

MODE = LANE0_DEGRADED_RELIABLE_2LANE_STATIC

Reason: the fresh P1.1 raw matrix shows lane0 raw pulses in both directions (`AB_L0`, `BA_L0`) while `AB_L1` fails at raw RX. The ACK-only lane0 run passes framed protocol acceptance by UART end-to-end counters, and the degraded lane0 capped soak passes with 256B payload, zero unrecovered loss, and shutdown-after-run.

## Current Use

```text
payload lane mask = 0x00000001
ack lane mask = 0x00000001
payload bytes = 256
stage seconds = 300
sent = 260068
rx_ok = 260068
tx_fail = 0
loss = 0.0%
win_rx_mbps = 1.775
window_to_shutdown_end_s = 371.9
BAD_DIR_FINAL = AB_L1
BAD_DIR_LAYER = NO_RX_RAW_PULSE
```

## Evidence

- G1 frozen baseline: `evidence/G1_freeze/G1_frozen_summary.txt`
- RX-only matrix: `evidence/lane_matrix/rxonly_matrix.md`
- Constrained matrix: `reports/constrained_2lane_static_baseline_current.summary.txt`
- Degraded soak summary: `reports/lane0_hw_loopback_safe_20260628_013620.summary.txt`
- Degraded UART log: `reports/uart_lane0_hw_loopback_safe_20260628_013620.log`

```text
RF_COMM_CURRENT_DEGRADED_MODE mode=LANE0_DEGRADED_RELIABLE_2LANE_STATIC status=PASS_LANE0_DEGRADED_SELECTED
ACK_PROTOCOL_PASS=1
DEGRADED_SMOKE_PASS=1
DEGRADED_SOAK_PASS=1
DEGRADED_SENT=260068
DEGRADED_RX_OK=260068
DEGRADED_TX_FAIL=0
DEGRADED_WINDOW_TO_SHUTDOWN_END_SECONDS=371.9
```
