# N03-10 Network-first Acceptance Package

Generated: 2026-07-01T11:22:56

Verdict: `PACKAGE_PARTIAL_REAL_BOARD_PENDING`

This package is a current-state N03 deliverable bundle. It proves source/offline/mock progress, incorporates the latest safe real-board wrapper result when present, and preserves the remaining real-board blockers. It does not claim the final N03 baseline PASS.

## Stage Matrix

| item | title | status | evidence | next required evidence | allowed claim |
| --- | --- | --- | --- | --- | --- |
| N03-0 | scope switch and IR physical deferred matrix | PASS_DEFERRED_GATE | N03_00_scope_switch_note.md; N03_00_ir_physical_deferred_matrix.md | none for scope switch | IR physical is deferred, not failed for N03 |
| N03-1 | static IP direct smoke | BLOCKED_PC_STATIC_IP_NOT_CONFIGURED | reports/n03_static_direct_network_preflight_current.summary.txt; reports/n03_network_first_acceptance_safe_20260701_112249.summary.txt; reports/external_preconditions_current.json; PC Ethernet lacks 192.168.10.1/24 static direct IP | board UART/TCP transcript proving ETH link up and TCP connect to 192.168.10.2:5001 | real static TCP only if safe wrapper N03_STATIC_DIRECT_TCP_PASS=1 |
| N03-2 | TCP hello/status/build-id | PASS_OFFLINE_REAL_PENDING | reports/n03_network_first_acceptance_safe_20260701_112249.summary.txt; reports/ps_pc_offline_gates_20260701_112224.summary.txt | real board HELLO/STATUS/GET_BUILD_ID transcript | real HELLO covered only if safe wrapper static smoke passed |
| N03-3 | TCP command protocol coverage | PASS_OFFLINE_REAL_PENDING | reports/n03_network_first_acceptance_safe_20260701_112249.summary.txt; reports/ps_pc_offline_gates_20260701_112224.summary.txt; reports/protocol_contract_current.md | real board command matrix with ACK/ERR for all N03 commands | N03_TCP_PROTOCOL_COMMAND_PASS is real only if safe wrapper marker is 1 |
| N03-4 | PC to PS memory echo | PASS_OFFLINE_REAL_PENDING | reports/n03_network_first_acceptance_safe_20260701_112249.summary.txt; reports/n03_network_first_acceptance_safe_20260701_112249.matrix.csv; reports/ps_pc_offline_gates_20260701_112224.summary.txt | real board memory echo matrix with payload_mismatch=0 | N03_TCP_PAYLOAD_MEMORY_ECHO_PASS is real only if safe wrapper marker is 1 |
| N03-5 | PC to PS to PL synthetic loopback | PASS_OFFLINE_REAL_PENDING | reports/n03_network_first_acceptance_safe_20260701_112249.summary.txt; reports/n03_network_first_acceptance_safe_20260701_112249.matrix.csv; reports/ps_pc_offline_gates_20260701_112224.summary.txt | real board PS/PL synthetic matrix with DMA counters and payload_mismatch=0 | N03_TCP_TO_PSPL_SYNTHETIC_LOOPBACK_PASS is real only if safe wrapper marker is 1 |
| N03-6 | DHCP timeout plus static fallback | SOURCE_READY_UART_INCONCLUSIVE_TCP_PENDING | reports/ps_lwip_bridge_static_current.md; reports/ps_uart_boot_probe_20260701_000400.summary.txt | UART DHCP_TIMEOUT and STATIC_FALLBACK_IP=192.168.10.2 plus TCP reconnect evidence | source supports fallback; no real fallback pass yet |
| N03-7 | PC-hosted DHCP lease | DEFERRED_NO_PC_DHCP_SERVER | no PC DHCP server run recorded | DHCP DISCOVER/OFFER/REQUEST/ACK and board IP in pool | no DHCP lease pass |
| N03-8 | payload matrix and throughput | PARTIAL_OFFLINE_APP_SEGMENTATION_REAL_MATRIX_PENDING | reports/ps_pc_offline_gates_20260701_112224.summary.txt | real board 16..8192 byte payload matrix and throughput CSV | offline app-payload segmentation/tooling only; no real throughput pass |
| N03-9 | link recovery and negative tests | PASS_OFFLINE_RECONNECT_PAYLOAD_PROTOCOL_NEGATIVE_REAL_LINK_PENDING | reports/n03_network_first_acceptance_safe_20260701_112249.summary.txt; reports/n03_network_first_acceptance_safe_20260701_112249.matrix.csv; reports/ps_pc_offline_gates_20260701_112224.summary.txt; reports/no_ethernet_network_boundary_evidence_current.md; reports/ps_lwip_bridge_static_current.md | real reconnect/disconnect matrix and negative command matrix | offline reconnect payload echo, bad-arg negatives, and source/boundary protocol-fault negatives only; real link recovery only if safe wrapper reconnect and negative markers are 1 |
| N03-10 | network-first acceptance package | PACKAGE_PARTIAL_REAL_BOARD_PENDING | evidence/n03_network_first; reports/n03_static_direct_network_preflight_current.md; reports/n03_network_first_acceptance_safe_20260701_112249.md | N03-1..N03-6, N03-8, and N03-9 real board evidence | package is ready for review, not final N03 pass |

## Current Source/Offline Evidence

- Offline summary: `reports/ps_pc_offline_gates_20260701_112224.summary.txt`
- Offline app payload segmentation: `PASS` (`8192_bytes_over_512_byte_rfcm_frames` when present)
- Offline reconnect payload echo: `PASS`
- Offline bad-argument negatives: `PASS`
- Offline/source protocol-fault negatives: `PASS`
- No-Ethernet boundary report: `reports/no_ethernet_network_boundary_evidence_current.md`
- No-Ethernet boundary CSV: `reports/no_ethernet_network_boundary_evidence_current.csv`
- No-Ethernet boundary JSON: `reports/no_ethernet_network_boundary_evidence_current.json`
- N03 static direct PC preflight summary: `reports/n03_static_direct_network_preflight_current.summary.txt`
- N03 static direct PC preflight report: `reports/n03_static_direct_network_preflight_current.md`
- N03 static direct PC preflight JSON: `reports/n03_static_direct_network_preflight_current.json`
- Latest elevated static setup launch summary: `reports/n03_static_direct_network_preflight_20260701_002437.summary.txt`
- Latest non-admin static setup apply refusal summary: `reports/n03_static_direct_network_preflight_20260701_105835.summary.txt`
- Latest UART boot probe summary: `reports/ps_uart_boot_probe_20260701_000400.summary.txt`
- Safe real-board wrapper summary: `reports/n03_network_first_acceptance_safe_20260701_112249.summary.txt`
- Safe real-board wrapper report: `reports/n03_network_first_acceptance_safe_20260701_112249.md`
- Safe real-board wrapper matrix: `reports/n03_network_first_acceptance_safe_20260701_112249.matrix.csv`
- Static PS bridge report: `reports/ps_lwip_bridge_static_current.md`
- Protocol contract report: `reports/protocol_contract_current.md`
- External preconditions: `reports/external_preconditions_current.json`
- P7 physical report: `reports/P7_01_2lane_raw_matrix_report.md`

## Final N03 Pass Gate

Do not mark the final N03 network-first baseline as passed until N03-1..N03-6, N03-8, and N03-9 have real board evidence with payload_mismatch=0 and reconnect/link recovery evidence. N03-7 may remain `DEFERRED_NO_PC_DHCP_SERVER` if no PC DHCP server is available.

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
