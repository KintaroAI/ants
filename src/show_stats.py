#!/usr/bin/env python3
"""
Show statistics visualization for ant colony simulation.
Reads stats.txt and creates graphs showing food preferences over time.
"""

import argparse
import os
import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Visualize ant colony statistics")
    parser.add_argument('--stats_file', default='stats.txt', 
                       help='Path to stats.txt file (default: stats.txt)')
    parser.add_argument('--output', default=None,
                       help='Output file for the plot (default: show plot)')
    parser.add_argument('--title', default='Ant Colony Food Preferences Over Time',
                       help='Plot title')
    parser.add_argument('--save', action='store_true',
                       help='Force save to file instead of displaying')
    parser.add_argument('--animate', action='store_true',
                       help='Create an animation by saving or showing each frame of the stats plot')
    return parser.parse_args()

def load_stats_data(stats_file):
    """Load statistics data from file."""
    if not os.path.exists(stats_file):
        print(f"Error: Stats file '{stats_file}' not found.")
        print("Run the simulation with --stats flag first:")
        print("  python src/colony.py --stats")
        sys.exit(1)
    
    steps = []
    colony_0_prefs = []
    colony_1_prefs = []
    
    with open(stats_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
                
            try:
                parts = line.split(',')
                if len(parts) != 3:
                    print(f"Warning: Skipping malformed line {line_num}: {line}")
                    continue
                    
                step = int(parts[0])
                pref_0 = float(parts[1])
                pref_1 = float(parts[2])
                
                steps.append(step)
                colony_0_prefs.append(pref_0)
                colony_1_prefs.append(pref_1)
                
            except (ValueError, IndexError) as e:
                print(f"Warning: Skipping malformed line {line_num}: {line}")
                continue
    
    if not steps:
        print("Error: No valid data found in stats file.")
        sys.exit(1)
    
    return np.array(steps), np.array(colony_0_prefs), np.array(colony_1_prefs)

def create_preference_plot(steps, colony_0_prefs, colony_1_prefs, title, xlim=None, ylim=None):
    plt.figure(figsize=(12, 8))
    
    # Plot food preferences over time
    plt.subplot(2, 1, 1)
    plt.plot(steps, colony_0_prefs, 'r-', linewidth=2, label='Colony 0 (Red)', alpha=0.8)
    plt.plot(steps, colony_1_prefs, 'k-', linewidth=2, label='Colony 1 (Black)', alpha=0.8)
    plt.axhline(y=0.0, color='green', linestyle='--', alpha=0.3, label='Green food preference')
    plt.axhline(y=1.0, color='orange', linestyle='--', alpha=0.3, label='Orange food preference')
    plt.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5, label='Neutral preference')
    plt.xlabel('Simulation Step')
    plt.ylabel('Food Preference')
    plt.title(f'{title} - Food Preferences')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(-0.05, 1.05) if ylim is None else plt.ylim(*ylim)
    if xlim is not None:
        plt.xlim(*xlim)
    
    # Plot preference difference
    plt.subplot(2, 1, 2)
    preference_diff = colony_0_prefs - colony_1_prefs
    plt.plot(steps, preference_diff, 'purple', linewidth=2, alpha=0.8)
    plt.axhline(y=0, color='gray', linestyle=':', alpha=0.5)
    plt.axhline(y=0.9, color='red', linestyle='--', alpha=0.5, label='Divergence threshold')
    plt.axhline(y=-0.9, color='red', linestyle='--', alpha=0.5)
    plt.xlabel('Simulation Step')
    plt.ylabel('Preference Difference (Colony 0 - Colony 1)')
    plt.title('Preference Divergence')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(-1.1, 1.1) if ylim is None else plt.ylim(*ylim)
    if xlim is not None:
        plt.xlim(*xlim)
    plt.tight_layout()
    return plt

def main():
    args = parse_arguments()

    # If output or save is set, use Agg backend
    if args.output or args.save:
        matplotlib.use('Agg')

    steps, colony_0_prefs, colony_1_prefs = load_stats_data(args.stats_file)
    print(f"Loaded {len(steps)} data points")
    print(f"Simulation ran for {steps[-1]} steps")
    print(f"Final preferences - Colony 0: {colony_0_prefs[-1]:.4f}, Colony 1: {colony_1_prefs[-1]:.4f}")

    if args.animate:
        max_step = steps[-1]
        xlim = (0, max_step)
        ylim_prefs = (-0.05, 1.05)
        ylim_diff = (-1.1, 1.1)

        if args.save:
            os.makedirs('stats-frames', exist_ok=True)
            for i in range(1, len(steps)+1):
                plt.close('all')
                frame_steps = steps[:i]
                frame_c0 = colony_0_prefs[:i]
                frame_c1 = colony_1_prefs[:i]
                frame_plot = create_preference_plot(frame_steps, frame_c0, frame_c1, args.title, xlim=xlim)
                frame_path = f'stats-frames/frame_{i:06d}.png'
                frame_plot.savefig(frame_path, dpi=150, bbox_inches='tight')
                print(f"Saved {frame_path}")
            print("Animation complete.")
            return
        else:
            # Interactive real-time animation
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            # Initial plots for preferences
            line_c0, = ax1.plot([], [], 'r-', linewidth=2, label='Colony 0 (Red)', alpha=0.8)
            line_c1, = ax1.plot([], [], 'k-', linewidth=2, label='Colony 1 (Black)', alpha=0.8)
            ax1.axhline(y=0.0, color='green', linestyle='--', alpha=0.3, label='Green food preference')
            ax1.axhline(y=1.0, color='orange', linestyle='--', alpha=0.3, label='Orange food preference')
            ax1.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5, label='Neutral preference')
            ax1.set_xlabel('Simulation Step')
            ax1.set_ylabel('Food Preference')
            ax1.set_title(f'{args.title} - Food Preferences')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim(ylim_prefs)
            ax1.set_xlim(xlim)
            # Initial plot for difference
            line_diff, = ax2.plot([], [], 'purple', linewidth=2, alpha=0.8)
            ax2.axhline(y=0, color='gray', linestyle=':', alpha=0.5)
            ax2.axhline(y=0.9, color='red', linestyle='--', alpha=0.5, label='Divergence threshold')
            ax2.axhline(y=-0.9, color='red', linestyle='--', alpha=0.5)
            ax2.set_xlabel('Simulation Step')
            ax2.set_ylabel('Preference Difference (Colony 0 - Colony 1)')
            ax2.set_title('Preference Divergence')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.set_ylim(ylim_diff)
            ax2.set_xlim(xlim)
            fig.tight_layout()
            plt.ion()  # Turn on interactive mode
            plt.show(block=False)
            for i in range(1, len(steps)+1):
                frame_steps = steps[:i]
                frame_c0 = colony_0_prefs[:i]
                frame_c1 = colony_1_prefs[:i]
                frame_diff = frame_c0 - frame_c1
                line_c0.set_data(frame_steps, frame_c0)
                line_c1.set_data(frame_steps, frame_c1)
                line_diff.set_data(frame_steps, frame_diff)
                fig.canvas.draw()
                fig.canvas.flush_events()
                #plt.pause(0.05)
            plt.ioff()  # Turn off interactive mode
            plt.show()  # Block to keep the final plot open
            print("Animation complete.")
            return

    plot = create_preference_plot(steps, colony_0_prefs, colony_1_prefs, args.title)

    output_file = args.output
    if args.save and output_file is None:
        output_file = "ant_colony_stats.png"

    if output_file:
        plot.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {output_file}")
    else:
        # Only try to show the plot if not using Agg backend
        if matplotlib.get_backend().lower() != 'agg':
            plot.show()
        else:
            print("Cannot display plot: Non-interactive backend (Agg) in use. Use --output or --save to save to a file.")
            sys.exit(1)

if __name__ == "__main__":
    main()