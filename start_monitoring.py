#!/usr/bin/env python3
"""
Enhanced Narrative Orchestrator v2.0 - Quick Start Script
Launches Drive monitoring with automatic pipeline execution
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.monitors.watch_drive import DriveManifestMonitor

def main():
    parser = argparse.ArgumentParser(
        description='🚀 Enhanced Narrative Orchestrator v2.0 - Quick Start',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start monitoring Wolverine sample project
  python start_monitoring.py samples/wolverine
  
  # Monitor with custom interval
  python start_monitoring.py /path/to/drive --interval 15
  
  # Monitor with verbose logging
  python start_monitoring.py /path/to/drive --verbose
  
  # Test mode (no actual pipeline execution)
  python start_monitoring.py samples/wolverine --test
        """
    )
    
    parser.add_argument('drive_folder', 
                       help='Path to Google Drive project folder or sample folder')
    parser.add_argument('--interval', type=int, default=30,
                       help='Polling interval in seconds (default: 30)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--test', action='store_true',
                       help='Test mode - detect changes but don\'t execute pipeline')
    
    args = parser.parse_args()
    
    # Print welcome banner
    print("🚀 Enhanced Narrative Orchestrator v2.0")
    print("=" * 50)
    print("✨ Features: SLDS Integration | Drive Monitoring | Auto Pipeline")
    print("📍 Monitoring:", args.drive_folder)
    print("⏱️  Interval:", f"{args.interval} seconds")
    print("🔧 Mode:", "TEST" if args.test else "PRODUCTION")
    print("=" * 50)
    
    # Validate folder
    drive_path = Path(args.drive_folder).expanduser()
    if not drive_path.exists():
        print(f"❌ Error: Folder not found: {drive_path}")
        sys.exit(1)
    
    # Check for manifest file
    manifest_path = drive_path / "manifest.json"
    if manifest_path.exists():
        print(f"📄 Found manifest: {manifest_path}")
    else:
        print(f"⚠️  No manifest.json found in {drive_path}")
        print("   Monitoring will wait for manifest creation...")
    
    # Setup monitoring
    monitor = DriveManifestMonitor(str(drive_path), args.interval)
    
    if args.test:
        def test_callback(manifest):
            print(f"🧪 TEST MODE: Would execute pipeline for {manifest.get('initiative_metadata', {}).get('name', 'Unknown')}")
        monitor.set_callback(test_callback)
    
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n👋 Enhanced Orchestrator stopped. Thanks for using v2.0!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()