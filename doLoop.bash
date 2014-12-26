#!/bin/bash 
myid=
target=
output_base=
# 86400 duration one day
duration=
start=
end=

let duration=duration-1
cur=$start
echo "-t $myid " > tmpAll.tmp
while [ $cur -lt $end ]; do
    echo Starting timestamp: $cur
    let next=cur+duration
    cp tmpAll.tmp tmp_$cur.tmp
    echo "-o $output_base$cur.json -e &since=$cur&until=$next $target" >> tmp_$cur.tmp
    python fbdl.py -i tmp_$cur.tmp 0 
    rm tmp_$cur.tmp
    let cur=next+1
    #break  # Put a break here for testing one execution.
done
rm tmpAll.tmp

