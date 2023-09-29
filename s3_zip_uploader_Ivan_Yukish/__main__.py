import argparse
import logging

from . import uploader

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Upload files to S3 with concurrency')
    parser.add_argument('url', help='URL to the ZIP archive')
    parser.add_argument('bucket_name', help='S3 bucket name')
    parser.add_argument('s3_key_prefix', default="", help='S3 key prefix for uploaded files')
    parser.add_argument('--concurrency', type=int, default=8, help='Concurrency level')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    # Download the ZIP file from the provided URL
    upload_successfully = uploader.run_uploader(args)
    if args.verbose and not upload_successfully:
        logger.error("Uploader wasn't upload files successfully")

if __name__ == '__main__':
    main()
