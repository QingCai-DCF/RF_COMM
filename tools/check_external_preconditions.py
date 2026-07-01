from __future__ import annotations

import argparse
import csv
import hashlib
import json
import socket
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
EXPECTED_CONSTRAINT_SHA256 = "CFF1A17EE77BBAF90080CF4F97E5920E961AEFAE3B6752F080E35FCF4D4B1F11"


@dataclass
class CheckRow:
    item: str
    status: str
    evidence: str
    note: str


def sha256(path: Path | None) -> str:
    if path is None or not path.exists() or not path.is_file():
        return "MISSING"
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def read_text(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def rel(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def find_constraint() -> Path | None:
    for path in ROOT.glob("*.txt"):
        if sha256(path) == EXPECTED_CONSTRAINT_SHA256:
            return path
    return None


def powershell_json(command: str) -> tuple[list[dict[str, Any]], str]:
    full_command = (
        "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; "
        "$OutputEncoding=[System.Text.Encoding]::UTF8; "
        "$ErrorActionPreference='SilentlyContinue'; "
        + command
        + " | ConvertTo-Json -Compress -Depth 4"
    )
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-Command", full_command],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=20,
    )
    text = proc.stdout.strip()
    if proc.returncode != 0:
        return [], proc.stderr.strip()
    if not text:
        return [], ""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return [], f"json_parse_error={exc}"
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)], ""
    if isinstance(payload, dict):
        return [payload], ""
    return [], "unexpected_json_shape"


def tcp_probe(host: str, port: int, timeout_s: float) -> bool:
    if not host:
        return False
    try:
        with socket.create_connection((host, port), timeout=timeout_s):
            return True
    except OSError:
        return False


def classify_ethernet(adapters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for adapter in adapters:
        name = str(adapter.get("Name", ""))
        desc = str(adapter.get("InterfaceDescription", ""))
        joined = f"{name} {desc}".lower()
        if any(token in joined for token in ["wi-fi", "wifi", "wireless", "wlan", "802.11"]):
            continue
        if any(token in joined for token in ["ethernet", "realtek", "gbe", "2.5gbe", "lan"]):
            out.append(adapter)
    return out


def add(rows: list[CheckRow], item: str, status: str, evidence: str, note: str) -> None:
    rows.append(CheckRow(item, status, evidence, note))


def md_table(rows: list[CheckRow]) -> str:
    lines = [
        "| item | status | evidence | note |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                cell.replace("\n", " ").replace("|", "/")
                for cell in [row.item, row.status, row.evidence, row.note]
            )
            + " |"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only external precondition snapshot for RF_COMM acceptance.")
    parser.add_argument("--target-host", default="192.168.10.2", help="Single-board static fallback IP to probe.")
    parser.add_argument("--target-host-a", default="192.168.10.2", help="AX7010 A static fallback IP to probe.")
    parser.add_argument("--target-host-b", default="192.168.10.3", help="AX7010 B static fallback IP to probe.")
    parser.add_argument("--tcp-port", type=int, default=5001, help="RFCM TCP port.")
    parser.add_argument("--timeout", type=float, default=0.5, help="TCP probe timeout seconds.")
    parser.add_argument("--skip-tcp-probe", action="store_true", help="Do not attempt quick TCP connect probes.")
    parser.add_argument("--require-pc-ip", action="store_true", help="Require the selected PC Ethernet subnet IP.")
    parser.add_argument("--expected-pc-ip", default="192.168.10.1", help="Expected PC-side static IPv4 address.")
    parser.add_argument("--expected-pc-prefix", type=int, default=24, help="Expected PC-side IPv4 prefix length.")
    args = parser.parse_args()

    REPORTS.mkdir(parents=True, exist_ok=True)
    rows: list[CheckRow] = []

    constraint = find_constraint()
    xpr = ROOT / "TFDU_VFIR_Client_Array" / "TFDU_VFIR_Client.xpr"
    wrapper = (
        ROOT
        / "TFDU_VFIR_Client_Array"
        / "TFDU_VFIR_Client.srcs"
        / "sources_1"
        / "imports"
        / "hdl"
        / "design_shiboqi_wrapper.v"
    )
    shutdown_bitstream = ROOT / "shutdown_bitstream" / "tfdu_shutdown_8lane_candidate.bit"
    reduced8_current = read_json(REPORTS / "external_reduced_8lane_frag16_bitstream_current.json")
    reduced8_value = str(reduced8_current.get("bitstream", ""))
    reduced8_bitstream = ROOT / reduced8_value if reduced8_value else None
    if reduced8_bitstream is None or not reduced8_bitstream.exists():
        reduced8_bitstream = REPORTS / "external_reduced_8lane_frag16_bitstream_20260627_065143" / "external_reduced_8lane_frag16_candidate.bit"
    status_consistency = REPORTS / "full_target_status_consistency_current.md"
    real_acceptance_template = REPORTS / "real_acceptance_template" / "real_acceptance_template_manifest.csv"

    adapters, adapter_err = powershell_json(
        "Get-NetAdapter -Physical | Select-Object Name,InterfaceDescription,Status,LinkSpeed,MacAddress,ifIndex"
    )
    ipv4_addresses, ipv4_err = powershell_json(
        "Get-NetIPAddress -AddressFamily IPv4 | Select-Object InterfaceAlias,InterfaceIndex,IPAddress,PrefixLength,AddressState,PrefixOrigin"
    )
    serial_ports, serial_err = powershell_json(
        "Get-CimInstance Win32_PnPEntity | Where-Object { $_.Name -match 'COM[0-9]+' } | Select-Object Name,DeviceID,Status"
    )
    ethernet = classify_ethernet(adapters)
    ethernet_up = [a for a in ethernet if str(a.get("Status", "")).lower() == "up"]
    ethernet_names = {str(a.get("Name", "")) for a in ethernet}
    ethernet_ipv4 = [
        row
        for row in ipv4_addresses
        if str(row.get("InterfaceAlias", "")) in ethernet_names
    ]
    expected_pc_ip_present = any(
        str(row.get("IPAddress", "")) == args.expected_pc_ip
        and int(row.get("PrefixLength", -1)) == args.expected_pc_prefix
        for row in ethernet_ipv4
    )

    xpr_text = read_text(xpr)
    wrapper_text = read_text(wrapper)
    status_consistency_text = read_text(status_consistency)
    reduced8_hash = sha256(reduced8_bitstream)
    shutdown_hash = sha256(shutdown_bitstream)

    add(
        rows,
        "hard_constraint",
        "PASS" if constraint is not None and sha256(constraint) == EXPECTED_CONSTRAINT_SHA256 else "FAIL",
        sha256(constraint),
        "Project hard constraint file must remain unchanged.",
    )
    add(rows, "no_hardware_programming", "PASS", "NO_HARDWARE_PROGRAMMING=1", "This preflight is read-only.")
    add(rows, "no_uart_write", "PASS", "NO_UART_WRITE=1", "Serial devices are enumerated only.")
    add(rows, "no_tfdu_drive", "PASS", "NO_TFDU_DRIVE=1", "No TX_DATA, bitstream programming, or TFDU drive occurs.")
    add(
        rows,
        "windows_network_query",
        "PASS" if not adapter_err else "WARN",
        f"adapters={len(adapters)} ethernet_candidates={len(ethernet)}",
        adapter_err or "Read Windows physical network adapter list.",
    )
    add(
        rows,
        "ethernet_link",
        "PASS" if ethernet_up else "BLOCKED",
        "; ".join(f"{a.get('Name')}:{a.get('Status')}:{a.get('LinkSpeed')}" for a in ethernet) or "no ethernet adapters classified",
        "At least one physical Ethernet link must be Up before real TCP/DHCP acceptance.",
    )
    add(
        rows,
        "n03_static_pc_ip",
        ("PASS" if expected_pc_ip_present else "BLOCKED") if args.require_pc_ip else "SKIPPED",
        (
            f"expected={args.expected_pc_ip}/{args.expected_pc_prefix} "
            f"present={expected_pc_ip_present} "
            f"ethernet_ipv4="
            + (
                "; ".join(
                    f"{row.get('InterfaceAlias')}:{row.get('IPAddress')}/{row.get('PrefixLength')}"
                    for row in ethernet_ipv4
                )
                or "none"
            )
        ),
        ipv4_err
        or "N03 static direct acceptance requires the PC Ethernet adapter to own the expected static IPv4 address.",
    )
    add(
        rows,
        "serial_ports",
        "PASS" if serial_ports else "WARN",
        "; ".join(str(p.get("Name", "")) for p in serial_ports) or serial_err or "none",
        "UART is useful for IP/debug banners, but real TCP can use known static/DHCP IP.",
    )
    add(
        rows,
        "vivado_2023_1_path",
        "PASS" if (Path("D:/Xilinx/Vivado/2023.1/bin/vivado.bat").exists()) else "WARN",
        "D:/Xilinx/Vivado/2023.1/bin/vivado.bat",
        "Vivado 2023.1 batch executable availability.",
    )
    add(
        rows,
        "active_project_safe_state",
        "PASS"
        if 'Path="$PSRCDIR/constrs_1/new/PORT1.xdc"' in xpr_text
        and 'Name="TargetConstrsFile" Val="$PSRCDIR/constrs_1/new/PORT1.xdc"' in xpr_text
        and "[1:0]ir_rx_in_0" in wrapper_text
        and "[1:0]loop_rx_b0" in wrapper_text
        else "FAIL",
        f"{rel(xpr)}; {rel(wrapper)}",
        "Current active project should remain restored to 2-lane/PORT1 unless intentionally changed later.",
    )
    add(
        rows,
        "shutdown_bitstream_available",
        "PASS" if shutdown_hash != "MISSING" else "BLOCKED",
        f"{rel(shutdown_bitstream)} sha256={shutdown_hash}",
        "Required for any future physical TFDU/TX run shutdown step.",
    )
    add(
        rows,
        "reduced_8lane_raw_candidate_available",
        "PASS" if reduced8_hash == "F3661A68DB0F36FCAC96DE983538EA31B5AA2B50338B44A81DAB3E45999AC778" else "BLOCKED",
        f"{rel(reduced8_bitstream)} sha256={reduced8_hash}",
        "Offline raw 32/16 Mbit/s candidate bitstream is available for review, not real acceptance.",
    )
    add(
        rows,
        "real_acceptance_templates_available",
        "PASS" if real_acceptance_template.exists() else "BLOCKED",
        rel(real_acceptance_template),
        "Future real runs should be validated against structured evidence templates.",
    )
    add(
        rows,
        "status_consistency_gate",
        "PASS" if "RF_COMM_FULL_TARGET_STATUS_CONSISTENCY overall=PASS" in status_consistency_text else "BLOCKED",
        rel(status_consistency),
        "Latest status/matrix/audit/hash/project evidence chain should be internally consistent.",
    )

    tcp_results: dict[str, bool | str] = {}
    if args.skip_tcp_probe:
        tcp_results = {"single": "skipped", "a": "skipped", "b": "skipped"}
    else:
        tcp_results = {
            "single": tcp_probe(args.target_host, args.tcp_port, args.timeout),
            "a": tcp_probe(args.target_host_a, args.tcp_port, args.timeout),
            "b": tcp_probe(args.target_host_b, args.tcp_port, args.timeout),
        }
    add(
        rows,
        "tcp_quick_probe_single_board",
        "PASS" if tcp_results["single"] is True else "BLOCKED",
        f"{args.target_host}:{args.tcp_port}={tcp_results['single']}",
        "Real N03 acceptance needs the board PS bridge reachable over TCP.",
    )
    add(
        rows,
        "tcp_quick_probe_two_ax7010",
        "PASS" if tcp_results["a"] is True and tcp_results["b"] is True else "BLOCKED",
        f"{args.target_host_a}:{args.tcp_port}={tcp_results['a']}; {args.target_host_b}:{args.tcp_port}={tcp_results['b']}",
        "Real N04/A01/S05 acceptance needs both AX7010 endpoints reachable.",
    )

    blockers = [row.item for row in rows if row.status == "BLOCKED"]
    fails = [row.item for row in rows if row.status == "FAIL"]
    if fails:
        overall = "FAIL"
    elif blockers:
        overall = "BLOCKED_NO_ETHERNET" if "ethernet_link" in blockers else "BLOCKED_EXTERNAL_PRECONDITIONS"
    else:
        overall = "READY_FOR_SAFE_REAL_ACCEPTANCE_PREFLIGHT"

    generated = datetime.now().isoformat(timespec="seconds")
    md_path = REPORTS / "external_preconditions_current.md"
    json_path = REPORTS / "external_preconditions_current.json"
    csv_path = REPORTS / "external_preconditions_current.csv"

    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))

    md = [
        "# External Preconditions",
        "",
        f"Generated: {generated}",
        "",
        "## Verdict",
        "",
        f"- Overall: `{overall}`",
        f"- Blockers: `{', '.join(blockers) if blockers else 'none'}`",
        "- No hardware programming: `1`",
        "- No UART write: `1`",
        "- No TFDU drive: `1`",
        "",
        "This is a read-only snapshot of external prerequisites for future real hardware acceptance. It does not replace real TCP/DHCP, two-AX7010, product-loop, rotating-shaft, or 8-lane hardware evidence.",
        "",
        "## Checks",
        "",
        md_table(rows),
        "",
        "## Adapter Snapshot",
        "",
        "```json",
        json.dumps({"ethernet": ethernet, "serial_ports": serial_ports}, indent=2, ensure_ascii=False),
        "```",
        "",
        "```text",
        f"RF_COMM_EXTERNAL_PRECONDITIONS overall={overall} blockers={len(blockers)}",
        "NO_HARDWARE_PROGRAMMING=1",
        "NO_UART_WRITE=1",
        "NO_TFDU_DRIVE=1",
        "```",
    ]
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    payload = {
        "generated": generated,
        "overall": overall,
        "blockers": blockers,
        "checks": [asdict(row) for row in rows],
        "adapters": adapters,
        "ethernet": ethernet,
        "serial_ports": serial_ports,
        "ipv4_addresses": ipv4_addresses,
        "tcp_results": tcp_results,
        "n03_expected_pc_ip": {
            "required": args.require_pc_ip,
            "expected_ip": args.expected_pc_ip,
            "expected_prefix": args.expected_pc_prefix,
            "present_on_ethernet": expected_pc_ip_present,
        },
        "artifacts": {
            "constraint": rel(constraint),
            "shutdown_bitstream": rel(shutdown_bitstream),
            "reduced_8lane_bitstream": rel(reduced8_bitstream),
            "status_consistency": rel(status_consistency),
        },
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"WROTE_MARKDOWN={md_path}")
    print(f"WROTE_JSON={json_path}")
    print(f"WROTE_CSV={csv_path}")
    print(f"RF_COMM_EXTERNAL_PRECONDITIONS overall={overall} blockers={len(blockers)}")
    print("NO_HARDWARE_PROGRAMMING=1")
    print("NO_UART_WRITE=1")
    print("NO_TFDU_DRIVE=1")
    return 0 if overall != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
