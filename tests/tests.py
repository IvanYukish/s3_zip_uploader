import io
import os
import tarfile

import boto3

from s3_zip_uploader_Ivan_Yukish.uploader import build_s3_key, upload_files_to_s3, run_uploader

EXPECTED_KEYS = sorted(f"Maz/photo_54746288293613274{n}_y.jpg" for n in range(66, 72))


def list_keys(s3_client, bucket_name):
    storage_objs = s3_client.list_objects(Bucket=bucket_name)
    return sorted(obj["Key"] for obj in storage_objs.get("Contents", []))


def test_upload_files_to_s3(image_file, s3_client, s3_bucket):
    key = "images/sample.png"
    upload_files_to_s3(file_name=image_file, bucket_name=s3_bucket, key=key)

    s3 = boto3.resource('s3')
    obj = s3.Object(s3_bucket, key)

    assert obj.key == key
    assert obj.bucket_name == s3_bucket
    assert obj.content_length == os.path.getsize(image_file)


def test_build_s3_key():
    base_dir = os.path.join("tmp", "extracted")
    file_name = os.path.join(base_dir, "Maz", "photo.jpg")

    assert build_s3_key(file_name, base_dir, "") == "Maz/photo.jpg"
    assert build_s3_key(file_name, base_dir, "backup") == "backup/Maz/photo.jpg"
    assert build_s3_key(file_name, base_dir, "backup/") == "backup/Maz/photo.jpg"


def test_run_uploader(argparse, s3_client):
    run_uploader(argparse)
    archive_files_amount = 6

    storage_objs = s3_client.list_objects(Bucket=argparse.bucket_name)
    assert len(storage_objs.get("Contents")) == archive_files_amount


def test_run_uploader_archive_formats(archive_url, make_args, s3_client):
    args = make_args(archive_url)

    assert run_uploader(args) is True
    assert list_keys(s3_client, args.bucket_name) == EXPECTED_KEYS


def test_run_uploader_with_key_prefix(archive_url, make_args, s3_client):
    args = make_args(archive_url, s3_key_prefix="backup")

    assert run_uploader(args) is True
    assert list_keys(s3_client, args.bucket_name) == [f"backup/{key}" for key in EXPECTED_KEYS]


def test_run_uploader_unsupported_archive(http_mock, make_args, s3_client):
    url = "https://example.com/not-an-archive"
    http_mock.get(url, content=b"just some plain text")
    args = make_args(url)

    assert run_uploader(args) is False
    assert list_keys(s3_client, args.bucket_name) == []


def test_run_uploader_rejects_tar_path_traversal(http_mock, make_args, s3_client):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar_ref:
        content = b"malicious"
        member = tarfile.TarInfo(name="../evil.txt")
        member.size = len(content)
        tar_ref.addfile(member, io.BytesIO(content))
    url = "https://example.com/evil"
    http_mock.get(url, content=buffer.getvalue())
    args = make_args(url)

    assert run_uploader(args) is False
    assert list_keys(s3_client, args.bucket_name) == []
