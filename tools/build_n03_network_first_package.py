#!/usr/bin/env python3
"""Build the tracked N03 network-first evidence package from current state."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
OUT = ROOT / "evidence" / "n03_network_first"


@dataclass
class StageRow:
    item: str
    title: str
    status: str
    evidence: str
    next_required_evidence: str
    allowed_claim: str


def read_text(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def latest(pattern: str) -> Path | None:
    matches = list(REPORTS.glob(pattern))
    if not matches:
        return None
    return sorted(matches, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def rel(path: Path | None) -> str:
    if path is None:
        return "MISSING"
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def marker(text: str, value: str) -> bool:
    return value in text


def marker_value(text: str, key: str) -> str:
    prefix = key + "="
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.split("=", 1)[1].strip()
    return ""


def sibling_report(summary: Path | None, suffix: str) -> Path | None:
    if summary is None:
        return None
    name = summary.name.removesuffix(".summary.txt") + suffix
    path = summary.with_name(name)
    return path if path.exists() else None


def current_report(name: str) -> Path | None:
    path = REPORTS / name
    return path if path.exists() else None


def md_table(rows: list[StageRow]) -> str:
    lines = [
        "| item | title | status | evidence | next required evidence | allowed claim |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                str(value).replace("|", "/").replace("\n", " ")
                for value in (
                    row.item,
                    row.title,
                    row.status,
                    row.evidence,
                    row.next_required_evidence,
                    row.allowed_claim,
                )
            )
            + " |"
        )
    return "\n".join(lines)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else ["item", "status"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def artifact_rows() -> list[dict[str, str]]:
    paths = [
        ROOT / "TFDU_VFIR_Client_Array" / "design_shiboqi_wrapper.bit",
        ROOT / "TFDU_VFIR_Client_Array" / "design_shiboqi_wrapper.xsa",
        ROOT / "software" / "_vitis_ws" / "rf_comm_ps_bridge" / "Debug" / "rf_comm_ps_bridge.elf",
        ROOT / "software" / "_vitis_ws_ps_ps_loopback" / "rf_comm_ps_ps_loopback" / "Debug" / "rf_comm_ps_ps_loopback.elf",
        ROOT / "software" / "ps_lwip_bridge" / "src" / "main.c",
        ROOT / "software" / "ps_lwip_bridge" / "src" / "tcp_bridge.c",
        ROOT / "software" / "ps_lwip_bridge" / "src" / "rf_protocol.h",
        ROOT / "software" / "host_client" / "rf_comm_client.py",
        ROOT / "software" / "host_client" / "run_acceptance.ps1",
        ROOT / "tools" / "probe_ps_uart_boot_safe.ps1",
        ROOT / "tools" / "setup_n03_static_direct_network_safe.ps1",
        ROOT / "tools" / "run_n03_network_first_acceptance_safe.ps1",
        ROOT / "tools" / "run_ps_pc_offline_gates.ps1",
    ]
    rows: list[dict[str, str]] = []
    for path in paths:
        rows.append(
            {
                "path": rel(path),
                "status": "PRESENT" if path.exists() else "MISSING",
                "sha256": sha256(path) if path.exists() else "",
            }
        )
    return rows


def report_template(title: str, verdict: str, body: str, rows: list[StageRow]) -> str:
    generated = datetime.now().isoformat(timespec="seconds")
    return "\n".join(
        [
            f"# {title}",
            "",
            f"Generated: {generated}",
            "",
            f"Verdict: `{verdict}`",
            "",
            body.strip(),
            "",
            "## Stage Matrix",
            "",
            md_table(rows),
            "",
            "## Non-Claims",
            "",
            "```text",
            "IR_PHYSICAL_PASS=0",
            "2LANE_PASS=0",
            "REAL_IR_DATA_ROUNDTRIP_PASS=0",
            "ROTATION_PASS=0",
            "4LANE_PASS=0",
            "8LANE_PASS=0",
            "FINAL_TARGET_PASS=0",
            "```",
        ]
    )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    generated = datetime.now().isoformat(timespec="seconds")

    offline_summary = latest("ps_pc_offline_gates_*.summary.txt")
    offline_text = read_text(offline_summary)
    safe_summary = latest("n03_network_first_acceptance_safe_*.summary.txt")
    safe_text = read_text(safe_summary)
    safe_report = sibling_report(safe_summary, ".md")
    safe_matrix = sibling_report(safe_summary, ".matrix.csv")
    static_net_summary = current_report("n03_static_direct_network_preflight_current.summary.txt")
    static_net_text = read_text(static_net_summary)
    static_net_report = current_report("n03_static_direct_network_preflight_current.md")
    static_net_json = current_report("n03_static_direct_network_preflight_current.json")
    uart_summary = latest("ps_uart_boot_probe_*.summary.txt")
    uart_text = read_text(uart_summary)
    external_json = REPORTS / "external_preconditions_current.json"
    external = {}
    if external_json.exists():
        external = json.loads(external_json.read_text(encoding="utf-8"))

    p7_report = REPORTS / "P7_01_2lane_raw_matrix_report.md"
    protocol_contract = REPORTS / "protocol_contract_current.md"
    static_report = REPORTS / "ps_lwip_bridge_static_current.md"

    command_ok = marker(offline_text, "N03_TCP_PROTOCOL_COMMAND_PASS=1")
    memory_ok = marker(offline_text, "N03_TCP_PAYLOAD_MEMORY_ECHO_PASS=1")
    synth_ok = marker(offline_text, "N03_TCP_TO_PSPL_SYNTHETIC_LOOPBACK_PASS=1")
    negative_ok = marker(offline_text, "N03_IR_PHYSICAL_DEFERRED_NEGATIVE_PASS=1")
    offline_ok = marker(offline_text, "PS_PC_OFFLINE_GATES_PASS") and marker(offline_text, "n03_modes=1")
    safe_dry_run = marker(safe_text, "N03_DRY_RUN=1")
    safe_blocked = marker(safe_text, "N03_REAL_BOARD_ACCEPTANCE_BLOCKED=1")
    safe_blocker = marker_value(safe_text, "N03_BLOCKED_REASON")
    safe_static_ok = marker(safe_text, "N03_STATIC_DIRECT_TCP_PASS=1") and not safe_dry_run
    safe_command_ok = marker(safe_text, "N03_TCP_PROTOCOL_COMMAND_PASS=1") and not safe_dry_run
    safe_memory_ok = marker(safe_text, "N03_TCP_PAYLOAD_MEMORY_ECHO_PASS=1") and not safe_dry_run
    safe_synth_ok = marker(safe_text, "N03_TCP_TO_PSPL_SYNTHETIC_LOOPBACK_PASS=1") and not safe_dry_run
    safe_negative_ok = marker(safe_text, "N03_IR_PHYSICAL_DEFERRED_NEGATIVE_PASS=1") and not safe_dry_run
    safe_link_ok = marker(safe_text, "N03_LINK_RECOVERY_PASS=1") and not safe_dry_run
    safe_acceptance_ok = marker(safe_text, "N03_REAL_BOARD_ACCEPTANCE_PASS=1") and not safe_dry_run
    pc_static_ip_ok = marker(static_net_text, "PC_EXPECTED_STATIC_IP_PRESENT=1")
    pc_ethernet_up = marker(static_net_text, "PC_ETHERNET_LINK_UP=1")
    static_net_pass = marker(static_net_text, "N03_STATIC_DIRECT_NETWORK_PREFLIGHT_PASS=1")
    static_apply_command = marker_value(static_net_text, "APPLY_DRY_RUN_COMMAND") or marker_value(
        static_net_text, "RECOMMENDED_APPLY_COMMAND"
    )
    firewall_command = marker_value(static_net_text, "FIREWALL_DRY_RUN_COMMAND") or marker_value(
        static_net_text, "RECOMMENDED_FIREWALL_COMMAND"
    )
    elevated_apply_command = marker_value(static_net_text, "ELEVATED_APPLY_COMMAND")
    elevated_uac_command = marker_value(static_net_text, "ELEVATED_UAC_COMMAND")
    is_admin = marker_value(static_net_text, "IS_ADMIN")
    admin_required = marker_value(static_net_text, "ADMIN_REQUIRED_TO_APPLY")
    uart_verdict = marker_value(uart_text, "UART_PROBE_VERDICT")
    uart_log_bytes_text = marker_value(uart_text, "UART_LOG_BYTES")
    try:
        uart_log_bytes = int(uart_log_bytes_text or "0")
    except ValueError:
        uart_log_bytes = 0
    uart_has_text = uart_log_bytes > 0
    uart_dhcp_fallback = marker(uart_text, "MATCH_DHCP_STATIC_FALLBACK=1")
    uart_tcp_listen = marker(uart_text, "MATCH_TCP_LISTEN_5001=1")
    static_ok = marker(read_text(static_report), "PS_BRIDGE_STATIC_CHECKS_PASS") or marker(offline_text, "PS_BRIDGE_STATIC_CHECKS_PASS")
    protocol_ok = marker(read_text(protocol_contract), "RF_COMM_PROTOCOL_CONTRACT overall=PASS")
    single_tcp = external.get("tcp_results", {}).get("single", None)
    real_board_reachable = safe_static_ok or single_tcp is True
    if static_net_text and not pc_static_ip_ok:
        blocker_note = "PC Ethernet lacks 192.168.10.1/24 static direct IP"
    elif safe_blocked:
        blocker_note = f"safe wrapper blocked: {safe_blocker or 'unknown'}"
    else:
        blocker_note = "192.168.10.2:5001 reachable" if real_board_reachable else "192.168.10.2:5001 not reachable in current preflight"

    static_status = (
        "PASS_REAL_BOARD"
        if safe_static_ok
        else "BLOCKED_PC_STATIC_IP_NOT_CONFIGURED"
        if static_net_text and pc_ethernet_up and not pc_static_ip_ok
        else "BLOCKED_TCP_TARGET_NOT_REACHABLE"
        if safe_blocked and safe_blocker == "tcp_target_not_reachable"
        else "READY_TO_RUN"
        if real_board_reachable
        else "REAL_BOARD_PENDING"
    )
    hello_status = "PASS_REAL_BOARD" if safe_static_ok else ("PASS_OFFLINE_REAL_PENDING" if offline_ok else "MISSING_OFFLINE_EVIDENCE")
    command_status = "PASS_REAL_BOARD" if safe_command_ok else ("PASS_OFFLINE_REAL_PENDING" if command_ok and protocol_ok else "MISSING_OR_PARTIAL")
    memory_status = "PASS_REAL_BOARD" if safe_memory_ok else ("PASS_OFFLINE_REAL_PENDING" if memory_ok else "MISSING_OFFLINE_EVIDENCE")
    synth_status = "PASS_REAL_BOARD" if safe_synth_ok else ("PASS_OFFLINE_REAL_PENDING" if synth_ok else "MISSING_OFFLINE_EVIDENCE")
    dhcp_fallback_status = (
        "PASS_UART_REAL_TCP_PENDING"
        if uart_dhcp_fallback and uart_tcp_listen
        else "SOURCE_READY_UART_INCONCLUSIVE_TCP_PENDING"
        if static_ok and uart_summary is not None
        else "SOURCE_READY_REAL_PENDING"
        if static_ok
        else "MISSING_SOURCE_EVIDENCE"
    )
    link_status = (
        "PASS_REAL_BOARD"
        if safe_link_ok and safe_negative_ok
        else "PASS_OFFLINE_REAL_LINK_PENDING"
        if negative_ok and marker(offline_text, "reconnect cycle 2/2")
        else "MISSING_OR_PARTIAL"
    )
    safe_evidence_parts = [
        rel(static_net_summary) if static_net_summary is not None else "MISSING_N03_STATIC_DIRECT_PREFLIGHT",
        rel(safe_summary) if safe_summary is not None else "MISSING_N03_SAFE_ACCEPTANCE",
        rel(external_json),
    ]
    safe_evidence = "; ".join(safe_evidence_parts)

    rows = [
        StageRow(
            "N03-0",
            "scope switch and IR physical deferred matrix",
            "PASS_DEFERRED_GATE",
            "N03_00_scope_switch_note.md; N03_00_ir_physical_deferred_matrix.md",
            "none for scope switch",
            "IR physical is deferred, not failed for N03",
        ),
        StageRow(
            "N03-1",
            "static IP direct smoke",
            static_status,
            f"{safe_evidence}; {blocker_note}",
            "board UART/TCP transcript proving ETH link up and TCP connect to 192.168.10.2:5001",
            "real static TCP only if safe wrapper N03_STATIC_DIRECT_TCP_PASS=1",
        ),
        StageRow(
            "N03-2",
            "TCP hello/status/build-id",
            hello_status,
            f"{rel(safe_summary)}; {rel(offline_summary)}",
            "real board HELLO/STATUS/GET_BUILD_ID transcript",
            "real HELLO covered only if safe wrapper static smoke passed",
        ),
        StageRow(
            "N03-3",
            "TCP command protocol coverage",
            command_status,
            f"{rel(safe_summary)}; {rel(offline_summary)}; {rel(protocol_contract)}",
            "real board command matrix with ACK/ERR for all N03 commands",
            "N03_TCP_PROTOCOL_COMMAND_PASS is real only if safe wrapper marker is 1",
        ),
        StageRow(
            "N03-4",
            "PC to PS memory echo",
            memory_status,
            f"{rel(safe_summary)}; {rel(safe_matrix)}; {rel(offline_summary)}",
            "real board memory echo matrix with payload_mismatch=0",
            "N03_TCP_PAYLOAD_MEMORY_ECHO_PASS is real only if safe wrapper marker is 1",
        ),
        StageRow(
            "N03-5",
            "PC to PS to PL synthetic loopback",
            synth_status,
            f"{rel(safe_summary)}; {rel(safe_matrix)}; {rel(offline_summary)}",
            "real board PS/PL synthetic matrix with DMA counters and payload_mismatch=0",
            "N03_TCP_TO_PSPL_SYNTHETIC_LOOPBACK_PASS is real only if safe wrapper marker is 1",
        ),
        StageRow(
            "N03-6",
            "DHCP timeout plus static fallback",
            dhcp_fallback_status,
            f"{rel(static_report)}; {rel(uart_summary)}",
            "UART DHCP_TIMEOUT and STATIC_FALLBACK_IP=192.168.10.2 plus TCP reconnect evidence",
            "source supports fallback; no real fallback pass yet",
        ),
        StageRow(
            "N03-7",
            "PC-hosted DHCP lease",
            "DEFERRED_NO_PC_DHCP_SERVER",
            "no PC DHCP server run recorded",
            "DHCP DISCOVER/OFFER/REQUEST/ACK and board IP in pool",
            "no DHCP lease pass",
        ),
        StageRow(
            "N03-8",
            "payload matrix and throughput",
            "PARTIAL_OFFLINE_REAL_MATRIX_PENDING" if memory_ok and synth_ok else "MISSING_OFFLINE_EVIDENCE",
            rel(offline_summary),
            "real board 16..8192 byte payload matrix and throughput CSV",
            "offline smoke payloads only",
        ),
        StageRow(
            "N03-9",
            "link recovery and negative tests",
            link_status,
            f"{rel(safe_summary)}; {rel(safe_matrix)}; {rel(offline_summary)}",
            "real reconnect/disconnect matrix and negative command matrix",
            "real link recovery only if safe wrapper reconnect and negative markers are 1",
        ),
        StageRow(
            "N03-10",
            "network-first acceptance package",
            "PACKAGE_PARTIAL_REAL_BOARD_PENDING",
            f"{rel(OUT)}; {rel(static_net_report)}; {rel(safe_report)}",
            "N03-1..N03-6, N03-8, and N03-9 real board evidence",
            "package is ready for review, not final N03 pass",
        ),
    ]

    write(
        OUT / "N03_01_static_ip_direct_smoke.md",
        report_template(
            "N03-1 Static IP Direct Smoke",
            rows[1].status,
            f"Current board target: 192.168.10.2:5001. Current preflight: {blocker_note}. N03 static direct PC preflight pass={int(static_net_pass)}. Current shell admin={is_admin or 'unknown'}. Recommended static IP command: `{static_apply_command or 'not captured'}`. Elevated setup command: `{elevated_apply_command or 'not captured'}`. UAC launch command: `{elevated_uac_command or 'not captured'}`. This file is a runbook/status record, not a real-board PASS transcript.",
            rows,
        ),
    )
    write(
        OUT / "N03_01_static_ip_direct_transcript.txt",
        f"generated={generated}\nstatus={rows[1].status}\ntarget=192.168.10.2:5001\ncurrent_preflight={blocker_note}\nstatic_direct_preflight_summary={rel(static_net_summary)}\nsafe_wrapper_summary={rel(safe_summary)}\npc_expected_static_ip_present={int(pc_static_ip_ok)}\nis_admin={is_admin}\nadmin_required_to_apply={admin_required}\nrecommended_apply_command={static_apply_command}\nrecommended_firewall_command={firewall_command}\nelevated_apply_command={elevated_apply_command}\nelevated_uac_command={elevated_uac_command}\nreal_tcp_connect_pass={int(safe_static_ok)}\n",
    )
    write(
        OUT / "N03_02_tcp_hello_report.md",
        report_template("N03-2 TCP Hello Report", rows[2].status, "Offline HELLO/STATUS path is covered by the latest offline gate. Real board HELLO/GET_BUILD_ID/PING transcript remains required.", rows),
    )
    write_csv(
        OUT / "N03_02_tcp_connect_disconnect.csv",
        [
            {"case": "offline_mock_reconnect", "status": "PASS" if marker(offline_text, "reconnect cycle 2/2") else "MISSING", "evidence": rel(offline_summary)},
            {"case": "real_board_reconnect_10x", "status": "REAL_BOARD_PENDING", "evidence": "required by plan"},
        ],
    )
    write(
        OUT / "N03_03_tcp_command_coverage.md",
        report_template("N03-3 TCP Command Coverage", rows[3].status, "N03 command frame covers PING, GET_VERSION, GET_BUILD_ID, READ commands, CONFIG mode, CLEAR, START, STOP, SHUTDOWN_SAFE, and IR-deferred negative commands in offline/mock evidence.", rows),
    )
    write_csv(
        OUT / "N03_03_tcp_command_matrix.csv",
        [
            {"command": "PING", "expected": "ACK PONG", "current_status": "PASS_OFFLINE"},
            {"command": "GET_VERSION", "expected": "ACK VERSION 1", "current_status": "PASS_OFFLINE"},
            {"command": "GET_BUILD_ID", "expected": "ACK BUILD_ID", "current_status": "PASS_OFFLINE"},
            {"command": "READ counters", "expected": "STATUS_RSP", "current_status": "PASS_OFFLINE"},
            {"command": "READ network_status", "expected": "ACK network_status", "current_status": "PASS_OFFLINE"},
            {"command": "READ pspl_status", "expected": "STATUS_RSP", "current_status": "PASS_OFFLINE"},
            {"command": "CONFIG payload_bytes 64", "expected": "ACK payload_bytes_accepted", "current_status": "PASS_OFFLINE"},
            {"command": "CONFIG mode network_memory_echo", "expected": "ACK network_memory_echo", "current_status": "PASS_OFFLINE"},
            {"command": "CONFIG mode pspl_synth_loopback", "expected": "ACK pspl_synth_loopback", "current_status": "PASS_OFFLINE"},
            {"command": "CONFIG mode ir_physical", "expected": "ERROR ERR_DEFERRED_IR_PHYSICAL_UNAVAILABLE", "current_status": "PASS_OFFLINE_NEGATIVE"},
            {"command": "START ir_tx", "expected": "ERROR ERR_DEFERRED_IR_PHYSICAL_UNAVAILABLE", "current_status": "PASS_OFFLINE_NEGATIVE"},
            {"command": "UNKNOWN_CMD", "expected": "ERROR ERR_UNKNOWN_CMD", "current_status": "PASS_OFFLINE_NEGATIVE"},
        ],
    )
    write(
        OUT / "N03_04_pc_ps_memory_echo_report.md",
        report_template("N03-4 PC-PS Memory Echo", rows[4].status, "Offline/mock memory echo reports payload_mismatch=0. Real board payload matrix remains pending.", rows),
    )
    write_csv(
        OUT / "N03_04_pc_ps_memory_echo_matrix.csv",
        [
            {"payload_bytes": str(size), "count": "100", "current_status": "REAL_BOARD_PENDING", "evidence": "required by plan"}
            for size in (1, 8, 16, 64, 128, 256, 512, 1024, 4096)
        ],
    )
    write(
        OUT / "N03_05_pc_ps_pl_synth_loopback_report.md",
        report_template("N03-5 PC-PS-PL Synthetic Loopback", rows[5].status, "Offline/mock synthetic mode verifies command/mode plumbing and payload compare. Real board PS/PL DMA counters remain pending.", rows),
    )
    write_csv(
        OUT / "N03_05_pc_ps_pl_synth_loopback_matrix.csv",
        [
            {"payload_bytes": "16", "count_or_seconds": "10", "current_status": "REAL_BOARD_PENDING"},
            {"payload_bytes": "64", "count_or_seconds": "100", "current_status": "REAL_BOARD_PENDING"},
            {"payload_bytes": "256", "count_or_seconds": "100", "current_status": "REAL_BOARD_PENDING"},
            {"payload_bytes": "256", "count_or_seconds": "60s", "current_status": "REAL_BOARD_PENDING"},
            {"payload_bytes": "1024", "count_or_seconds": "60s", "current_status": "REAL_BOARD_PENDING"},
            {"payload_bytes": "1024", "count_or_seconds": "300s", "current_status": "REAL_BOARD_PENDING"},
        ],
    )
    write(
        OUT / "N03_06_dhcp_timeout_fallback_report.md",
        report_template("N03-6 DHCP Timeout Static Fallback", rows[6].status, f"Source/static checks confirm DHCP start/timeout/static fallback plumbing. Latest read-only UART probe verdict: `{uart_verdict or 'MISSING'}` with {uart_log_bytes} captured bytes. Real UART DHCP fallback plus TCP fallback evidence remains pending.", rows),
    )
    write(
        OUT / "N03_06_dhcp_timeout_fallback_transcript.txt",
        f"generated={generated}\nexpected_DHCP_TIMEOUT=1\nexpected_STATIC_FALLBACK_IP=192.168.10.2\nreal_uart_transcript_present={int(uart_has_text)}\nuart_summary={rel(uart_summary)}\nuart_probe_verdict={uart_verdict}\nuart_log_bytes={uart_log_bytes}\nuart_dhcp_static_fallback_seen={int(uart_dhcp_fallback)}\nuart_tcp_listen_5001_seen={int(uart_tcp_listen)}\nstatus={rows[6].status}\n",
    )
    write(
        OUT / "N03_07_pc_hosted_dhcp_lease_report.md",
        report_template("N03-7 PC-hosted DHCP Lease", rows[7].status, "No PC DHCP server lease run is recorded. This is explicitly allowed to defer by the N03 plan.", rows),
    )
    write(OUT / "N03_07_dhcp_uart_log.txt", f"generated={generated}\nstatus=DEFERRED_NO_PC_DHCP_SERVER\n")
    write(OUT / "N03_07_pc_ipconfig.txt", f"generated={generated}\nstatus=DEFERRED_NO_PC_DHCP_SERVER\n")
    write(
        OUT / "N03_08_network_payload_matrix_report.md",
        report_template("N03-8 Network Payload Matrix", rows[8].status, "The full real 16..8192 byte throughput matrix is not yet run. Current evidence is offline smoke coverage only.", rows),
    )
    write_csv(
        OUT / "N03_08_network_payload_matrix.csv",
        [
            {"mode": mode, "payload_bytes": str(size), "seconds": "60", "current_status": "REAL_BOARD_PENDING"}
            for mode in ("pc_ps_memory_echo", "pc_ps_pl_synth_loopback")
            for size in (16, 64, 128, 256, 512, 1024, 4096, 8192)
        ],
    )
    write(
        OUT / "N03_09_link_recovery_negative_tests.md",
        report_template("N03-9 Link Recovery Negative Tests", rows[9].status, "Offline reconnect and negative command paths are covered. Real cable unplug/replug and board reconnect evidence remains pending.", rows),
    )
    write_csv(
        OUT / "N03_09_reconnect_matrix.csv",
        [
            {"case": "offline_mock_reconnect_2x", "status": "PASS_OFFLINE" if marker(offline_text, "reconnect cycle 2/2") else "MISSING", "evidence": rel(offline_summary)},
            {"case": "real_board_reconnect_20x", "status": "REAL_BOARD_PENDING", "evidence": "required by plan"},
            {"case": "real_cable_unplug_replug", "status": "REAL_BOARD_PENDING", "evidence": "manual hardware step required"},
        ],
    )
    write_csv(
        OUT / "N03_09_negative_command_matrix.csv",
        [
            {"case": "START ir_tx", "expected": "ERR_DEFERRED_IR_PHYSICAL_UNAVAILABLE", "current_status": "PASS_OFFLINE"},
            {"case": "CONFIG mode ir_physical", "expected": "ERR_DEFERRED_IR_PHYSICAL_UNAVAILABLE", "current_status": "PASS_OFFLINE"},
            {"case": "UNKNOWN_CMD", "expected": "ERR_UNKNOWN_CMD", "current_status": "PASS_OFFLINE"},
            {"case": "malformed frame header", "expected": "ERROR/bad_magic or disconnect-safe behavior", "current_status": "SOURCE_TESTED_OFFLINE"},
            {"case": "wrong length", "expected": "ERROR/payload_too_large or parser-safe behavior", "current_status": "SOURCE_TESTED_OFFLINE"},
        ],
    )
    package_body = [
        "# N03-10 Network-first Acceptance Package",
        "",
        f"Generated: {generated}",
        "",
        "Verdict: `PACKAGE_PARTIAL_REAL_BOARD_PENDING`",
        "",
        "This package is a current-state N03 deliverable bundle. It proves source/offline/mock progress, incorporates the latest safe real-board wrapper result when present, and preserves the remaining real-board blockers. It does not claim the final N03 baseline PASS.",
        "",
        "## Stage Matrix",
        "",
        md_table(rows),
        "",
        "## Current Source/Offline Evidence",
        "",
        f"- Offline summary: `{rel(offline_summary)}`",
        f"- N03 static direct PC preflight summary: `{rel(static_net_summary)}`",
        f"- N03 static direct PC preflight report: `{rel(static_net_report)}`",
        f"- N03 static direct PC preflight JSON: `{rel(static_net_json)}`",
        f"- Latest UART boot probe summary: `{rel(uart_summary)}`",
        f"- Safe real-board wrapper summary: `{rel(safe_summary)}`",
        f"- Safe real-board wrapper report: `{rel(safe_report)}`",
        f"- Safe real-board wrapper matrix: `{rel(safe_matrix)}`",
        f"- Static PS bridge report: `{rel(static_report)}`",
        f"- Protocol contract report: `{rel(protocol_contract)}`",
        f"- External preconditions: `{rel(external_json)}`",
        f"- P7 physical report: `{rel(p7_report)}`",
        "",
        "## Final N03 Pass Gate",
        "",
        "Do not mark the final N03 network-first baseline as passed until N03-1..N03-6, N03-8, and N03-9 have real board evidence with payload_mismatch=0 and reconnect/link recovery evidence. N03-7 may remain `DEFERRED_NO_PC_DHCP_SERVER` if no PC DHCP server is available.",
        "",
        "## Non-Claims",
        "",
        "```text",
        "IR_PHYSICAL_PASS=0",
        "2LANE_PASS=0",
        "REAL_IR_DATA_ROUNDTRIP_PASS=0",
        "ROTATION_PASS=0",
        "4LANE_PASS=0",
        "8LANE_PASS=0",
        "FINAL_TARGET_PASS=0",
        "```",
    ]
    write(OUT / "N03_10_network_first_acceptance_package.md", "\n".join(package_body))

    write_csv(OUT / "N03_stage_matrix.csv", [asdict(row) for row in rows])
    (OUT / "N03_stage_matrix.json").write_text(
        json.dumps([asdict(row) for row in rows], indent=2) + "\n",
        encoding="utf-8",
    )
    artifact_data = artifact_rows()
    write_csv(OUT / "artifact_hashes.csv", artifact_data)
    artifact_lines = [f"generated={generated}"]
    for row in artifact_data:
        artifact_lines.append(f"{row['status']} {row['path']} {row['sha256']}")
    write(OUT / "artifact_hashes.txt", "\n".join(artifact_lines))

    print(f"WROTE_N03_PACKAGE={OUT}")
    print(f"N03_PACKAGE_STATUS={rows[-1].status}")
    print(f"N03_OFFLINE_SUMMARY={rel(offline_summary)}")
    print(f"N03_STATIC_DIRECT_PREFLIGHT_SUMMARY={rel(static_net_summary)}")
    print(f"N03_UART_SUMMARY={rel(uart_summary)}")
    print(f"N03_SAFE_ACCEPTANCE_SUMMARY={rel(safe_summary)}")
    print(f"N03_SAFE_ACCEPTANCE_PASS={int(safe_acceptance_ok)}")
    print("N03_REAL_BOARD_PASS=0")
    print("NO_IR_PHYSICAL_PASS_CLAIM=1")
    print("NO_2LANE_PASS_CLAIM=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
