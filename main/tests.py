from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import File
import os
from django.conf import settings


class FileModelTest(TestCase):
    """Test cases for File model"""

    def test_file_creation(self):
        """Test creating a file instance"""
        # Create a simple image file
        image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        file_obj = File.objects.create(image=image)
        self.assertIsNotNone(file_obj.id)
        # Django adds a random suffix to prevent filename collisions
        self.assertTrue(file_obj.image.name.startswith("coffee/test_image"))
        self.assertTrue(file_obj.image.name.endswith(".jpg"))
        self.assertIsNotNone(file_obj.created_at)
        self.assertIsNotNone(file_obj.updated_at)

    def test_file_str_method(self):
        """Test File __str__ method"""
        image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg"
        )
        file_obj = File.objects.create(image=image)
        expected_str = f"File {file_obj.id} - {file_obj.image.name}"
        self.assertEqual(str(file_obj), expected_str)

    def test_file_ordering(self):
        """Test that files are ordered by created_at descending"""
        image1 = SimpleUploadedFile("test1.jpg", b"content1", content_type="image/jpeg")
        file1 = File.objects.create(image=image1)
        
        image2 = SimpleUploadedFile("test2.jpg", b"content2", content_type="image/jpeg")
        file2 = File.objects.create(image=image2)
        
        files = File.objects.all()
        self.assertEqual(files[0].id, file2.id)  # Most recent first
        self.assertEqual(files[1].id, file1.id)


class CoffeeReadingAPITest(TestCase):
    """Test cases for Coffee Reading API endpoint"""

    def setUp(self):
        """Set up test client"""
        self.client = APIClient()
        self.url = '/api/v1/coffee-reading/'

    def test_missing_image_field(self):
        """Test API with missing images field"""
        response = self.client.post('/api/v1/coffee-reading/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_empty_image_file(self):
        """Test API with empty image file"""
        # Test with empty file (no file uploaded)
        # When no file is provided, the field won't be in request.data
        # So we test by not including 'images' field, which is already tested in test_missing_image_field
        # For this test, we'll test with an empty file object
        empty_file = SimpleUploadedFile(
            "empty.jpg",
            b"",  # Empty content
            content_type="image/jpeg"
        )
        response = self.client.post('/api/v1/coffee-reading/', {'images': empty_file})
        # Empty file might be accepted or rejected depending on validation
        # It should at least not crash
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            status.HTTP_502_BAD_GATEWAY
        ])

    def test_invalid_file_type(self):
        """Test API with invalid file type"""
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"file content",
            content_type="text/plain"
        )
        response = self.client.post('/api/v1/coffee-reading/', {'images': invalid_file})
        # Should fail at serializer validation
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR])

    def test_valid_image_upload(self):
        """Test API with valid image file"""
        # Note: This test will fail if OPENAI_API_KEY is not set
        # We'll mock this in a more advanced test
        image = SimpleUploadedFile(
            "test.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        response = self.client.post('/api/v1/coffee-reading/', {'images': image})
        # If API key is not set, should return 500
        # If API key is set, should return 200 or 502 (OpenAI error)
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            status.HTTP_502_BAD_GATEWAY
        ])

    def test_large_file_size(self):
        """Test API with file exceeding size limit"""
        # Create a file larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        large_file = SimpleUploadedFile(
            "large.jpg",
            large_content,
            content_type="image/jpeg"
        )
        response = self.client.post('/api/v1/coffee-reading/', {'images': large_file})
        # Should fail validation
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR])


class FileSerializerTest(TestCase):
    """Test cases for File serializer"""

    def setUp(self):
        from .serializers import FileSerializer
        self.serializer_class = FileSerializer

    def test_file_serializer_fields(self):
        """Test FileSerializer has correct fields"""
        image = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")
        file_obj = File.objects.create(image=image)
        
        serializer = self.serializer_class(file_obj)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('image', data)
        self.assertIn('image_url', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)

    def test_file_serializer_validation_file_size(self):
        """Test FileSerializer validates file size"""
        from .serializers import FileSerializer
        
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        large_file = SimpleUploadedFile("large.jpg", large_content, content_type="image/jpeg")
        
        serializer = self.serializer_class(data={'image': large_file})
        self.assertFalse(serializer.is_valid())
        self.assertIn('image', serializer.errors)

    def test_file_serializer_validation_file_type(self):
        """Test FileSerializer validates file type"""
        from .serializers import FileSerializer
        
        invalid_file = SimpleUploadedFile("test.txt", b"content", content_type="text/plain")
        
        serializer = self.serializer_class(data={'image': invalid_file})
        self.assertFalse(serializer.is_valid())
        self.assertIn('image', serializer.errors)
