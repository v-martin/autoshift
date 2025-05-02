from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import io
from PIL import Image
from django.conf import settings


class Command(BaseCommand):
    help = 'Test file storage connection'

    def handle(self, *args, **options):
        # Test text file
        path = default_storage.save('test-file.txt', ContentFile(b'Test content'))
        self.stdout.write(self.style.SUCCESS(f'Text file saved at {path}'))
        
        # Try to access the file
        try:
            content = default_storage.open(path).read()
            self.stdout.write(self.style.SUCCESS(f'File content: {content}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading file: {e}'))
        
        # Try to get URL
        try:
            url = default_storage.url(path)
            self.stdout.write(self.style.SUCCESS(f'File URL: {url}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting URL: {e}'))
        
        # Delete the test file
        try:
            default_storage.delete(path)
            self.stdout.write(self.style.SUCCESS('Text file deleted'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error deleting file: {e}'))
            
        # Test image file
        try:
            # Create a test image
            image_io = io.BytesIO()
            image = Image.new('RGB', (100, 100), color='red')
            image.save(image_io, format='JPEG')
            image_io.seek(0)
            
            # Save the test image
            image_path = default_storage.save('user_avatars/test-image.jpg', ContentFile(image_io.getvalue()))
            self.stdout.write(self.style.SUCCESS(f'Image saved at {image_path}'))
            
            # Get the URL of the image
            image_url = default_storage.url(image_path)
            self.stdout.write(self.style.SUCCESS(f'Image URL: {image_url}'))
            
            # Create a test permanent image that won't be deleted
            perm_image_path = default_storage.save('user_avatars/example.jpeg', ContentFile(image_io.getvalue()))
            self.stdout.write(self.style.SUCCESS(f'Permanent image saved at {perm_image_path}'))
            self.stdout.write(self.style.SUCCESS(f'Permanent image URL: {default_storage.url(perm_image_path)}'))
            
            # Delete the test image
            default_storage.delete(image_path)
            self.stdout.write(self.style.SUCCESS('Image deleted'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error with image test: {e}'))
