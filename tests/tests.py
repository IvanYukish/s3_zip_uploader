import boto3

from s3_zip_uploader_Ivan_Yukish.uploader import upload_files_to_s3, run_uploader


def test_upload_files_to_s3(image_file, s3_client, s3_bucket):
    upload_files_to_s3(file_name=image_file, bucket_name=s3_bucket, s3_key_prefix="")

    s3 = boto3.resource('s3')
    key = "/".join(image_file.split("/")[3:])
    obj = s3.Object(s3_bucket, key)

    assert obj.key == key
    assert obj.bucket_name == s3_bucket


def test_run_uploader(argparse, s3_client):
    run_uploader(argparse)
    archive_files_amount = 6

    storage_objs = s3_client.list_objects(Bucket=argparse.bucket_name)
    assert len(storage_objs.get("Contents")) == archive_files_amount
