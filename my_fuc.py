benchmark_list = [
    "400.perlbench",
    "401.bzip2",
    "403.gcc",
    "410.bwaves",
    "416.gamess",
    "429.mcf",
    "433.milc",
    "434.zeusmp",
    "435.gromacs",
    "436.cactusADM",
    "437.leslie3d",
    "444.namd",
    "445.gobmk",
    "450.soplex",
    "453.povray",
    "454.calculix",
    "456.hmmer",
    "458.sjeng",
    "459.GemsFDTD",
    "462.libquantum",
    "464.h264ref",
    "465.tonto",
    "470.lbm",
    "471.omnetpp",
    "473.astar",
    "481.wrf",
    "482.sphinx3",
    "483.xalancbmk",
    "998.specrand",
    "999.specrand",
]

def get_spec_bench_path(_spec_path,_bench,_is_test):
    if _bench in benchmark_list:
        if _is_test:
            run_path = _spec_path + "/" + _bench + "/run/run_base_test_none.0000/"            
        else: 
            run_path = _spec_path + "/" + _bench + "/run/run_base_ref_none.0000/"            
        return run_path    
    else: 
        print("Wrong SPEC CPU Benchmark!")
        exit(1)
