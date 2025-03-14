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

GEM5_PATH = "../gem5_test/gem5"
CPU_CONFIG_PATH = path.abspath(GEM5_PATH + "/skylake_config")
COMMON_CONFIG_PATH = path.abspath(GEM5_PATH + "/configs")
GEM5_RUN_PATH = path.abspath(GEM5_PATH + "/build/X86/gem5.opt")
RAMULATOR2_CONFIG_PATH = path.abspath(GEM5_PATH + "/ext/ramulator2/ramulator2/ddr5_config.yaml")
BENCH_PATH = path.abspath(GEM5_PATH + "/skylake_config/IntMM")
SPEC_PATH = path.abspath("../SPEC_CPU2006/benchspec/CPU2006")
# sys.path.append(GEM5_PATH)
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

num_benchs = len(benchmark_list)

BENCH_NAME = "400.perlbench"
OUTPUT_DIR = getcwd() + "/sim_test_out_" + BENCH_NAME
RAMULATOR_OUTPUT_PATH = OUTPUT_DIR + "/output_ramulator.yaml"
max_inst = int(10e6)
# Change Run Path 
run_path = get_spec_bench_path(SPEC_PATH,BENCH_NAME,True)
print("Change Working Path to ",run_path)
chdir(run_path)
# print(getcwd())

# subprocess.run([GEM5_RUN_PATH, CPU_CONFIG_PATH+"/run-se.py","--ramu_config", RAMULATOR2_CONFIG_PATH, "--binary", BENCH_PATH])

subprocess.run([GEM5_RUN_PATH, 
                "--outdir="+OUTPUT_DIR,
                CPU_CONFIG_PATH+"/run-se.py",
                "--ramu_config", RAMULATOR2_CONFIG_PATH, 
                "--ramu_output", RAMULATOR_OUTPUT_PATH,
                "--spec_path", SPEC_PATH,
                "--spec_bench_test",
                "--spec_bench", BENCH_NAME,
                "--str_maxinsts", str(max_inst)])


