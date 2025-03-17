#!/usr/bin/env bash

sim_result_path=$1
echo "======================================"
echo " Gem5 Simulation Result Parsing"
echo "  - simulation result path"$sim_result_path

sim_result=`exec ls $sim_result_path`

# echo $sim_result

echo "bench_name simInsts ipc llc_miss MPKI"
for sim_out in $sim_result;
do
    # echo $sim_out
    stat_path="$sim_result_path/$sim_out/"stats.txt""
    simInsts=`grep "simInsts" $stat_path | awk '{print $2}'`
    ipc=`grep "system.cpu.ipc" $stat_path | awk '{print $2}'`
    llcmiss=`grep "system.l3cache.overallMisses::total" $stat_path | awk '{print $2}'`
    mpki=$(awk "BEGIN {print $llcmiss * 1000 / $simInsts}")
    # echo " simInsts : "$simInsts
    # echo " ipc : "$ipc
    # echo " llc cache miss : "$llcmiss
    # echo " MPKI : "$mpki
    echo $sim_out $simInsts $ipc $llcmiss $mpki
done