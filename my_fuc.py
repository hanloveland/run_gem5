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

poly_datamining_list = [ "correlation", "covariance" ]
poly_kernel_list = [ "2mm", "3mm", "atax", "bicg", "doitgen", "mvt"]
poly_blas_list = [ "gemm", "gemver", "gesummv", "symm", "syr2k", "syrk", "trmm"]
poly_solver_list = [ "durbin", "lu", "ludcmp", "trisolv", "cholesky", "gramschmidt" ]
poly_medley_list = [ "deriche", "floyd-warshall", "nussinov" ]
poly_stencil_list = [ "adi", "fdtd-2d", "heat-3d", "jacobi-1d", "jacobi-2d", "seidel-2d" ]

mibench_automotive_list = ["basicmath", "bitcount", "qsort", "susan"] 
mibench_security_list = ["blowfish", "rijndael", "sha"]
mibench_network_list = ["dijkstra","patricia"]
mibench_telecomm_list = ["CRC32","FFT","gsm"] 

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

def get_poly_bench_path(_poly_path,_bench):
    if _bench in poly_datamining_list:
        run_path = _poly_path + "/" + "datamining/" + _bench
    elif _bench in poly_kernel_list:
        run_path = _poly_path + "/" + "linear-algebra/kernels/" + _bench
    elif _bench in poly_blas_list:
        run_path = _poly_path + "/" + "linear-algebra/blas/" + _bench       
    elif _bench in poly_solver_list:
        run_path = _poly_path + "/" + "linear-algebra/solvers/" + _bench             
    elif _bench in poly_medley_list:
        run_path = _poly_path + "/" + "medley/" + _bench      
    elif _bench in poly_stencil_list:
        run_path = _poly_path + "/" + "stencils/" + _bench           
    else: 
        print("Wrong PolyBench!!")
        exit(1)
    return run_path
    
def get_mibench_path(_mibench_path,_bench):
    if _bench in mibench_automotive_list:
        run_path = _mibench_path + "/" + "automotive/" + _bench    
    elif _bench in mibench_security_list:
        run_path = _mibench_path + "/" + "security/" + _bench  
    elif _bench in mibench_network_list:
        run_path = _mibench_path + "/" + "network/" + _bench  
    elif _bench in mibench_telecomm_list:
        run_path = _mibench_path + "/" + "telecomm/" + _bench       
    elif _bench == "adpcm":
        run_path = _mibench_path + "/" + "telecomm/" + _bench + "/bin"
    else: 
        print(f"{_bench} is not Mibench!!")
        exit(1)
    return run_path