#!/bin/bash

MAX_PARALLEL=10
START_ANTS=10
END_ANTS=100
START_FOOD=10
END_FOOD=100

# You can adjust the step if you want fewer total runs
STEP_ANTS=10
STEP_FOOD=10

run_one() {
    local ants=$1
    local food=$2
    echo "Running experiment: ANTS=$ants FOOD=$food"
    venv/bin/python src/colony.py --output_mode=dummy --num_food="$food" --num_ants="$ants"
}

export -f run_one

JOBS=0
for ants in $(seq $START_ANTS $STEP_ANTS $END_ANTS); do
    for food in $(seq $START_FOOD $STEP_FOOD $END_FOOD); do
        bash -c "run_one $ants $food" &
        JOBS=$((JOBS+1))
        if [ "$JOBS" -ge "$MAX_PARALLEL" ]; then
            wait -n  # Wait for any job to finish
            JOBS=$((JOBS-1))
        fi
    done
done

# Wait for all remaining jobs
wait
echo "All scatter experiments complete."