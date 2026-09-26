import concurrent.futures
import logging
import os
import tarfile
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import boto3
import requests

logger = logging.getLogger(__name__)


class UnsupportedArchiveError(Exception):
    pass


def extract_archive(archive_path: str, dest_dir: str) -> None:
    # Detect the format by content, so URLs without a file extension work too.
    # tarfile's default "r:*" mode handles plain, gzip, bzip2 and xz tarballs.
    if zipfile.is_zipfile(archive_path):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(dest_dir)
    elif tarfile.is_tarfile(archive_path):
        with tarfile.open(archive_path) as tar_ref:
            _safe_extract_tar(tar_ref, dest_dir)
    else:
        raise UnsupportedArchiveError(
            "Unsupported archive format, expected zip, tar, tar.gz, tar.bz2 or tar.xz"
        )


def _safe_extract_tar(tar_ref: tarfile.TarFile, dest_dir: str) -> None:
    if hasattr(tarfile, "data_filter"):
        tar_ref.extractall(dest_dir, filter="data")
        return

    # Fallback for Python versions without extraction filters (PEP 706)
    dest_dir = os.path.realpath(dest_dir)
    members = []
    for member in tar_ref.getmembers():
        target = os.path.realpath(os.path.join(dest_dir, member.name))
        if os.path.commonpath([dest_dir, target]) != dest_dir:
            raise UnsupportedArchiveError(f"Archive member escapes target directory: {member.name}")
        if member.isfile() or member.isdir():
            members.append(member)
    tar_ref.extractall(dest_dir, members=members)


def build_s3_key(file_name: str, base_dir: str, s3_key_prefix: str) -> str:
    relative_path = Path(file_name).relative_to(base_dir).as_posix()
    if not s3_key_prefix:
        return relative_path
    return f"{s3_key_prefix.rstrip('/')}/{relative_path}"


def collect_files(base_dir: str) -> List[str]:
    return sorted(str(path) for path in Path(base_dir).rglob("*") if path.is_file())


def upload_files_to_s3(file_name: str, bucket_name: str, key: str) -> str:

    s3_client = boto3.client('s3')
    s3_client.upload_file(file_name, bucket_name, key)
    return file_name


def run_uploader(parser_args):
    try:
        response = requests.get(parser_args.url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(e)
        return False

    with TemporaryDirectory() as temp_dir:
        archive_path = os.path.join(temp_dir, "downloaded_archive")
        extract_dir = os.path.join(temp_dir, "extracted")

        with open(archive_path, 'wb') as archive_file:
            archive_file.write(response.content)

        try:
            extract_archive(archive_path, extract_dir)
        except (UnsupportedArchiveError, zipfile.BadZipFile, tarfile.TarError) as e:
            logger.error(e)
            return False

        file_names = collect_files(extract_dir)

        with concurrent.futures.ThreadPoolExecutor(max_workers=parser_args.concurrency) as executor:
            results = [executor.submit(
                upload_files_to_s3,
                file_name=file_name,
                bucket_name=parser_args.bucket_name,
                key=build_s3_key(file_name, extract_dir, parser_args.s3_key_prefix),
            ) for file_name in file_names]
            for result in concurrent.futures.as_completed(results):
                if parser_args.verbose:
                    logger.info(result.result())
    return True
