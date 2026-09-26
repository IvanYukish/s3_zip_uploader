import os
import tarfile
import tempfile
import zipfile
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


TEST_ARCHIVE_PATH = os.path.join(BASE_DIR, "tests/test_arch.zip")
TAR_MODES = {
    "tar": "w",
    "tar.gz": "w:gz",
    "tar.bz2": "w:bz2",
    "tar.xz": "w:xz",
}


@pytest.fixture
def http_mock():
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def response_content(http_mock):
    url = "https://example.com/sample.zip"
    with open(TEST_ARCHIVE_PATH, "rb") as f:
        http_mock.get(url, content=f.read())
    yield url


@pytest.fixture(params=["zip", *TAR_MODES])
def archive_url(request, http_mock, temp_dir):
    """Serve the test archive repacked in each supported format.

    The URL has no file extension, so the uploader has to detect the format by content.
    """
    archive_format = request.param
    if archive_format == "zip":
        archive_path = TEST_ARCHIVE_PATH
    else:
        source_dir = os.path.join(temp_dir, "source")
        with zipfile.ZipFile(TEST_ARCHIVE_PATH) as zip_ref:
            zip_ref.extractall(source_dir)
        archive_path = os.path.join(temp_dir, f"test_arch.{archive_format}")
        with tarfile.open(archive_path, TAR_MODES[archive_format]) as tar_ref:
            tar_ref.add(os.path.join(source_dir, "Maz"), arcname="Maz")

    url = f"https://example.com/download/{archive_format.replace('.', '-')}"
    with open(archive_path, "rb") as f:
        http_mock.get(url, content=f.read())
    yield url


@pytest.fixture
def make_args(s3_bucket):
    args = namedtuple("args", ["url", "bucket_name", "s3_key_prefix", "verbose", "concurrency"])

    def _make_args(url, s3_key_prefix=""):
        return args(url, s3_bucket, s3_key_prefix, True, 8)

    return _make_args


@pytest.fixture
def argparse(response_content, make_args):
    return make_args(response_content)
