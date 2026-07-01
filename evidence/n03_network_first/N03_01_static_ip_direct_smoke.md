# N03-1 Static IP Direct Smoke

Generated: 2026-07-01T11:46:54

Verdict: `REAL_BOARD_PENDING`

Current board target: 192.168.10.2:5001. Current preflight: PC Ethernet lacks 192.168.10.1/24 static direct IP. N03 static direct PC preflight pass=0. Current shell admin=0. Recommended static IP command: `New-NetIPAddress -InterfaceAlias "以太网" -IPAddress 192.168.10.1 -PrefixLength 24 -SkipAsSource $false`. Elevated setup command: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\user\Documents\RF_COMM\tools\setup_n03_static_direct_network_safe.ps1 -InterfaceAlias 以太网 -ExpectedPcIp 192.168.10.1 -PrefixLength 24 -TargetHost 192.168.10.2 -Port 5001 -TimeoutMs 1000 -Apply -AddFirewallRule`. UAC launch command: `Start-Process -FilePath powershell.exe -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File C:\Users\user\Documents\RF_COMM\tools\setup_n03_static_direct_network_safe.ps1 -InterfaceAlias 以太网 -ExpectedPcIp 192.168.10.1 -PrefixLength 24 -TargetHost 192.168.10.2 -Port 5001 -TimeoutMs 1000 -Apply -AddFirewallRule' -Verb RunAs`. This file is a runbook/status record, not a real-board PASS transcript.

## Stage Matrix

| item | title | status | evidence | next required evidence | allowed claim |
| --- | --- | --- | --- | --- | --- |
| N03-0 | scope switch and IR physical deferred matrix | PASS_DEFERRED_GATE | N03_00_scope_switch_note.md; N03_00_ir_physical_deferred_matrix.md | none for scope switch | IR physical is deferred, not failed for N03 |
| N03-1 | static IP direct smoke | REAL_BOARD_PENDING | reports/n03_static_direct_network_preflight_current.summary.txt; reports/n03_network_first_acceptance_safe_20260701_113628.summary.txt; reports/external_preconditions_current.json; PC Ethernet lacks 192.168.10.1/24 static direct IP | board UART/TCP transcript proving ETH link up and TCP connect to 192.168.10.2:5001 | real static TCP only if safe wrapper N03_STATIC_DIRECT_TCP_PASS=1 |
| N03-2 | TCP hello/status/build-id | PASS_OFFLINE_RECONNECT_10X_REAL_PENDING | reports/n03_network_first_acceptance_safe_20260701_113628.summary.txt; reports/ps_pc_offline_gates_20260701_113607.summary.txt; reports/n03_offline_reconnect_matrix_current.md; reports/n03_offline_reconnect_matrix_current.csv | real board HELLO/STATUS/GET_BUILD_ID transcript | real HELLO covered only if safe wrapper static smoke passed |
| N03-3 | TCP command protocol coverage | PASS_OFFLINE_REAL_PENDING | reports/n03_network_first_acceptance_safe_20260701_113628.summary.txt; reports/ps_pc_offline_gates_20260701_113607.summary.txt; reports/protocol_contract_current.md | real board command matrix with ACK/ERR for all N03 commands | N03_TCP_PROTOCOL_COMMAND_PASS is real only if safe wrapper marker is 1 |
| N03-4 | PC to PS memory echo | PASS_OFFLINE_REAL_PENDING | reports/n03_network_first_acceptance_safe_20260701_113628.summary.txt; reports/n03_network_first_acceptance_safe_20260701_113628.matrix.csv; reports/ps_pc_offline_gates_20260701_113607.summary.txt | real board memory echo matrix with payload_mismatch=0 | N03_TCP_PAYLOAD_MEMORY_ECHO_PASS is real only if safe wrapper marker is 1 |
| N03-5 | PC to PS to PL synthetic loopback | PASS_OFFLINE_REAL_PENDING | reports/n03_network_first_acceptance_safe_20260701_113628.summary.txt; reports/n03_network_first_acceptance_safe_20260701_113628.matrix.csv; reports/ps_pc_offline_gates_20260701_113607.summary.txt | real board PS/PL synthetic matrix with DMA counters and payload_mismatch=0 | N03_TCP_TO_PSPL_SYNTHETIC_LOOPBACK_PASS is real only if safe wrapper marker is 1 |
| N03-6 | DHCP timeout plus static fallback | SOURCE_READY_UART_INCONCLUSIVE_TCP_PENDING | reports/ps_lwip_bridge_static_current.md; reports/ps_uart_boot_probe_20260701_000400.summary.txt | UART DHCP_TIMEOUT and STATIC_FALLBACK_IP=192.168.10.2 plus TCP reconnect evidence | source supports fallback; no real fallback pass yet |
| N03-7 | PC-hosted DHCP lease | DEFERRED_NO_PC_DHCP_SERVER_PREFLIGHTED | reports/n03_pc_hosted_dhcp_preflight_current.summary.txt; reports/n03_pc_hosted_dhcp_preflight_current.md; reports/n03_pc_hosted_dhcp_preflight_current.json; status=BLOCKED_ETHERNET_LINK_DOWN | DHCP DISCOVER/OFFER/REQUEST/ACK and board IP in pool | PC DHCP preflight only; no DHCP lease pass |
| N03-8 | payload matrix and throughput | PASS_OFFLINE_LOCALHOST_MATRIX_REAL_THROUGHPUT_PENDING | reports/ps_pc_offline_gates_20260701_113607.summary.txt; reports/n03_offline_payload_matrix_current.md; reports/n03_offline_payload_matrix_current.csv | real board 16..8192 byte payload matrix and throughput CSV | offline localhost payload matrix/tooling only; no real throughput pass |
| N03-9 | link recovery and negative tests | PASS_OFFLINE_RECONNECT_20X_PAYLOAD_PROTOCOL_NEGATIVE_REAL_LINK_PENDING | reports/n03_network_first_acceptance_safe_20260701_113628.summary.txt; reports/n03_network_first_acceptance_safe_20260701_113628.matrix.csv; reports/ps_pc_offline_gates_20260701_113607.summary.txt; reports/n03_offline_reconnect_matrix_current.md; reports/n03_offline_reconnect_matrix_current.csv; reports/no_ethernet_network_boundary_evidence_current.md; reports/ps_lwip_bridge_static_current.md | real reconnect/disconnect matrix and negative command matrix | offline 10x/20x reconnect, payload echo, bad-arg negatives, and source/boundary protocol-fault negatives only; real link recovery only if safe wrapper reconnect and negative markers are 1 |
| N03-10 | network-first acceptance package | PACKAGE_PARTIAL_REAL_BOARD_PENDING | evidence/n03_network_first; reports/n03_static_direct_network_preflight_current.md; reports/n03_network_first_acceptance_safe_20260701_113628.md; reports/n03_network_first_readiness_current.md | N03-1..N03-6, N03-8, and N03-9 real board evidence | package is ready for review, not final N03 pass |

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
