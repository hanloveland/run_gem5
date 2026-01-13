#!/usr/bin/env python

# Run Gem5 Simulation Script

# Folder Structure 
# - run_sim
# - gem5
# - SPEC_CPU

from os import chdir, getcwd, path, environ, mkdir
import sys
import subprocess
from my_fuc import *
import argparse
from pathlib import Path   

import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import curses

from datetime import datetime

curses_done = False
spec_bench_is_test = False
# set_max_inst = True
# max_inst = int(10e5)
# ouput_dir_name = "/POLY_TEST"
# bench_type = "polybench" # or "spec_cpu"
# gem5_sim_num_core = 4

mix_benchmark_dic = {
    "h1": "429.mcf:470.lbm:syr2k:fdtd-2d",
    "h2": "433.milc:481.wrf:syrk:covariance",
    "h3": "470.lbm:481.wrf:symm:correlation",
    "m1": "410.bwaves:437.leslie3d:lu:gramschmidt",
    "m2": "410.bwaves:458.sjeng:trmm:gemm",
    "m3": "437.leslie3d:458.sjeng:adi:heat-3d",
    "l1": "403.gcc:401.bzip2:doitgen:nussinov",
    "l2": "473.astar:434.zeusmp:seidel-2d:floyd-warshall",
    "l3": "462.libquantum:403.gcc:seidel-2d:doitgen",
    "x1": "470.lbm:410.bwaves:lu:seidel-2d",
    "x2": "429.mcf:437.leslie3d:gemm:floyd-warshall",
    "x3": "481.wrf:458.sjeng:adi:doitgen",
    "t1": "481.wrf:482.sphinx3:483.xalancbmk:998.specrand",
}

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="run_multi_sim.py",
        description="Bulk runner for SPEC CPU / PolyBench / mix with structured outputs.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # 1) Benchmark suite selection
    p.add_argument("--suite", choices=["spec_cpu", "polybench", "mix"], required=True, help="Benchmark suite to run. (Mix is fixed at 4 CPU cores.)",
    )

    # 2) Number of CPUs (gem5 --num-cpus)
    p.add_argument("--num-cpus",type=int,default=1,metavar="N",help="Number of CPUs to simulate in gem5.",
    )

    # 3) Gem5 max simulation instructions
    p.add_argument("--max-inst",type=int,default=0,metavar="N",help="Maximum number of simulated instructions in gem5 (0 = no limit).",
    )

    # 4) Simulation output directory
    p.add_argument("--outdir",type=Path,required=True,help="Simulation output directory (e.g., gem5 m5out path).",
    )

    # 5) Ramulator configuration file path
    p.add_argument("--ramulator-config",type=Path,required=True,help="Path to Ramulator2 configuration file.",
    )

    p.add_argument("--no-curses", action="store_true", help="Disable curses UI."
    )   

    return p

def init_curses():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(0)
    return stdscr

def exit_curses(stdscr):
    if stdscr is None:
        return
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

# def exit_curses():
#     global curses_done
#     if curses_done == False:
#         curses_done = True
#         stdscr.keypad(False)
#         curses.nocbreak()
#         curses.echo()
#         curses.endwin()

def conv_time(elapsed_second):
    elapsed_h = int(int(elapsed_second)/3600)
    elapsed_m = int((int(elapsed_second)%3600)/60)
    elapsed_s = int((int(elapsed_second)%3600)%60)
    elapsed_time = f"{elapsed_h:2d}h {elapsed_m:2d}m {elapsed_s:2d}s"
    return elapsed_time

def create_output_folder(folder_name):
    if not path.exists(folder_name):
        mkdir(folder_name)
        return folder_name 

    i = 1
    new_folder_name = f"{folder_name}_{i}"
    while path.exists(new_folder_name):
        i += 1
        new_folder_name = f"{folder_name}_{i}"
    mkdir(new_folder_name)
    return new_folder_name

def run_worker(bench_type, bench_name, shared_status, key, output_path):
    """
    Records the start time, runs the command, then records the finish time and output.
    """
    # Record start time
    # Done, Start Time, End Time, Result_log
    shared_status[key] = (False,time.time(),time.time(),"working")
    
    BENCH_NAME = bench_name
    NUM_CORES = gem5_sim_num_core
    MAIN_MEMORY_CAPCITY = 128
    OUTPUT_DIR = output_path + "/" + BENCH_NAME
    ORI_PATH = getcwd()
    RAMULATOR_OUTPUT_PATH = OUTPUT_DIR + "/output_ramulator.yaml"    
    # Change Run Path 
    if path.exists(OUTPUT_DIR):
        rmdir(OUTPUT_DIR)        
    mkdir(OUTPUT_DIR)
    run_path = OUTPUT_DIR + "/run"
    mkdir(run_path)
    if bench_type == "spec_cpu" or bench_type == "polybench":
        for i in range(NUM_CORES):
            core_cwd = run_path + "/core_"+str(i) + "_" + BENCH_NAME
            mkdir(core_cwd)
    elif bench_type == "mix":
        mix_bench = mix_benchmark_dic.get(bench_name, "Cannot Find Mix-benchmark list")
        for i, b in enumerate(mix_bench.split(":")):
            core_cwd = run_path + "/core_"+str(i) + "_" + b
            mkdir(core_cwd)

    chdir(run_path)

    # Make Gem5 Running Command
    gem5_command = [GEM5_RUN_PATH]
    # Gem5 Simulation Result Path 
    gem5_command.append("--outdir="+OUTPUT_DIR)
    # Redirect Gem5 Standard output 
    gem5_command.append("--redirect-stdout")
    # Redirect Gem5 Standard error
    gem5_command.append("--redirect-stderr")
    # Skylake configuration Path 
    gem5_command.append(CPU_CONFIG_PATH+"/run-se.py")
    # the number of process 
    gem5_command.append("--str_numcores")
    gem5_command.append(str(NUM_CORES))
    # Ramulator2 Memory Configuration Path 
    gem5_command.append("--ramu_config")
    gem5_command.append(RAMULATOR2_CONFIG_PATH)
    # Ramulator2 Simulaion Result Path 
    gem5_command.append("--ramu_output")    
    gem5_command.append(RAMULATOR_OUTPUT_PATH)    
    # Ramulator2 Memory Capacity
    gem5_command.append("--ramu_cap")    
    gem5_command.append(str(MAIN_MEMORY_CAPCITY))    
    if bench_type == "spec_cpu":
        # Spec CPU Benchmark Path
        gem5_command.append("--spec_path")        
        gem5_command.append(SPEC_PATH)        
        # Spec CPU Benchmark Name
        gem5_command.append("--spec_bench")            
        gem5_command.append(BENCH_NAME)        
        if spec_bench_is_test:
            gem5_command.append( "--spec_bench_test")   
        gem5_command.append("--run_path")
        gem5_command.append(run_path)                 
    elif bench_type == "polybench":
        gem5_command.append("--poly_path")
        gem5_command.append(POLY_PATH)            
        gem5_command.append("--poly_bench") 
        gem5_command.append(BENCH_NAME) 
        gem5_command.append("--run_path")
        gem5_command.append(run_path)          
    elif bench_type == "mix":
        gem5_command.append("--spec_path")
        gem5_command.append(SPEC_PATH)  
        gem5_command.append("--poly_path")
        gem5_command.append(POLY_PATH)                    
        gem5_command.append("--run_path")
        gem5_command.append(run_path)                    
        gem5_command.append("--mix_bench")
        gem5_command.append(mix_bench)
        
    # Set Gem5 Simulation Instruction Number 
    if set_max_inst:
            gem5_command.append("--str_maxinsts")   
            gem5_command.append(str(max_inst))   
    # set Specbenchmark Dataset Size (test or ref)

    # Run the command (blocking call)
    result = subprocess.run(gem5_command,shell=False, capture_output=True, text=True)
    # Record finish time and command output as a tuple
    finish_time = time.time() 
    shared_status[key] = (True, shared_status[key][1], finish_time, result.stdout.strip())

    # Return to Original Path 
    chdir(ORI_PATH)

    return result.stdout.strip()


if __name__ == '__main__':
    args = build_parser().parse_args()
    global set_max_inst
    global max_inst
    global ouput_dir_name
    global bench_type
    global ramulator_config_path

    bench_type = args.suite
    gem5_sim_num_core = args.num_cpus
    ouput_dir_name = str(args.outdir)

    if args.max_inst == 0:
        set_max_inst = False
        max_inst = 0
    else:
        set_max_inst = True
        max_inst = args.max_inst

    ramulator_config_path = str(args.ramulator_config)

    no_use_curses = args.no_curses

    # print(args)
    # exit(1)
    now = datetime.now()
    # Create a shared dictionary using multiprocessing.Manager
    print("=================================================================")
    print("Running Gem5 Simulation with Multi-Process")
    print(" - Date : ", now.date())
    print(" - Time : ", now.time())
    print("=================================================================")
    manager = multiprocessing.Manager()
    status_dict = manager.dict()

    # Settting Gem5 Running Enviroment 
    GEM5_PATH = "../gem5_test/gem5"
    CPU_CONFIG_PATH = path.abspath(GEM5_PATH + "/skylake_config")
    COMMON_CONFIG_PATH = path.abspath(GEM5_PATH + "/configs")
    GEM5_RUN_PATH = path.abspath(GEM5_PATH + "/build/X86/gem5.opt")
    # GEM5_RUN_PATH = path.abspath(GEM5_PATH + "/build/X86/gem5.fast")
    # RAMULATOR2_CONFIG_PATH = path.abspath("ramulator2_config/ddr5_config.yaml")
    # RAMULATOR2_CONFIG_PATH = path.abspath("ramulator2_config/ddr5_pch_config.yaml")
    RAMULATOR2_CONFIG_PATH = path.abspath(ramulator_config_path)    
    BENCH_PATH = path.abspath(GEM5_PATH + "/skylake_config/IntMM")
    SPEC_PATH = path.abspath("../SPEC_CPU2006/benchspec/CPU2006")
    POLY_PATH = path.abspath("../PolyBenchC-4.2.1/build")

    ## Simulation Result Top 
    OUTPUT_DIR = getcwd() + "/" + ouput_dir_name
    OUTPUT_DIR = create_output_folder(OUTPUT_DIR)
    if not no_use_curses:
        OUTPUT_DIR = create_output_folder(OUTPUT_DIR)

    sys.path.append(CPU_CONFIG_PATH)
    sys.path.append(COMMON_CONFIG_PATH)
    sys.path.append(CPU_CONFIG_PATH+"/system")
    environ["GEM5_COMMON_CONFIG_PATH"] = COMMON_CONFIG_PATH
    environ["GEM5_CPU_CONFIG_PATH"] = CPU_CONFIG_PATH

    if (bench_type != "spec_cpu" and bench_type != "polybench" and bench_type != "mix"):
        print(f" Wrong Benchmark Type - {bench_type}")
        exit(1)

    # Not Working "400.perlbench", "416.gamess", "436.cactusADM", "450.soplex" and "459.GemsFDTD"
    if bench_type == "spec_cpu":
        # benchmark_list = ["401.bzip2"]
        benchmark_list = [
           "401.bzip2", "403.gcc", "410.bwaves", 
           "429.mcf", 
           "433.milc", "434.zeusmp", "435.gromacs", "437.leslie3d", 
           "444.namd", "445.gobmk",
           "453.povray","454.calculix", "456.hmmer", "458.sjeng", 
           "462.libquantum","464.h264ref","465.tonto", 
           "470.lbm","471.omnetpp", "473.astar",
           "481.wrf", "482.sphinx3", "483.xalancbmk", 
           "998.specrand", "999.specrand"]

        # benchmark_list = ["401.bzip2", "410.bwaves", "429.mcf", "433.milc", "434.zeusmp","445.gobmk", "464.h264ref","465.tonto", "481.wrf" ]

    elif bench_type == "polybench":
        benchmark_list = ["2mm","3mm","adi","cholesky","correlation","covariance","doitgen","fdtd-2d",
                        "floyd-warshall","gemm","gramschmidt","heat-3d","jacobi-2d","lu","ludcmp","nussinov",
                        "seidel-2d","symm","syr2k","syrk","trmm"]
 
    elif bench_type == "mix":
        benchmark_list = ["h1","h2", "h3", "m1", "m2", "m3", "l1", "l2", "l3", "x1", "x2", "x3"]
        # benchmark_list = ["h1"]
    
    num_benchs = len(benchmark_list)

    num_workers = 4
    start_time = time.time()

    stdscr = None
    if not no_use_curses:
        stdscr = init_curses()    
        stdscr.keypad(True)
        curses.curs_set(0)          

    try: 
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            # Submit tasks with a unique key for each command
            futures = {executor.submit(run_worker, bench_type, cmd, status_dict, i, OUTPUT_DIR): i for i, cmd in enumerate(benchmark_list)}
            
            # Monitor the status of each task while any task is still running
            if not no_use_curses:
                done_cnt = 0
                while any(not f.done() for f in futures):
                    stdscr.clear()
                    sim_elapsed = time.time() - start_time
                    elapsed_time = conv_time(sim_elapsed)
                    done_cnt = 0

                    stdscr.addstr(0, 0, f"Running Gem5 Simulation [{done_cnt}/{num_benchs}].....{elapsed_time} elapsed....")
                    
                    for key in list(status_dict.keys()):
                        value = status_dict[key]
                        # If the value is a float, the task is still running; value represents the start time
                        if value[0] == False:
                            elapsed = time.time() - value[1]
                            elapsed_time = conv_time(elapsed)
                            # print(f"Task {key} running: {elapsed:.2f} sec elapsed")
                            stdscr.addstr(key+1, 2, f"Worker [{key:2d}][{benchmark_list[key]:15s}] [RUNNING]: {elapsed_time} elapsed")
                        else:
                            elapsed = value[2] - value[1]
                            elapsed_time = conv_time(elapsed)
                            stdscr.addstr(key+1, 2, f"Worker [{key:2d}][{benchmark_list[key]:15s}] [DONE   ]: {elapsed_time} elapsed")
                            done_cnt=done_cnt+1
                        # If the task is finished, value is a tuple (finish_time, output)
                    stdscr.refresh()
                    time.sleep(5)  # Adjust polling interval as needed
            else:
                # 각 벤치마크가 끝나는 즉시 future가 완료되므로, 그 순간 1줄만 출력
                for f in as_completed(futures):
                    idx = futures[f]
                    bench_name = benchmark_list[idx]

                    # elapsed time은 status_dict에 end/start가 이미 기록된다는 가정
                    # value: (done_bool, start_time, end_time)
                    try:
                        value = status_dict[idx]
                        if value[0] is True:
                            elapsed = value[2] - value[1]
                            print(f"[DONE] {bench_name}  {conv_time(elapsed)}")
                        else:
                            # 혹시 status_dict 업데이트가 늦는 경우를 대비
                            print(f"[DONE] {bench_name}")
                    except Exception:
                        print(f"[DONE] {bench_name}")

                    # worker 내부 예외가 있으면 여기서 raise되게 해서 실패를 바로 알 수 있음
                    f.result()    
        if not no_use_curses:                                
            exit_curses(stdscr)

    except:
        exit_curses(stdscr)
        print("Error Occurs (curses)")
                                

    elapsed = time.time() - start_time
    elapsed_time = conv_time(elapsed)
    now = datetime.now()
    print("=================================================================")
    print(f"Done Gem5 Simulation - {elapsed_time}")
    print(" - Date : ", now.date())
    print(" - Time : ", now.time())    
    print("=================================================================")
    print("\n\n")
    print(" Parsing Simulation Result")
    result = subprocess.run(["./parse_sim_result.sh",OUTPUT_DIR],shell=False,capture_output=True, text=True)
    parsing_result = result.stdout
    print(parsing_result)    
    # After all tasks are complete, print the results
    original_stdout = sys.stdout
    with open("multi_sim.log","w") as f:
        sys.stdout = f

        print("======================== Gem5 Simulation Result ========================")
        for i, benchname in enumerate(benchmark_list):
            value = status_dict[i]
            elapsed = value[2] - value[1]
            elapsed_time = conv_time(elapsed)
            print(f"[{benchname[:20]}] elapsed time :  {elapsed_time} sec")

        print(" Parsing Simulation Results")
        print(parsing_result)        

        print("=================================================================")

        for future in as_completed(futures):
            key = futures[future]
            value = status_dict[key]
            benchname = benchmark_list[key]
            try:
                output = future.done()                
                print(f"[{benchname[:20]}] is Done ? [{output}]\n")
            except Exception as exc:
                print(f"Task {key} encountered an error: {exc}")
                exit_curses(stdscr) 

    sys.stdout = original_stdout
