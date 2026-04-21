#!/usr/bin/env python3
"""
Enhanced Drive File Monitor for Narrative Orchestrator v0.5

Monitors Google Drive folder for manifest.json changes and automatically
triggers the Figma pipeline when updates are detected.

Author: Cursor Agent - Enhanced Narrative Orchestrator System
Version: 0.5.0
"""

import json
import time
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Callable
import subprocess
import os

# ─── LOGGING SETUP ──
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('core/monitors/watch_drive.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DriveManifestMonitor:
    """
    Monitors Google Drive manifest.json files for changes and triggers
    the enhanced Figma pipeline automatically.
    """
    
    def __init__(self, drive_folder: str, polling_interval: int = 30):
        """
        Initialize the Drive monitor.
        
        Args:
            drive_folder: Path to Google Drive project folder
            polling_interval: How often to check for changes (seconds)
        """
        self.drive_folder = Path(drive_folder).expanduser()
        self.manifest_path = self.drive_folder / "manifest.json"
        self.polling_interval = polling_interval
        self.last_hash: Optional[str] = None
        self.last_modified: Optional[float] = None
        self.callback: Optional[Callable[[Dict[str, Any]], None]] = None
        
        # Ensure drive folder exists
        self.drive_folder.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized Drive monitor for: {self.manifest_path}")
        logger.info(f"Polling interval: {polling_interval} seconds")
    
    def set_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Set callback function to execute when manifest changes."""
        self.callback = callback
    
    def calculate_file_hash(self) -> Optional[str]:
        """Calculate SHA-256 hash of manifest file."""
        try:
            if not self.manifest_path.exists():
                return None
            
            with open(self.manifest_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            return None
    
    def load_manifest(self) -> Optional[Dict[str, Any]]:
        """Load and parse manifest.json."""
        try:
            if not self.manifest_path.exists():
                logger.warning(f"Manifest file not found: {self.manifest_path}")
                return None
            
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                
            # Validate basic structure
            if not isinstance(manifest, dict):
                logger.error("Manifest is not a valid JSON object")
                return None
                
            if 'initiative_metadata' not in manifest:
                logger.error("Manifest missing required 'initiative_metadata' field")
                return None
            
            logger.info(f"Loaded manifest: {manifest.get('initiative_metadata', {}).get('name', 'Unnamed')}")
            return manifest
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in manifest file: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading manifest: {e}")
            return None
    
    def trigger_pipeline(self, manifest: Dict[str, Any]) -> bool:
        """
        Trigger the enhanced Figma pipeline with the updated manifest.
        """
        try:
            logger.info("🚀 Triggering enhanced Figma pipeline...")
            
            # Extract key info for logging
            initiative_name = manifest.get('initiative_metadata', {}).get('name', 'Unknown')
            version = manifest.get('initiative_metadata', {}).get('version', '0.0')
            schema_version = manifest.get('schema_version', '0.4')
            
            logger.info(f"Initiative: {initiative_name} v{version} (Schema: {schema_version})")
            
            # If callback is set, use it (for programmatic integration)
            if self.callback:
                logger.info("Executing registered callback...")
                self.callback(manifest)
                return True
            
            # Otherwise, trigger via Cursor CLI (if available)
            try:
                cursor_cmd = [
                    'cursor-agent', 
                    '--project', str(self.drive_folder.parent),
                    '--message', f'Run the enhanced Figma pipeline for manifest at {self.manifest_path}'
                ]
                
                result = subprocess.run(cursor_cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    logger.info("✅ Pipeline triggered via Cursor CLI")
                    return True
                else:
                    logger.warning(f"Cursor CLI returned error: {result.stderr}")
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.warning("Cursor CLI not available or timeout")
            
            # Fallback: Log detailed trigger info for manual processing
            self._log_pipeline_trigger(manifest)
            return True
            
        except Exception as e:
            logger.error(f"Failed to trigger pipeline: {e}")
            return False
    
    def _log_pipeline_trigger(self, manifest: Dict[str, Any]) -> None:
        """Log detailed trigger information for manual processing."""
        
        trigger_log = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'trigger_type': 'drive_manifest_change',
            'manifest_path': str(self.manifest_path),
            'initiative_metadata': manifest.get('initiative_metadata', {}),
            'flows_count': len(manifest.get('flows', [])),
            'schema_version': manifest.get('schema_version', '0.4'),
            'auto_sync': manifest.get('drive', {}).get('auto_sync', False),
            'figma_file': manifest.get('figma', {}).get('target_file_url'),
            'exports_folder': manifest.get('drive', {}).get('exports_folder')
        }
        
        trigger_log_path = self.drive_folder.parent / 'core' / 'monitors' / 'pipeline_triggers.jsonl'
        trigger_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(trigger_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(trigger_log) + '\n')
        
        logger.info(f"📝 Pipeline trigger logged to: {trigger_log_path}")
        logger.info("🔔 MANUAL ACTION REQUIRED: Open Cursor and run the pipeline")
    
    def check_for_changes(self) -> bool:
        """Check if manifest file has changed."""
        try:
            if not self.manifest_path.exists():
                if self.last_hash is not None:
                    logger.info("Manifest file was deleted")
                    self.last_hash = None
                    self.last_modified = None
                return False
            
            # Get file modification time and hash
            current_modified = self.manifest_path.stat().st_mtime
            current_hash = self.calculate_file_hash()
            
            if current_hash is None:
                return False
            
            # Check if file changed
            if self.last_hash != current_hash or self.last_modified != current_modified:
                logger.info(f"📄 Manifest change detected: {self.manifest_path}")
                logger.info(f"Previous hash: {self.last_hash}")
                logger.info(f"Current hash: {current_hash}")
                
                self.last_hash = current_hash
                self.last_modified = current_modified
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking for changes: {e}")
            return False
    
    def start_monitoring(self) -> None:
        """Start the monitoring loop."""
        logger.info("🔍 Starting Drive manifest monitoring...")
        logger.info(f"Watching: {self.manifest_path}")
        logger.info("Press Ctrl+C to stop")
        
        # Initialize baseline
        self.last_hash = self.calculate_file_hash()
        if self.manifest_path.exists():
            self.last_modified = self.manifest_path.stat().st_mtime
            logger.info(f"Baseline established - Hash: {self.last_hash}")
        
        try:
            while True:
                if self.check_for_changes():
                    manifest = self.load_manifest()
                    if manifest:
                        success = self.trigger_pipeline(manifest)
                        if success:
                            logger.info("✅ Pipeline trigger completed")
                        else:
                            logger.error("❌ Pipeline trigger failed")
                    else:
                        logger.error("Failed to load changed manifest")
                
                time.sleep(self.polling_interval)
                
        except KeyboardInterrupt:
            logger.info("\n⏹️ Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            raise


def main():
    """Main entry point for Drive monitoring."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Drive Manifest Monitor')
    parser.add_argument('drive_folder', help='Path to Google Drive project folder')
    parser.add_argument('--interval', type=int, default=30, 
                       help='Polling interval in seconds (default: 30)')
    parser.add_argument('--verbose', action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and start monitor
    monitor = DriveManifestMonitor(args.drive_folder, args.interval)
    monitor.start_monitoring()


if __name__ == "__main__":
    main()