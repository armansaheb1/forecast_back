#!/usr/bin/env python3
"""
Disk space cleanup script with instrumentation for debugging.
This script cleans up Flutter temporary directories and build artifacts.
"""
import os
import shutil
import subprocess
import json
import time
from pathlib import Path

LOG_PATH = "/forecast_back/.cursor/debug.log"

def log_debug(session_id, run_id, hypothesis_id, location, message, data):
    """Write debug log entry in NDJSON format"""
    entry = {
        "sessionId": session_id,
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000)
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

def get_disk_usage(path):
    """Get disk usage for a path"""
    try:
        result = subprocess.run(
            ["df", "-h", path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def get_dir_size(path):
    """Get directory size in bytes"""
    try:
        result = subprocess.run(
            ["du", "-sb", path],
            capture_output=True,
            text=True,
            check=True
        )
        return int(result.stdout.split()[0])
    except:
        return 0

def main():
    session_id = "debug-session"
    run_id = "cleanup-run-1"
    
    # #region agent log
    try:
        log_debug(session_id, run_id, "A", "cleanup_disk_space.py:main", "Starting disk cleanup", {
            "timestamp": time.time()
        })
    except Exception as e:
        print(f"Warning: Could not write log: {e}")
    # #endregion
    
    # Hypothesis A: Flutter temp directories accumulating in /tmp
    # Hypothesis B: Build artifacts consuming excessive space
    # Hypothesis C: Old build caches not being cleaned
    # Hypothesis D: Multiple Flutter processes leaving orphaned temp dirs
    # Hypothesis E: Disk space not being monitored/cleaned proactively
    
    # Check initial disk space
    initial_disk = get_disk_usage("/")
    print(f"Initial disk usage:\n{initial_disk}\n")
    # #region agent log
    try:
        log_debug(session_id, run_id, "A", "cleanup_disk_space.py:main", "Initial disk usage", {
            "usage": initial_disk
        })
    except:
        pass
    # #endregion
    
    # Clean up Flutter temp directories in /tmp
    tmp_flutter_dirs = list(Path("/tmp").glob("flutter_tools.*"))
    print(f"Found {len(tmp_flutter_dirs)} Flutter temp directories")
    # #region agent log
    try:
        log_debug(session_id, run_id, "A", "cleanup_disk_space.py:main", "Found Flutter temp directories", {
            "count": len(tmp_flutter_dirs),
            "dirs": [str(d) for d in tmp_flutter_dirs[:5]]  # Log first 5
        })
    except:
        pass
    # #endregion
    
    total_freed = 0
    for tmp_dir in tmp_flutter_dirs:
        if tmp_dir.is_dir():
            size_before = get_dir_size(str(tmp_dir))
            # #region agent log
            log_debug(session_id, run_id, "A", "cleanup_disk_space.py:main", "Before removing temp dir", {
                "path": str(tmp_dir),
                "size_bytes": size_before
            })
            # #endregion
            try:
                shutil.rmtree(str(tmp_dir))
                total_freed += size_before
                print(f"  Removed {tmp_dir.name} ({size_before / (1024*1024):.1f} MB)")
                # #region agent log
                try:
                    log_debug(session_id, run_id, "A", "cleanup_disk_space.py:main", "Removed temp dir", {
                        "path": str(tmp_dir),
                        "freed_bytes": size_before
                    })
                except:
                    pass
                # #endregion
            except Exception as e:
                print(f"  Failed to remove {tmp_dir.name}: {e}")
                # #region agent log
                try:
                    log_debug(session_id, run_id, "A", "cleanup_disk_space.py:main", "Failed to remove temp dir", {
                        "path": str(tmp_dir),
                        "error": str(e)
                    })
                except:
                    pass
                # #endregion
    
    # Clean up Flutter build directory (keep structure, remove intermediates)
    build_dir = Path("/forecast_back/forecast_app/build")
    if build_dir.exists():
        build_size_before = get_dir_size(str(build_dir))
        # #region agent log
        log_debug(session_id, run_id, "B", "cleanup_disk_space.py:main", "Before cleaning build dir", {
            "path": str(build_dir),
            "size_bytes": build_size_before
        })
        # #endregion
        
        # Remove build intermediates but keep the structure
        intermediates = build_dir / "app" / "intermediates"
        if intermediates.exists():
            intermediates_size_before = get_dir_size(str(intermediates))
            try:
                shutil.rmtree(str(intermediates))
                total_freed += intermediates_size_before
                # #region agent log
                log_debug(session_id, run_id, "B", "cleanup_disk_space.py:main", "Removed build intermediates", {
                    "path": str(intermediates),
                    "freed_bytes": intermediates_size_before
                })
                # #endregion
            except Exception as e:
                # #region agent log
                log_debug(session_id, run_id, "B", "cleanup_disk_space.py:main", "Failed to remove intermediates", {
                    "error": str(e)
                })
                # #endregion
    
    # Check final disk space
    final_disk = get_disk_usage("/")
    # #region agent log
    log_debug(session_id, run_id, "A", "cleanup_disk_space.py:main", "Final disk usage", {
        "usage": final_disk,
        "total_freed_bytes": total_freed,
        "total_freed_mb": round(total_freed / (1024 * 1024), 2)
    })
    # #endregion
    
    print(f"\nCleanup complete. Freed approximately {round(total_freed / (1024 * 1024), 2)} MB")
    print(f"\nFinal disk usage:\n{final_disk}")

if __name__ == "__main__":
    main()

