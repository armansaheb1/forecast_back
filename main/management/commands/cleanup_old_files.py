import os
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from main.models import File
from django.conf import settings

logger = logging.getLogger('main')


class Command(BaseCommand):
    help = 'Clean up old uploaded files and their database records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to keep files (default: 30)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Find old files
        old_files = File.objects.filter(created_at__lt=cutoff_date)
        count = old_files.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(f'No files older than {days} days found.')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'Found {count} file(s) older than {days} days.')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN: Files that would be deleted:')
            )
            for file_obj in old_files:
                self.stdout.write(f'  - {file_obj.image.name} (ID: {file_obj.id}, Created: {file_obj.created_at})')
            return
        
        # Delete files
        deleted_count = 0
        error_count = 0
        
        for file_obj in old_files:
            try:
                # Delete physical file
                if file_obj.image:
                    file_path = file_obj.image.path
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f'Deleted file: {file_path}')
                
                # Delete database record
                file_obj.delete()
                deleted_count += 1
                
            except Exception as e:
                error_count += 1
                logger.error(f'Error deleting file {file_obj.id}: {str(e)}')
                self.stdout.write(
                    self.style.ERROR(f'Error deleting file {file_obj.id}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {deleted_count} file(s). '
                f'Errors: {error_count}'
            )
        )
        
        # Clean up empty directories
        self._cleanup_empty_directories()

    def _cleanup_empty_directories(self):
        """Remove empty directories in media/coffee"""
        media_path = os.path.join(settings.MEDIA_ROOT, 'coffee')
        
        if not os.path.exists(media_path):
            return
        
        try:
            # Walk through directories and remove empty ones
            for root, dirs, files in os.walk(media_path, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        if not os.listdir(dir_path):  # Directory is empty
                            os.rmdir(dir_path)
                            logger.info(f'Removed empty directory: {dir_path}')
                    except OSError:
                        pass  # Directory not empty or other error
        except Exception as e:
            logger.error(f'Error cleaning up directories: {str(e)}')

