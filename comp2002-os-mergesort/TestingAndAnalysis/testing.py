import subprocess
import re
import csv
import time
import os
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
import math

# Path to the compiled mergesort executable
EXECUTABLE = "../test-mergesort"

# Parameters to test
input_sizes = [10, 100, 10_000, 1_000_000, 10_000_000,100_000_000]
# input_sizes = [10,100,10_000]
# cutoff_levels = [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
cutoff_levels = [0, 1, 2, 4, 8, 16, 32, 2048]
seeds = [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]

# Output file for results
OUTPUT_CSV = "mergesort_results.csv"

def run_test(size, cutoff, seed):
    """Runs a single test and returns (success, time_sec, output_str)."""
    try:
        start_time = time.time()
        result = subprocess.run(
            [EXECUTABLE, str(size), str(cutoff), str(seed)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=100,
            text=True
        )
        end_time = time.time()
        elapsed = end_time - start_time

        output = result.stdout.strip()
        # Match successful output
        match = re.search(r"Sorting (\d+) elements took ([\d.]+) seconds", output)
        if match:
            return True, float(match.group(2)), output
        else:
            return False, None, output + "\n" + result.stderr

    except subprocess.TimeoutExpired:
        return False, None, f"Timeout for size={size}, cutoff={cutoff}, seed={seed}"

def main():
    print("=== Parallel Merge Sort Benchmark ===")
    results = []
    baseline = None
    
    for size in input_sizes:
        for cutoff in cutoff_levels:
            for seed in seeds:
                print(f"Running: size={size}, cutoff={cutoff}, seed={seed} ... ", end="")
                success, time_taken, output = run_test(size, cutoff, seed)
                status = "OK" if success else "FAIL"
                print(status)
                if cutoff == 0: baseline = time_taken if time_taken else -1
                results.append({
                    "size": size,
                    "cutoff": cutoff,
                    "seed": seed,
                    "success": success,
                    "time_sec": time_taken if time_taken else -1,
                    "speedup": (baseline if baseline else -1) / (time_taken if time_taken else -1),
                    "output": output[:200].replace("\n", " ")
                })

    # Write to CSV
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["size", "cutoff", "seed", "success", "time_sec", "output"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to {OUTPUT_CSV}")

    # --- Generate performance graphs ---
    plot_results(results)

def plot_results(results):
    # Group by cutoff level for comparison
    plt.figure(figsize=(10, 6))
    for cutoff in sorted(set(r["cutoff"] for r in results)):
        sizes = [r["size"] for r in results if r["cutoff"] == cutoff and r["success"]]
        times = [r["time_sec"] for r in results if r["cutoff"] == cutoff and r["success"]]
        if sizes and times:
            plt.plot(sizes, times, marker="o", label=f"Cutoff {cutoff}")

    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Input Size (n)")
    plt.ylabel("Time (seconds)")
    plt.title("Parallel Merge Sort Performance vs. Input Size and Cutoff Level")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.tight_layout()
    plt.savefig("mergesort_performance.png")
    print("Graph saved as mergesort_performance.png")


if __name__ == "__main__":
    main()
