RF_COMM software workspace
==========================

This directory contains source-only software added for the PS-to-PC and PS-to-PL
bridge stage of the project.

Current hardware handoff
------------------------

- XSA: `TFDU_VFIR_Client_Array/design_shiboqi_wrapper.xsa`
- Bitstream: `TFDU_VFIR_Client_Array/design_shiboqi_wrapper.bit`
  (`TFDU_VFIR_Client_Array/TFDU_VFIR_Client.runs/impl_1/design_shiboqi_wrapper.bit`
  is still accepted by board scripts when present)
- IR AXI-Lite base: `0x43C00000`
- AXI DMA base: `0x40400000`
- First-stage PL target: one IR lane, 4 Mbit/s raw PHY target

Subdirectories
--------------

- `ps_lwip_bridge`: bare-metal Zynq PS bridge source for Vitis 2023.1.
- `ps_ps_loopback`: standalone UART-only PS-to-PL-to-PS loopback experiment
  that alternates 1-lane and 2-lane masks and prints packet loss plus live
  payload throughput without requiring a PC host connection.
- `host_client`: Python TCP client for PC-side test and bring-up.

Offline PC protocol regression
------------------------------

When the board is not connected, run the host-side protocol tests against a
local mock RFCM server:

```powershell
python -m unittest '.\software\host_client\test_rf_comm_client.py' -v
```

The tests exercise HELLO, STATUS_REQ/STATUS_RSP including extended per-lane
health counters, TX_DATA ACK accounting, CONFIG ACK accounting including
independent TX/RX lane masks, RX_DATA forwarding, TX_DATA ERROR accounting,
fragmented TCP receives, coalesced TCP frames, missing-ACK timeout accounting,
oversize payload rejection, and repeated TCP reconnects.
They do not replace board-level TCP/DHCP or optical-link tests, but they give a
fast regression gate for the PC upper-computer protocol path.

To exercise the same acceptance wrapper without a board, run the local RFCM mock
server flow:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\software\host_client\run_acceptance.ps1 -Mode offline_mock
```

This starts `software/host_client/mock_rfcm_server.py` on an automatically
selected localhost TCP port, runs HELLO, STATUS, CONFIG, TX/RX echo traffic,
CSV log analysis, and TCP reconnect checks, then stops the mock server. It
proves the PC acceptance tooling and protocol framing, but it still does not
replace real PS/lwIP DHCP, DMA, PL, or optical-link tests.

Project gates
-------------

For the current simulation-only phase, run the lighter simulation gate:

```powershell
.\tools\run_simulation_gates.ps1 -Jobs 16
```

It verifies the hard constraint file hash, the full RTL/XSim suite including
the 64 MHz / 4 Mbit/s single-lane and projected 32/16 Mbit/s 8-lane
PHY-rate model, the raw-PHY versus payload-throughput budget model,
retry-exhaustion recovery simulation, continuous four-lane half-duplex stress
simulation, continuous 2+2 lane full-duplex stress simulation, 256-byte
single-lane long-packet latency simulation, 600 rpm / 20 cm rotating-sector
autoroute stress simulation, the 72000-rotation / 288000-sector autoroute
search model, protocol defensive-behavior simulation, and AXI-wrapper lane
counter simulation, plus PS bridge static source checks and the PC-side mock
protocol tests.
It intentionally does not require board access, JTAG, TCP/DHCP hardware runs,
BOOT.BIN freshness, or physical rotating-shaft soak evidence.

After the simulation gate passes, generate the plain-text evidence report with:

```powershell
.\tools\write_simulation_evidence_report.ps1
```

The report is written to `reports/simulation_evidence_report.txt` and records
the constraint-file hashes, each XSim pass signature, PS bridge TCP/DHCP source
check status, and the current simulation-stage PASS/FAIL result.

From the repository root, run the repeatable gate script after RTL, PS, host, or
documentation changes:

```powershell
.\tools\run_project_gates.ps1
```

The default gate verifies the hard constraint file hash, bit/XSA/ELF presence,
BOOT.BIN freshness, post-route timing and utilization reports, Vivado log
errors, the full IR array loopback simulation suite, and the PC-side offline
protocol tests. It leaves Vitis rebuild, BOOT.BIN rebuild, and JTAG probing as
explicit options:

```powershell
.\tools\run_project_gates.ps1 -RunVitisBuild
.\tools\run_project_gates.ps1 -RunBootImageBuild
.\tools\run_project_gates.ps1 -RunHwCheck
```

Use `-SkipLoopbackSim` or `-SkipHostTests` only for quick local checks; the full
software/RTL evidence should use the default gate.

Bring-up sequence
-----------------

For the first board-side PS-PS loopback experiment without the PC host, build
and boot the standalone UART test:

```powershell
& 'D:\Xilinx\Vitis\2023.1\bin\xsct.bat' '.\software\ps_ps_loopback\build_vitis.tcl'
.\software\ps_ps_loopback\build_boot_image.ps1 -Force
```

The directly bootable image is:

```text
software/_boot_ps_ps_loopback/BOOT.BIN
```

The UART output reports `PSPS_STATS` once per second while alternating
`lane_mask=0x1` and `lane_mask=0x3`.

1. Build the PS bridge:

   ```powershell
   & 'D:\Xilinx\Vitis\2023.1\bin\xsct.bat' '.\software\ps_lwip_bridge\build_vitis.tcl'
   ```

2. Program the FPGA and start the PS application:

   ```powershell
   & 'D:\Xilinx\Vitis\2023.1\bin\xsct.bat' '.\software\ps_lwip_bridge\run_on_hw.tcl'
   ```

3. For SD-card boot or untethered soak runs, generate the Zynq boot image:

   ```powershell
   .\tools\build_boot_image.ps1
   ```

   The generated files are:

   ```text
   software/_boot/rf_comm_boot.bif
   software/_boot/BOOT.BIN
   ```

4. Run PC-side TCP smoke checks:

   ```powershell
   python '.\software\host_client\rf_comm_client.py' --host 192.168.10.2 --hello --status --require-clean
   python '.\software\host_client\rf_comm_client.py' --host 192.168.10.2 --config-session 0x1234 --config-lane-mask 0x1 --config-enable 0 --config-mode network_memory_echo --status --require-clean
   python '.\software\host_client\rf_comm_client.py' --host 192.168.10.2 --config-mode pspl_synth_loopback --status --require-clean
   python '.\software\host_client\rf_comm_client.py' --host 192.168.10.2 --repeat 1000 --payload-size 32 --window 1 --ack-timeout 3 --status-interval 1 --require-clean
   python '.\software\host_client\rf_comm_client.py' --host 192.168.10.2 --reconnect-cycles 20
   ```

Use the DHCP address printed on UART instead of `192.168.10.2` when DHCP
succeeds.

The same checks can be run through the acceptance wrapper:

```powershell
.\software\host_client\run_acceptance.ps1 -Mode smoke -TargetHost 192.168.10.2
.\software\host_client\run_acceptance.ps1 -Mode n03_memory_echo -TargetHost 192.168.10.2
.\software\host_client\run_acceptance.ps1 -Mode n03_pspl_synth -TargetHost 192.168.10.2
.\software\host_client\run_acceptance.ps1 -Mode n03_negative -TargetHost 192.168.10.2
.\software\host_client\run_acceptance.ps1 -Mode reconnect -TargetHost 192.168.10.2
```

Use `-DryRun` to print the exact commands without connecting to the board.
Under the active runtime rule, continuous physical operation is capped at
600 seconds. The `soak_2h` acceptance mode therefore keeps its historical name
but sends `--duration 600` to the client and analyzes the CSV with a 600-second
minimum duration. Any manually provided `-DurationSeconds` value above 600 is
also capped to 600. The wrapper still uses `--require-clean` and `--csv-log` so
the ACK/error/status stream is preserved as test evidence. The CSV also records
final `SENT_SUMMARY`, `SUMMARY`, and `ACCEPTANCE_PASS` or `ACCEPTANCE_FAIL`
marker rows.

For traffic modes, the wrapper automatically runs the CSV analyzer after the
host client exits. Use `-SkipLogAnalysis` only when you intentionally want to
defer the second-pass log check.

Analyze a completed CSV log with:

```powershell
python '.\software\host_client\analyze_acceptance_log.py' '.\software\host_client\logs\soak_2h.csv' --require-pass --min-duration 600 --max-errors 0 --min-status-frames 1
```

For final throughput evidence, add `--min-tx-mbps`, `--min-rx-mbps`, or
`--min-rx-frames` to match the mode being tested.
