import os
import hashlib
import logging
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
import shutil
from typing import List, Tuple

# Configure logging
log_file = os.path.expanduser('~/mac_resource_cleaner.log')
logger = logging.getLogger('ResourceCleaner')
logger.setLevel(logging.INFO)

# Create and configure file handler
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Create and configure stream handler
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Clear existing handlers and add new ones
logger.handlers = []
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

class MacResourceCleaner:
    """Class to check and clean unused system resources on macOS."""

    def __init__(self):
        self.cache_dirs = [
            os.path.expanduser('~/Library/Caches'),
            '/Library/Caches',
            '/System/Library/Caches'
        ]
        self.app_support_dir = os.path.expanduser('~/Library/Application Support')
        self.downloads_dir = os.path.expanduser('~/Downloads')
        self.log_dirs = [
            os.path.expanduser('~/Library/Logs'),
            '/Library/Logs',
            '/var/log'
        ]
        self.days_old = 30  # Files older than 30 days are considered stale
        self.size_threshold = 10 * 1024 * 1024  # 10 MB for large log files

    def get_file_age(self, file_path: str) -> float:
        """Get file age in days."""
        try:
            mtime = os.path.getmtime(file_path)
            file_age = (datetime.now() - datetime.fromtimestamp(mtime)).days
            return file_age
        except Exception as e:
            logger.error(f"Error getting age of {file_path}: {e}")
            return 0

    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""
        try:
            return os.path.getsize(file_path)
        except Exception as e:
            logger.error(f"Error getting size of {file_path}: {e}")
            return 0

    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        try:
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ''

    def check_cache_files(self) -> List[Tuple[str, str, int]]:
        """Check for old cache files."""
        old_caches = []
        for cache_dir in self.cache_dirs:
            if not os.path.exists(cache_dir):
                logger.warning(f"Cache directory {cache_dir} does not exist")
                continue
            for root, _, files in os.walk(cache_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self.get_file_age(file_path) > self.days_old:
                        size = self.get_file_size(file_path)
                        old_caches.append((file_path, 'Cache', size))
        return old_caches

    def check_orphaned_app_support(self) -> List[Tuple[str, str, int]]:
        """Check for orphaned Application Support files."""
        orphaned = []
        if not os.path.exists(self.app_support_dir):
            logger.warning(f"Application Support directory {self.app_support_dir} does not exist")
            return orphaned
        installed_apps = {app.stem for app in Path('/Applications').glob('*.app')}
        for app_dir in os.listdir(self.app_support_dir):
            app_dir_path = os.path.join(self.app_support_dir, app_dir)
            if os.path.isdir(app_dir_path) and app_dir not in installed_apps:
                size = sum(self.get_file_size(os.path.join(root, f))
                          for root, _, fs in os.walk(app_dir_path) for f in fs)
                orphaned.append((app_dir_path, 'Orphaned App Support', size))
        return orphaned

    def check_duplicate_files(self, directory: str = None) -> List[Tuple[str, str, int]]:
        """Check for duplicate files in the specified directory."""
        if directory is None:
            directory = self.downloads_dir
        if not os.path.exists(directory):
            logger.warning(f"Directory {directory} does not exist")
            return []
        file_hashes = {}
        duplicates = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path):
                    file_hash = self.calculate_file_hash(file_path)
                    if file_hash:
                        if file_hash in file_hashes:
                            file_hashes[file_hash].append(file_path)
                        else:
                            file_hashes[file_hash] = [file_path]
        for file_hash, paths in file_hashes.items():
            if len(paths) > 1:
                for path in paths[1:]:  # Keep the first file, mark others as duplicates
                    size = self.get_file_size(path)
                    duplicates.append((path, 'Duplicate File', size))
        return duplicates

    def check_large_logs(self) -> List[Tuple[str, str, int]]:
        """Check for large log files."""
        large_logs = []
        for log_dir in self.log_dirs:
            if not os.path.exists(log_dir):
                logger.warning(f"Log directory {log_dir} does not exist")
                continue
            for root, _, files in os.walk(log_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    size = self.get_file_size(file_path)
                    if size > self.size_threshold:
                        large_logs.append((file_path, 'Large Log', size))
        return large_logs

    def check_empty_dirs(self, directory: str = None) -> List[Tuple[str, str, int]]:
        """Check for empty directories in the specified directory."""
        if directory is None:
            directory = os.path.expanduser('~')
        empty_dirs = []
        for root, dirs, files in os.walk(directory):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not any(os.scandir(dir_path)):  # Directory is empty
                        empty_dirs.append((dir_path, 'Empty Directory', 0))
                except Exception as e:
                    logger.error(f"Error checking directory {dir_path}: {e}")
        return empty_dirs

    def scan_resources(self) -> List[Tuple[str, str, int]]:
        """Scan all types of unused resources."""
        logger.info("Starting resource scan")
        resources = []
        resources.extend(self.check_cache_files())
        resources.extend(self.check_orphaned_app_support())
        resources.extend(self.check_duplicate_files())
        resources.extend(self.check_large_logs())
        resources.extend(self.check_empty_dirs())
        logger.info(f"Found {len(resources)} unused resources")
        return resources

    def print_resources(self, resources: List[Tuple[str, str, int]]):
        """Print list of unused resources."""
        if not resources:
            print("No unused resources found.")
            logger.info("No unused resources found")
            return
        print("\nUnused Resources Found:")
        print("=" * 80)
        print(f"{'Path':<50} {'Type':<20} {'Size (MB)':<10}")
        print("-" * 80)
        for path, resource_type, size in resources:
            size_mb = size / (1024 * 1024)
            print(f"{path:<50} {resource_type:<20} {size_mb:.2f}")
            logger.info(f"Unused resource: {path} ({resource_type}, {size_mb:.2f} MB)")

    def delete_resources(self, resources: List[Tuple[str, str, int]], confirm: bool = True):
        """Delete specified resources with user confirmation."""
        if not resources:
            logger.info("No resources to delete")
            return
        if confirm:
            print("\nWARNING: The following resources will be deleted:")
            self.print_resources(resources)
            response = input("Confirm deletion (y/n)? ").strip().lower()
            if response != 'y':
                logger.info("Deletion cancelled by user")
                print("Deletion cancelled.")
                return
        for path, resource_type, _ in resources:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    logger.info(f"Deleted file: {path} ({resource_type})")
                elif os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                    logger.info(f"Deleted directory: {path} ({resource_type})")
            except Exception as e:
                logger.error(f"Failed to delete {path}: {e}")
                print(f"Failed to delete {path}: {e}")

def scan_and_log():
    """Run resource scan and log results."""
    cleaner = MacResourceCleaner()
    print("Scanning for unused macOS resources...")
    resources = cleaner.scan_resources()
    cleaner.print_resources(resources)
    print("\nScan complete. Check ~/mac_resource_cleaner.log for details.")

def main():
    """Main function to schedule and run resource checks."""
    try:
        logger.info("Starting macOS resource cleaner")
        # Schedule scans every 3 hours
        schedule.every(3).hours.do(scan_and_log)
        # Run first scan immediately
        scan_and_log()
        # Keep script running for scheduled tasks
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Script stopped by user")
        print("Script stopped by user")
    except Exception as e:
        logger.error(f"Script error: {e}")
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
