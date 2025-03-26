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

import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import curses

from datetime import datetime

curses_done = False
set_max_inst = True
max_inst = int(10e9)
ouput_dir_name = "/SimResult_ProposedDDR5"
spec_bench_is_test = False

def exit_curses():
    global curses_done
    if curses_done == False:
        curses_done = True
        stdscr.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

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

def run_worker(bench_name, shared_status, key, output_path):
    """
    Records the start time, runs the command, then records the finish time and output.
    """
    # Record start time
    # Done, Start Time, End Time, Result_log
    shared_status[key] = (False,time.time(),time.time(),"working")
    
    BENCH_NAME = bench_name
    MAIN_MEMORY_CAPCITY = 64
    OUTPUT_DIR = output_path + "/" + BENCH_NAME
    ORI_PATH = getcwd()
    RAMULATOR_OUTPUT_PATH = OUTPUT_DIR + "/output_ramulator.yaml"    
    # Change Run Path 
    run_path = get_spec_bench_path(SPEC_PATH,BENCH_NAME,spec_bench_is_test)
    if spec_bench_is_test == True:
        spec_bench_test = "--spec_bench_test"
    else:
        spec_bench_test = ""
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
    # Ramulator2 Memory Configuration Path 
    gem5_command.append("--ramu_config")
    gem5_command.append(RAMULATOR2_CONFIG_PATH)
    # Ramulator2 Simulaion Result Path 
    gem5_command.append("--ramu_output")    
    gem5_command.append(RAMULATOR_OUTPUT_PATH)    
    # Ramulator2 Memory Capacity
    gem5_command.append("--ramu_cap")    
    gem5_command.append(str(MAIN_MEMORY_CAPCITY))    
    # Spec CPU Benchmark Path
    gem5_command.append("--spec_path")        
    gem5_command.append(SPEC_PATH)        
    # Spec CPU Benchmark Name
    gem5_command.append("--spec_bench")            
    gem5_command.append(BENCH_NAME)        
    # Set Gem5 Simulation Instruction Number 
    if set_max_inst:
            gem5_command.append("--str_maxinsts")   
            gem5_command.append(str(max_inst))   
    # set Specbenchmark Dataset Size (test or ref)
    if spec_bench_is_test:
            gem5_command.append( "--spec_bench_test")   

    # Run the command (blocking call)
    result = subprocess.run(gem5_command,shell=False, capture_output=True, text=True)
    # result = subprocess.run([GEM5_RUN_PATH, 
    #                    "--outdir="+OUTPUT_DIR,
    #                    "--redirect-stdout",
    #                    "--redirect-stderr",
    #                    CPU_CONFIG_PATH+"/run-se.py",
    #                    "--ramu_config", RAMULATOR2_CONFIG_PATH, 
    #                    "--ramu_output", RAMULATOR_OUTPUT_PATH,
    #                    "--spec_path", SPEC_PATH,
    #                    "--spec_bench", BENCH_NAME,
    #                    "--ramu_cap",str(MAIN_MEMORY_CAPCITY)
    #                    ],shell=False, capture_output=True, text=True)
    # Record finish time and command output as a tuple
    finish_time = time.time() 
    shared_status[key] = (True, shared_status[key][1], finish_time, result.stdout.strip())

    # Return to Original Path 
    chdir(ORI_PATH)

    return result.stdout.strip()


if __name__ == '__main__':
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
    RAMULATOR2_CONFIG_PATH = path.abspath("ramulator2_config/ddr5_pch_config.yaml")
    BENCH_PATH = path.abspath(GEM5_PATH + "/skylake_config/IntMM")
    SPEC_PATH = path.abspath("../SPEC_CPU2006/benchspec/CPU2006")

    ## Simulation Result Top 
    OUTPUT_DIR = getcwd() + ouput_dir_name
    OUTPUT_DIR = create_output_folder(OUTPUT_DIR)

    sys.path.append(CPU_CONFIG_PATH)
    sys.path.append(COMMON_CONFIG_PATH)
    sys.path.append(CPU_CONFIG_PATH+"/system")
    environ["GEM5_COMMON_CONFIG_PATH"] = COMMON_CONFIG_PATH
    environ["GEM5_CPU_CONFIG_PATH"] = CPU_CONFIG_PATH

    # Not Working "400.perlbench", "416.gamess", "436.cactusADM", "450.soplex" and "459.GemsFDTD"
    benchmark_list = [
        "401.bzip2", "403.gcc", "410.bwaves", 
        "429.mcf", 
        "433.milc", "434.zeusmp", "435.gromacs", "437.leslie3d", 
        "444.namd", "445.gobmk", "447.dealII",
        "453.povray","454.calculix", "456.hmmer", "458.sjeng", 
        "462.libquantum","464.h264ref","465.tonto", 
        "470.lbm","471.omnetpp", "473.astar",
        "481.wrf", "482.sphinx3", "483.xalancbmk", 
        "998.specrand", "999.specrand"]

    # benchmark_list = ["400.perlbench"]
    num_benchs = len(benchmark_list)

    num_workers = 8
    start_time = time.time()
    stdscr = curses.initscr() 
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(0)  
    try: 
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            # Submit tasks with a unique key for each command
            futures = {executor.submit(run_worker, cmd, status_dict, i, OUTPUT_DIR): i for i, cmd in enumerate(benchmark_list)}
            
            # Monitor the status of each task while any task is still running
            done_cnt = 0
            while any(not f.done() for f in futures):
                stdscr.clear()
                sim_elapsed = time.time() - start_time
                elapsed_time = conv_time(sim_elapsed)
                stdscr.addstr(0, 0, f"Running Gem5 Simulation [{done_cnt}/{num_benchs}].....{elapsed_time} elapsed....")
                done_cnt = 0
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
                time.sleep(1)  # Adjust polling interval as needed
        exit_curses()
    except:
        exit_curses()
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
                exit_curses()  

    sys.stdout = original_stdout
