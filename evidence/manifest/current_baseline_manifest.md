# P1 2lane ILA Baseline Manifest

Generated: 2026-06-29T15:36:25

This is a read-only manifest for the current P1 lane-mapping baseline. It records hashes and source-shape checks only; it does not program hardware, write UART, or drive TFDU boards.

## Verdict

- Stage: `P1_2LANE_ILA_BASELINE_CURRENT`
- Overall: `PASS_READY_FOR_P1_MATRIX`
- Scope: `CONSTRAINED_2LANE_STATIC_BASELINE_P0_MANIFEST_FOR_P1_MATRIX`
- Hardware action: `none`
- UART action: `none`
- TFDU drive: `none`

## Artifacts

| name | required | exists | path | sha256 | role |
| --- | --- | --- | --- | --- | --- |
| active_bit | 1 | 1 | TFDU_VFIR_Client_Array/TFDU_VFIR_Client.runs/impl_1/design_shiboqi_wrapper.bit | 699E4A89DF01A69A38BF52ACF29A52CD91AEE9FEDF4458FE229354D59E0897FE | active FPGA bitstream for P1 2-lane ILA lane mapping |
| active_ltx | 1 | 1 | TFDU_VFIR_Client_Array/TFDU_VFIR_Client.runs/impl_1/design_shiboqi_wrapper.ltx | 32805D7AE4FDFB411F74E821A6CCF99702C879E825318548224640062F18913C | active ILA probes for P1 2-lane physical matrix |
| active_xsa | 1 | 1 | TFDU_VFIR_Client_Array/design_shiboqi_wrapper.xsa | C8C53B8ADB1B53E4210E6DBBA709DF456B11C0BECE4ECA9DD6028670B42BDD58 | active hardware platform exported from current design |
| active_bit_copy | 1 | 1 | TFDU_VFIR_Client_Array/design_shiboqi_wrapper.bit | 699E4A89DF01A69A38BF52ACF29A52CD91AEE9FEDF4458FE229354D59E0897FE | top-level convenience copy of active bitstream |
| active_boot | 1 | 1 | software/_boot/BOOT.BIN | 87E9BDF6899D65E9859DA8A8EE0A9EDC4F8C3AC5D6994388DD98637351F426F2 | current BOOT.BIN recorded to avoid stage mix-ups |
| ps_loopback_elf | 1 | 1 | software/_vitis_ws_ps_ps_loopback/rf_comm_ps_ps_loopback/Debug/rf_comm_ps_ps_loopback.elf | 4282F3A1C84EF3194111705278C1A6E755735E2F31520881995DB56401D07749 | PS loopback/control ELF used by board-side tests |
| shutdown_bit | 1 | 1 | shutdown_bitstream/tfdu_shutdown_j10_j11.bit | F72680DD3EDA852E64F0B844F54D372368FDB3BDEB775B75507623E6DC167765 | post-test TFDU shutdown bitstream |
| constraint | 1 | 1 | 项目约束(目标）.txt | CFF1A17EE77BBAF90080CF4F97E5920E961AEFAE3B6752F080E35FCF4D4B1F11 | hard project constraint |
| project_xpr | 1 | 1 | TFDU_VFIR_Client_Array/TFDU_VFIR_Client.xpr | ECDDE1B776E4197EDB1528091CCA45A68234ECB0B615FC8BC88CE5504B6C42CA | Vivado project file |
| port_xdc | 1 | 1 | TFDU_VFIR_Client_Array/TFDU_VFIR_Client.srcs/constrs_1/new/PORT1.xdc | 13B233937908A2DF171AE6DD7D97DFC1FA342C01A76434DCB4EC4EDF1BFAD98C | active TFDU port constraints |
| block_design | 1 | 1 | TFDU_VFIR_Client_Array/TFDU_VFIR_Client.srcs/sources_1/bd/design_shiboqi/design_shiboqi.bd | BABEBA9580B65D9AC4B8FFBEDACCBA72A864C6AA3D3CF1B87243F9F80AD6F73B | active block design |
| ila_xci | 1 | 1 | TFDU_VFIR_Client_Array/TFDU_VFIR_Client.srcs/sources_1/bd/design_shiboqi/ip/design_shiboqi_ila_2lane_phy_0/design_shiboqi_ila_2lane_phy_0.xci | 73A276A4E45074C9EC0EB894FAF533395A0206A7F3FEE96185C45407F36DB9B5 | 2-lane physical ILA IP configuration |
| ir_array_xci | 1 | 1 | TFDU_VFIR_Client_Array/TFDU_VFIR_Client.srcs/sources_1/bd/design_shiboqi/ip/design_shiboqi_ir_array_top_axi_0_0/design_shiboqi_ir_array_top_axi_0_0.xci | AD11A4C84235D7C766983D9262B34DD5C3A10F127F503BA585E612CBE636381B | active IR array IP packet/lane configuration |
| ir_loopback_b0_xci | 1 | 1 | TFDU_VFIR_Client_Array/TFDU_VFIR_Client.srcs/sources_1/bd/design_shiboqi/ip/design_shiboqi_ir_loopback_b0_15/design_shiboqi_ir_loopback_b0_15.xci | 2A0BC3EAE9F1332A95211DDE80DCF5D92740530599728B6F5C997A54530514EB | active B-side loopback IP packet/lane configuration |
| ps_makefile | 1 | 1 | software/_vitis_ws_ps_ps_loopback/rf_comm_ps_ps_loopback/Debug/src/subdir.mk | 9A464A5DF4E79ED6903738906A1A1D2633E037A40DC90015F260B0127188AB0F | actual PS loopback ELF compile flags |
| ir_hw_header | 1 | 1 | software/ps_lwip_bridge/src/ir_hw.h | A282AC0129D68FBD35FA84705B60AE6338A41EA3FBCCB3F1F91E368DC00CC388 | shared PS IR hardware packet constants |
| guard_script | 1 | 1 | tools/check_active_artifact_stage.py | 5ECC7E550BDD795F91DAA6593DE3CC481543CD07A80517C7256E6203FB0264D2 | artifact stage guard used before P1 hardware run |
| p1_wrapper | 1 | 1 | tools/run_p1_lane_mapping_matrix_safe.ps1 | D771E408EDD198B67B425D7FBB7C3A6F9147609A5137AB877C945CFB6B19737C | safe P1 lane-mapping wrapper |
| matrix_wrapper | 1 | 1 | tools/run_2lane_matrix_safe.ps1 | B50A833CD470F43A7E94931EC48AEBECBCFA649154F17AF9C221ADC40F44EE22 | safe 2-lane matrix runner |
| prearmed_wrapper | 1 | 1 | tools/run_2lane_hw_prearmed_ila_safe.ps1 | 2764FA075B987BDC4009C6A441B5AFBA2EE8486C0C900626DBAA86588756DE8B | single prearmed ILA capture wrapper |
| add_ila_script | 1 | 1 | tools/add_2lane_phy_ila.tcl | D17B8FFC34CF902FA9517A7208B5A6BDDE2070657CB933B1426E4F2C8FD1F1C2 | script that adds the passive 2-lane physical ILA |
| build_script | 1 | 1 | tools/build_current_bitstream.tcl | 2DB3A1484FF6A96D1624CE8BC0860294C322EED25813ADA6039E8264D6E1B935 | script used for the current bitstream rebuild |
| routed_artifact_script | 1 | 1 | tools/write_active_routed_artifacts.tcl | D3F525C4D815D817C7D4E7368B10497780CCD66954C32590350915096B449CF3 | read-only routed-artifact extraction helper |
| shutdown_script | 1 | 1 | tools/program_tfdu_shutdown.tcl | 3C82016D7D37B7A7605E9CDA7CC14FB8332897BCDF475BC5882F98F74C81D444 | shutdown programming Tcl script |

## Source Checks

| name | status | detail |
| --- | --- | --- |
| required_artifacts_exist | PASS | missing= |
| hard_constraint_hash | PASS | constraint_sha256=CFF1A17EE77BBAF90080CF4F97E5920E961AEFAE3B6752F080E35FCF4D4B1F11 |
| active_bit_copy_matches | PASS | active_bit=699E4A89DF01A69A38BF52ACF29A52CD91AEE9FEDF4458FE229354D59E0897FE active_bit_copy=699E4A89DF01A69A38BF52ACF29A52CD91AEE9FEDF4458FE229354D59E0897FE |
| project_uses_port1_xdc | PASS | Vivado project references PORT1.xdc |
| port1_expected_pinmap | PASS | all expected TFDU pins match |
| port1_no_duplicate_package_pins | PASS | duplicates= |
| b_rx1_moved_to_g15 | PASS | loop_rx_b0[1]=G15 |
| bd_uses_ir_stream_bidir_vec_bd | PASS | BD contains ir_stream_bidir_vec_bd |
| bd_lane_count_2 | PASS | BD contains LANE_COUNT value 2 |
| bd_contains_ila_2lane_phy | PASS | BD contains passive 2-lane physical ILA |
| ila_xci_probe_count_9 | PASS | C_NUM_OF_PROBES=9 |
| ila_xci_depth_16384 | PASS | C_DATA_DEPTH=16384 |
| ila_xci_probe8_width_32 | PASS | C_PROBE8_WIDTH=32 |
| ltx_contains_2lane_phy_ila | PASS | LTX contains design_shiboqi_i/ila_2lane_phy with probes 0..8 |
| pl_2lane_packet_config | PASS | LANE_COUNT=2 MAX_PACKET_BYTES=255 FRAGMENT_BYTES=255 allowed_max_packet=255_or_264 |
| loopback_b0_packet_config_matches | PASS | LANE_COUNT=2 RAW_PACKET_BYTES=255 FRAGMENT_BYTES=255 |
| ps_compile_packet_defines_present | PASS | PSPS_PAYLOAD_BYTES=247 IR_HW_MAX_PACKET_BYTES=255 IR_HW_RX_TRANSFER_BYTES=255 IR_HW_APP_HEADER_BYTES=8 |
| ps_raw_payload_fits_pl_packet | PASS | raw_payload=PSPS_PAYLOAD_BYTES+IR_HW_APP_HEADER_BYTES=255 PL_MAX_PACKET_BYTES=255 |
| ps_packet_buffers_fit_pl_packet | PASS | IR_HW_MAX_PACKET_BYTES=255 IR_HW_RX_TRANSFER_BYTES=255 PL_MAX_PACKET_BYTES=255 |

```text
RF_COMM_P1_2LANE_ILA_BASELINE stage=P1_2LANE_ILA_BASELINE_CURRENT overall=PASS_READY_FOR_P1_MATRIX
NO_HARDWARE_PROGRAMMING=1
NO_UART_WRITE=1
NO_TFDU_DRIVE=1
ROOT_CONSTRAINT_SHA256=CFF1A17EE77BBAF90080CF4F97E5920E961AEFAE3B6752F080E35FCF4D4B1F11
```
