import concurrent.futures
import glob
import logging
import os
import zipfile
from tempfile import TemporaryDirectory

import boto3
import requests

logger = logging.getLogger(__name__)


def upload_files_to_s3(file_name: str, bucket_name: str, s3_key_prefix: str) -> str:

    s3_client = boto3.client('s3')
    key = s3_key_prefix if s3_key_prefix else "/".join(file_name.split("/")[3:])
    s3_client.upload_file(file_name, bucket_name, key)
    return file_name


def run_uploader(parser_args):
    response = requests.get(parser_args.url)
    response.raise_for_status()

    file_names = []
    with TemporaryDirectory() as temp_dir:
        zip_file_path = os.path.join(temp_dir, "downloaded_file.zip")

        with open(zip_file_path, 'wb') as zip_file:
            zip_file.write(response.content)

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

            for filename in glob.iglob(f"{temp_dir}/**", recursive=True):
                if os.path.isfile(filename) and not zipfile.is_zipfile(filename):
                    file_names.append(filename)

            with concurrent.futures.ThreadPoolExecutor(max_workers=parser_args.concurrency) as executor:
                results = [executor.submit(
                    upload_files_to_s3,
                    file_name=file_name,
                    bucket_name=parser_args.bucket_name,
                    s3_key_prefix=parser_args.s3_key_prefix,
                ) for file_name in file_names]
                for result in concurrent.futures.as_completed(results):
                    if parser_args.verbose:
                        logger.info(result.result())
