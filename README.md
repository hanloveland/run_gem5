# ===== Gem5 Run Script =====

Gem5 Simulation Enviorment Structure 

- Gem5 
- SPEC_CPU2006
- run_gem5  

##  SPEC CPU 2006 List

✅: Done, 🔨: Running, ⭕: Simulation Done but Need Check output ❌: Does Not Working 🚧: Exit during Running (timing..)
| Benchmark Name | Ref/Test | Simulation Inst. | Host Runtime(s) | IPC | L3 Cache Miss | Status |
|:-------:|:-------:|:-------|:-------:|:-------:|:-------:|:-------:|
| 400.perlbench | Test | 12038151 | 69.70 |  0.925781 | 23363 | ✅ | 
| 401.bzip2 | Test | 2274644798 | ? | 1.138596 | 1494035 | ❓ | 
| 403.gcc | Test | 8974723 | ? | 1.147972 | 24820 | ❓ |
| 410.bwaves | Test | 17732999747 | ? | 0.730162 | 397274740 | ❓ |
| 416.gamess | - | - | - | - | - | ❌ |
| 429.mcf | Test | 3160666731 | 23497.83 | 0.317292 | 139157905 | ✅ |
| 433.milc | Test | 30023126400 | - | 0.902677 | 349318351 | 🚧|
| 434.zeusmp | Test | 32947891935 | - |  0.820609 | 208218936 | 🚧 |
| 435.gromacs | Test | 4436351728 | 14937.22 | 0.899755 | 1400538 | ❓ |
| 436.cactusADM | - | - | - | - | - | ❌ |
| 437.leslie3d | Test | 24495896204 | - | 0.632660 | 260666346 | 🚧 |
| 444.namd | Test | 35656679848 | - | 1.299682 | 3581408 | 🚧 |
| 445.gobmk | Test | ? | ? | ? | ? | ❓ |
| 447.dealII | - | - | - | - | - | 🔨 |
| 450.soplex | Test | 22506749 | 112.53 | 0.953352 | 28498 | ⭕ |
| 453.povray | Test | 9550670 | 43.61 | 0.900061 | 25509 | ⭕ |
| 454.calculix | Test | 263282 | 612.66 | 1.180130 | 54968 | ✅ |
| 456.hmmer | Test | 14571356316 | 58525.27 | 2.061590 | 14542 | ✅ |
| 458.sjeng | Test | 10924119037 | 54274.66 | 0.777200 | 18496706 | ✅ |
| 459.GemsFDTD | - | - | - | - | - | ❌ |
| 462.libquantum | Test | 226386985 | 528.95 | 2.485585 | 6210 | ✅ |
| 464.h264ref | Test | 641408 | 4.78 | 0.539089 | 5310 | ❓ |
| 465.tonto | Test | 1580038 | 9.09 | 0.626211 | 12674 | ❓ |
| 470.lbm | Test | ? | ? | ? | ? | ❓ |
| 471.omnetpp | Test | 1617553407 | ?7752.86| 1.207573 | 135244 | ✅ |
| 473.astar | Test | 13345055303 | - | 0.891398 | 234699 | 🚧 |
| 481.wrf | Test | 8825102007 | - | 0.361304 | 87326190 | 🚧 |
| 482.sphinx3 | Test | 5349867 | 15.70 | 1.138603 | 6564 | ❓ |
| 483.xalancbmk | Test | 3634642 | 17.58 | 0.739478 | 27403 | ❓ |
| 998.specrand | Test | 62363414 | 245.56 | 1.336844 | 3632 | ✅ |
| 999.specrand | Test | 62363414 | 253.39 | 1.336844 | 3632 | ✅ |

※ IPC: system.cpu.ipc
※ L3 Cache Miss: system.l3cache.overallMisses::total
MPKI: Miss Per Kilo-Instruciotn 
