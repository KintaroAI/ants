clean() {
    rm -f frames/*
    rm -f stats-frames/*
    rm -f stats.txt
    rm -f stats.mp4
    rm -f simulation.mp4
    rm -f combined.mp4
    rm -f last_run.env
    rm -f ant_colony_stats.png
}

clean

venv/bin/python src/colony.py --output_mode=files --stats --num_food=20 --num_ants=40 --no_stop_on_divergence
./show_stats.sh --animate --save
./generate_colony_video.sh
./generate_stats_video.sh
./generate_combined_video.sh

# Archive experiment results
source last_run.env
EXP_BASE="experiments/experiment_${NUM_ANTS}_${NUM_FOOD}_${MAX_STEPS}_"
IDX=1
while true; do
    EXP_DIR="${EXP_BASE}$(printf '%06d' $IDX)"
    if [ ! -d "$EXP_DIR" ]; then
        mkdir -p "$EXP_DIR"
        break
    fi
    IDX=$((IDX+1))
done

mv -f last_run.env stats.txt ant_colony_stats.png ./*.mp4 "$EXP_DIR"/
echo "Experiment archived in $EXP_DIR"