import os
import tempfile
from collections import namedtuple

import boto3
import pytest
import requests_mock
from PIL import Image
from moto import mock_s3

from config import BASE_DIR


@pytest.fixture
def temp_dir():
    temp_dir = tempfile.TemporaryDirectory()
    yield temp_dir.name
    temp_dir.cleanup()


@pytest.fixture
def image_file(temp_dir):
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", dir=temp_dir, delete=False) as tmp_file:
        # Create a sample image (you can replace this with your own image creation logic)
        image = Image.new("RGB", (100, 100), color="red")
        image.save(tmp_file, "PNG")

    # Return the path to the temporary image file
    yield tmp_file.name

    # Clean up: Remove the temporary image file after the test
    tmp_file.close()
    import os
    os.remove(tmp_file.name)


@pytest.fixture
def s3_client():
    with mock_s3():
        s3 = boto3.client("s3")
        yield s3


@pytest.fixture(scope="function")
def s3_bucket(s3_client):
    bucket_name = "pytest-s3-bucket"
    s3_client.create_bucket(Bucket=bucket_name)
    yield bucket_name
    # Clean up: Delete the S3 bucket after tests
    try:
        # Delete all objects in the bucket
        bucket = boto3.resource("s3").Bucket(bucket_name)
        bucket.objects.all().delete()

        # Delete the bucket itself
        s3_client.delete_bucket(Bucket=bucket_name)
    except Exception as e:
        pytest.fail(f"Failed to delete S3 bucket: {str(e)}")


@pytest.fixture
def response_content():
    with requests_mock.Mocker() as m:
        url = "https://example.com/sample.zip"
        m.get(url, content=open(os.path.join(BASE_DIR, "tests/test_arch.zip"), 'rb').read())
        yield url


@pytest.fixture
def argparse(response_content, s3_bucket):
    args = namedtuple("args", ["url", "bucket_name", "s3_key_prefix", "verbose", "concurrency"])
    return args(response_content, s3_bucket, "", True, 8)
