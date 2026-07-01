# N03-4 PC-PS Memory Echo

Generated: 2026-07-01T10:59:01

Verdict: `PASS_OFFLINE_REAL_PENDING`

Offline/mock memory echo reports payload_mismatch=0. Real board payload matrix remains pending.

## Stage Matrix

| item | title | status | evidence | next required evidence | allowed claim |
| --- | --- | --- | --- | --- | --- |
| N03-0 | scope switch and IR physical deferred matrix | PASS_DEFERRED_GATE | N03_00_scope_switch_note.md; N03_00_ir_physical_deferred_matrix.md | none for scope switch | IR physical is deferred, not failed for N03 |
| N03-1 | static IP direct smoke | BLOCKED_PC_STATIC_IP_NOT_CONFIGURED | reports/n03_static_direct_network_preflight_current.summary.txt; reports/n03_network_first_acceptance_safe_20260701_105854.summary.txt; reports/external_preconditions_current.json; PC Ethernet lacks 192.168.10.1/24 static direct IP | board UART/TCP transcript proving ETH link up and TCP connect to 192.168.10.2:5001 | real static TCP only if safe wrapper N03_STATIC_DIRECT_TCP_PASS=1 |
| N03-2 | TCP hello/status/build-id | PASS_OFFLINE_REAL_PENDING | reports/n03_network_first_acceptance_safe_20260701_105854.summary.txt; reports/ps_pc_offline_gates_20260630_234446.summary.txt | real board HELLO/STATUS/GET_BUILD_ID transcript | real HELLO covered only if safe wrapper static smoke passed |
| N03-3 | TCP command protocol coverage | PASS_OFFLINE_REAL_PENDING | reports/n03_network_first_acceptance_safe_20260701_105854.summary.txt; reports/ps_pc_offline_gates_20260630_234446.summary.txt; reports/protocol_contract_current.md | real board command matrix with ACK/ERR for all N03 commands | N03_TCP_PROTOCOL_COMMAND_PASS is real only if safe wrapper marker is 1 |
| N03-4 | PC to PS memory echo | PASS_OFFLINE_REAL_PENDING | reports/n03_network_first_acceptance_safe_20260701_105854.summary.txt; reports/n03_network_first_acceptance_safe_20260701_105854.matrix.csv; reports/ps_pc_offline_gates_20260630_234446.summary.txt | real board memory echo matrix with payload_mismatch=0 | N03_TCP_PAYLOAD_MEMORY_ECHO_PASS is real only if safe wrapper marker is 1 |
| N03-5 | PC to PS to PL synthetic loopback | PASS_OFFLINE_REAL_PENDING | reports/n03_network_first_acceptance_safe_20260701_105854.summary.txt; reports/n03_network_first_acceptance_safe_20260701_105854.matrix.csv; reports/ps_pc_offline_gates_20260630_234446.summary.txt | real board PS/PL synthetic matrix with DMA counters and payload_mismatch=0 | N03_TCP_TO_PSPL_SYNTHETIC_LOOPBACK_PASS is real only if safe wrapper marker is 1 |
| N03-6 | DHCP timeout plus static fallback | SOURCE_READY_UART_INCONCLUSIVE_TCP_PENDING | reports/ps_lwip_bridge_static_current.md; reports/ps_uart_boot_probe_20260701_000400.summary.txt | UART DHCP_TIMEOUT and STATIC_FALLBACK_IP=192.168.10.2 plus TCP reconnect evidence | source supports fallback; no real fallback pass yet |
| N03-7 | PC-hosted DHCP lease | DEFERRED_NO_PC_DHCP_SERVER | no PC DHCP server run recorded | DHCP DISCOVER/OFFER/REQUEST/ACK and board IP in pool | no DHCP lease pass |
| N03-8 | payload matrix and throughput | PARTIAL_OFFLINE_REAL_MATRIX_PENDING | reports/ps_pc_offline_gates_20260630_234446.summary.txt | real board 16..8192 byte payload matrix and throughput CSV | offline smoke payloads only |
| N03-9 | link recovery and negative tests | PASS_OFFLINE_REAL_LINK_PENDING | reports/n03_network_first_acceptance_safe_20260701_105854.summary.txt; reports/n03_network_first_acceptance_safe_20260701_105854.matrix.csv; reports/ps_pc_offline_gates_20260630_234446.summary.txt | real reconnect/disconnect matrix and negative command matrix | real link recovery only if safe wrapper reconnect and negative markers are 1 |
| N03-10 | network-first acceptance package | PACKAGE_PARTIAL_REAL_BOARD_PENDING | evidence/n03_network_first; reports/n03_static_direct_network_preflight_current.md; reports/n03_network_first_acceptance_safe_20260701_105854.md | N03-1..N03-6, N03-8, and N03-9 real board evidence | package is ready for review, not final N03 pass |

## Non-Claims

```text
IR_PHYSICAL_PASS=0
2LANE_PASS=0
REAL_IR_DATA_ROUNDTRIP_PASS=0
ROTATION_PASS=0
4LANE_PASS=0
8LANE_PASS=0
FINAL_TARGET_PASS=0
```
