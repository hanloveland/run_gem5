#!/usr/bin/env python

# Run Gem5 Simulation Script

# Folder Structure 
# - run_sim
# - gem5
# - SPEC_CPU

from os import chdir, getcwd, path, environ
import sys
import subprocess
from my_fuc import *

# SPEC_CPU, POLYBENCH_SINGLE, POLYBENCH_SINGLE_ALL, MIBENCH 
BENCH_TYPE="POLYBENCH_SINGLE"

GEM5_PATH = "../gem5_test/gem5"
CPU_CONFIG_PATH = path.abspath(GEM5_PATH + "/skylake_config")
COMMON_CONFIG_PATH = path.abspath(GEM5_PATH + "/configs")
GEM5_RUN_PATH = path.abspath(GEM5_PATH + "/build/X86/gem5.opt")
# RAMULATOR2_CONFIG_PATH = path.abspath(GEM5_PATH + "/ext/ramulator2/ramulator2/ddr5_config.yaml")
RAMULATOR2_CONFIG_PATH = path.abspath("./ramulator2_config/ddr5_config.yaml")
# RAMULATOR2_CONFIG_PATH = path.abspath("./ramulator2_config/ddr5_pch_config.yaml")
# BENCH_PATH = path.abspath(GEM5_PATH + "/skylake_config/IntMM")
BENCH_PATH = "/home/mklee/share/PolyBench/PolyBenchC-4.2.1/build/2mm"
SPEC_PATH = path.abspath("../SPEC_CPU2006/benchspec/CPU2006")
POLY_PATH = path.abspath("../PolyBench/PolyBenchC-4.2.1/build")
MIBENCH_PATH = path.abspath("../mibench")
MAIN_PATH = getcwd()
# Unit is GB
MAIN_MEMORY_CAPCITY=128
sys.path.append(CPU_CONFIG_PATH)
sys.path.append(COMMON_CONFIG_PATH)
sys.path.append(CPU_CONFIG_PATH+"/system")
environ["GEM5_COMMON_CONFIG_PATH"] = COMMON_CONFIG_PATH
environ["GEM5_CPU_CONFIG_PATH"] = CPU_CONFIG_PATH

benchmark_list = [
    "400.perlbench", "401.bzip2", "403.gcc", "410.bwaves", "416.gamess", "429.mcf", "433.milc",
    "434.zeusmp", "435.gromacs", "436.cactusADM", "437.leslie3d", "444.namd", "445.gobmk",
    "450.soplex", "453.povray","454.calculix", "456.hmmer", "458.sjeng", "459.GemsFDTD",
    "462.libquantum","464.h264ref","465.tonto", "470.lbm","471.omnetpp", "473.astar",
    "481.wrf", "482.sphinx3", "483.xalancbmk", "998.specrand", "999.specrand"]
# 2mm, 3mm, adi, cholesky, correlation, covariance, doitgen, fdtd-2d, floyd-warshall, gemm, gramschmidt, heat-3d, jacobi-2d, lu, ludcmp, nussinov, seidel-2d, symm, syr2k, syrk, trmm

polybench_list = [
    "2mm","3mm","adi","cholesky","correlation","covariance","doitgen","fdtd-2d",
    "floyd-warshall","gemm","gramschmidt","heat-3d","jacobi-2d","lu","ludcmp","nussinov",
    "seidel-2d","symm","syr2k","syrk","trmm"]


# polybench_list = [
#     "covariance", "2mm", "3mm", "atax", "bicg", "doitgen", "mvt", "gemm",
#     "gemver", "gesummv", "symm", "syr2k", "syrk", "trmm", "durbin", "lu",
#     "ludcmp", "trisolv", "deriche",  "floyd-warshall", "nussinov", "adi",
#     "fdtd-2d", "heat-3d", "jacobi-1d", "jacobi-2d", "seidel-2d", "cholesky",
#     "gramschmidt", "correlation"]

# mibench_list = ["gsm"]

# We Not Use Mibench 
mibench_list = [
    "basicmath", "bitcount", "qsort", "susan", "blowfish", "rijndael", "sha",
    "dijkstra", "patricia", "CRC32", "FFT", "gsm"]

BENCH_NAME = "429.mcf"
# POLY_NAME = "covariance"
# OUTPUT_FOLDER="/polybench"
# OUTPUT_FOLDER="/simout_baseline_4core_8800_8800_0"
# OUTPUT_DIR = getcwd() + OUTPUT_FOLDER + "/sim_test_out_" + BENCH_NAME
# RAMULATOR_OUTPUT_PATH = OUTPUT_DIR + "/output_ramulator.yaml"

# Common Option
GEM5_NUM_CORE=1
max_inst = int(10e8)

if BENCH_TYPE == "SPEC_CPU":
    # Run A binary 
    # Run Single Polybench
    OUTPUT_FOLDER="/spec_cpu"
    SPEC_NAME="401.bzip2"
    for spec_bench in benchmark_list:
        OUTPUT_DIR = MAIN_PATH + OUTPUT_FOLDER + "/sim_out_" + spec_bench
        RAMULATOR_OUTPUT_PATH = OUTPUT_DIR + "/output_ramulator.yaml"
        run_path = get_spec_bench_path(SPEC_PATH,spec_bench,False)
        print("Change Working Path to ",run_path)
        chdir(run_path)

        subprocess.run([GEM5_RUN_PATH, 
                        "--outdir="+OUTPUT_DIR,
                        CPU_CONFIG_PATH+"/run-se.py",
                        "--str_numcores", str(GEM5_NUM_CORE),
                        "--ramu_config", RAMULATOR2_CONFIG_PATH, 
                        "--ramu_output", RAMULATOR_OUTPUT_PATH,
                        "--spec_bench", spec_bench,
                        "--spec_path", SPEC_PATH, 
                        "--ramu_cap",str(MAIN_MEMORY_CAPCITY),
                        "--str_maxinsts", str(max_inst)])
elif BENCH_TYPE == "POLYBENCH_SINGLE":
    # Run A binary 
    # Run Single Polybench
    OUTPUT_FOLDER="/polybench"
    POLY_NAME="covariance"
    for polybench in polybench_list:
        OUTPUT_DIR = MAIN_PATH + OUTPUT_FOLDER + "/sim_out_" + POLY_NAME
        RAMULATOR_OUTPUT_PATH = OUTPUT_DIR + "/output_ramulator.yaml"
        run_path = get_poly_bench_path(POLY_PATH,POLY_NAME)
        print("Change Working Path to ",run_path)
        chdir(run_path)

        subprocess.run([GEM5_RUN_PATH, 
                        "--outdir="+OUTPUT_DIR,
                        CPU_CONFIG_PATH+"/run-se.py",
                        "--str_numcores", str(GEM5_NUM_CORE),
                        "--ramu_config", RAMULATOR2_CONFIG_PATH, 
                        "--ramu_output", RAMULATOR_OUTPUT_PATH,
                        "--poly_bench", polybench,
                        "--ramu_cap",str(MAIN_MEMORY_CAPCITY),
                        "--str_maxinsts", str(max_inst)])
elif BENCH_TYPE == "POLYBENCH_SINGLE_ALL":
    # Run All Polybench
    OUTPUT_FOLDER="/polybench"
    for polybench in polybench_list:
        OUTPUT_DIR = MAIN_PATH + OUTPUT_FOLDER + "/sim_out_" + polybench
        RAMULATOR_OUTPUT_PATH = OUTPUT_DIR + "/output_ramulator.yaml"
        run_path = get_poly_bench_path(POLY_PATH,polybench)
        print("Change Working Path to ",run_path)
        chdir(run_path)

        subprocess.run([GEM5_RUN_PATH, 
                        "--outdir="+OUTPUT_DIR,
                        CPU_CONFIG_PATH+"/run-se.py",
                        "--str_numcores", str(GEM5_NUM_CORE),
                        "--ramu_config", RAMULATOR2_CONFIG_PATH, 
                        "--ramu_output", RAMULATOR_OUTPUT_PATH,
                        "--poly_bench", polybench,
                        "--ramu_cap",str(MAIN_MEMORY_CAPCITY),
                        "--str_maxinsts", str(max_inst)])
elif BENCH_TYPE == "MIBENCH":
    # Mibench
    OUTPUT_FOLDER="/mibench"
    for mibench in mibench_list:
        OUTPUT_DIR = MAIN_PATH + OUTPUT_FOLDER + "/" + mibench
        RAMULATOR_OUTPUT_PATH = OUTPUT_DIR + "/output_ramulator.yaml"
        run_path = get_mibench_path(MIBENCH_PATH,mibench)
        print("Change Working Path to ",run_path)
        chdir(run_path)

        subprocess.run([GEM5_RUN_PATH, 
                        "--outdir="+OUTPUT_DIR,
                        CPU_CONFIG_PATH+"/run-se.py",
                        "--str_numcores", str(GEM5_NUM_CORE),
                        "--ramu_config", RAMULATOR2_CONFIG_PATH, 
                        "--ramu_output", RAMULATOR_OUTPUT_PATH,
                        "--mibench", mibench,
                        "--ramu_cap",str(MAIN_MEMORY_CAPCITY),
                        "--str_maxinsts", str(max_inst)])
