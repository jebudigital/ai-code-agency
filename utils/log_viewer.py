#!/usr/bin/env python3
"""
Log Viewer Utility for AI Coding Agency
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import argparse

def view_logs(log_dir: str = "logs", component: str = None, lines: int = 50, follow: bool = False):
    """View logs from the specified component"""
    log_path = Path(log_dir)
    
    if not log_path.exists():
        print(f"❌ Log directory not found: {log_path}")
        return
    
    if component:
        # View specific component log
        log_file = log_path / f"{component}.log"
        if not log_file.exists():
            print(f"❌ Log file not found: {log_file}")
            return
        
        print(f"📋 Viewing {component} logs: {log_file}")
        print("=" * 80)
        
        try:
            with open(log_file, 'r') as f:
                lines_content = f.readlines()
                if lines > 0:
                    lines_content = lines_content[-lines:]
                
                for line in lines_content:
                    print(line.rstrip())
                    
                if follow:
                    print("\n🔄 Following logs (press Ctrl+C to stop)...")
                    # Simple tail follow implementation
                    try:
                        while True:
                            with open(log_file, 'r') as f:
                                f.seek(0, 2)  # Seek to end
                                while True:
                                    line = f.readline()
                                    if line:
                                        print(line.rstrip())
                                    else:
                                        import time
                                        time.sleep(0.1)
                    except KeyboardInterrupt:
                        print("\n👋 Stopped following logs")
                        
        except Exception as e:
            print(f"❌ Error reading log file: {e}")
    
    else:
        # List all available logs
        print(f"📁 Available logs in {log_path}:")
        print("=" * 50)
        
        log_files = list(log_path.glob("*.log"))
        if not log_files:
            print("No log files found.")
            return
        
        for log_file in sorted(log_files):
            if log_file.exists():
                stat = log_file.stat()
                size = stat.st_size
                modified = datetime.fromtimestamp(stat.st_mtime)
                
                print(f"📄 {log_file.stem}")
                print(f"   Size: {size:,} bytes")
                print(f"   Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
                print()
        
        print("To view a specific log:")
        print(f"  python utils/log_viewer.py --component <component_name>")
        print(f"  python utils/log_viewer.py --component main --lines 100")
        print(f"  python utils/log_viewer.py --component ollama --follow")

def export_logs(log_dir: str = "logs", output_file: str = None):
    """Export all logs to a single file"""
    log_path = Path(log_dir)
    
    if not log_path.exists():
        print(f"❌ Log directory not found: {log_path}")
        return
    
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"ai_coding_agency_logs_{timestamp}.txt"
    
    output_path = Path(output_file)
    
    try:
        with open(output_path, 'w') as f:
            f.write("AI Coding Agency - Complete Log Export\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            # Get all log files
            log_files = list(log_path.glob("*.log"))
            
            for log_file in sorted(log_files):
                if log_file.exists():
                    f.write(f"{log_file.stem.upper()} LOGS\n")
                    f.write("-" * (len(log_file.stem) + 6) + "\n")
                    
                    with open(log_file, 'r') as log_f:
                        f.write(log_f.read())
                    f.write("\n\n")
        
        print(f"✅ Logs exported to: {output_path}")
        
    except Exception as e:
        print(f"❌ Error exporting logs: {e}")

def show_performance_summary(log_dir: str = "logs"):
    """Show performance summary from logs"""
    log_path = Path(log_dir)
    
    if not log_path.exists():
        print(f"❌ Log directory not found: {log_path}")
        return
    
    perf_log = log_path / "performance.log"
    if not perf_log.exists():
        print("❌ Performance log not found")
        return
    
    print("📊 Performance Summary")
    print("=" * 30)
    
    try:
        with open(perf_log, 'r') as f:
            lines = f.readlines()
            
        # Parse performance data
        operations = {}
        for line in lines:
            if "Performance:" in line:
                try:
                    # Extract JSON data
                    start = line.find("{")
                    if start != -1:
                        import json
                        data = json.loads(line[start:])
                        op = data.get('operation', 'unknown')
                        duration = data.get('duration_seconds', 0)
                        
                        if op not in operations:
                            operations[op] = []
                        operations[op].append(duration)
                except:
                    continue
        
        if not operations:
            print("No performance data found")
            return
        
        for op, durations in operations.items():
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            total_duration = sum(durations)
            
            print(f"\n🔧 {op}")
            print(f"   Count: {len(durations)}")
            print(f"   Avg: {avg_duration:.2f}s")
            print(f"   Min: {min_duration:.2f}s")
            print(f"   Max: {max_duration:.2f}s")
            print(f"   Total: {total_duration:.2f}s")
            
    except Exception as e:
        print(f"❌ Error reading performance log: {e}")

def main():
    """Main function for log viewer"""
    parser = argparse.ArgumentParser(
        description="Log Viewer for AI Coding Agency",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--component', '-c', metavar='COMPONENT',
                       help='Component to view logs for (main, planner, coder, reviewer, doc_agent, project_manager, ollama, performance, errors)')
    parser.add_argument('--lines', '-n', type=int, default=50,
                       help='Number of lines to show (default: 50, 0 for all)')
    parser.add_argument('--follow', '-f', action='store_true',
                       help='Follow log file (like tail -f)')
    parser.add_argument('--export', '-e', action='store_true',
                       help='Export all logs to a single file')
    parser.add_argument('--output', '-o', metavar='FILE',
                       help='Output file for export')
    parser.add_argument('--performance', '-p', action='store_true',
                       help='Show performance summary')
    parser.add_argument('--log-dir', '-d', default='logs',
                       help='Log directory (default: logs)')
    
    args = parser.parse_args()
    
    if args.export:
        export_logs(args.log_dir, args.output)
    elif args.performance:
        show_performance_summary(args.log_dir)
    elif args.component:
        view_logs(args.log_dir, args.component, args.lines, args.follow)
    else:
        view_logs(args.log_dir)

if __name__ == "__main__":
    main()
