# Archive to S3 file uploader with concurrency support
## How to start the application

**The commands:**

First you have to install package:
```
$ pip install s3-zip-uploader-Ivan-Yukish
```

Then run the uploader:
```
$ python3 -m s3_zip_uploader_Ivan_Yukish https://example.com/path-to-archive bucket_example_name s3_key_prefix --concurrency 8 --verbose

```

## Application description

The uploader downloads an archive, extracts it and uploads every file to S3 in parallel.

Supported archive formats: `zip`, `tar`, `tar.gz` / `tgz`, `tar.bz2`, `tar.xz`.
The format is detected from the file content, so the URL doesn't need a file extension.

Each file is uploaded under its path inside the archive, e.g. `photos/a.jpg`.
If `s3_key_prefix` is set, it is prepended: `backup/photos/a.jpg`.

Before running app you should set up your AWS CLI account credentials: [docs](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).

## Running tests:
```
pytest
```

## File structure

Our file structure is:
```
├── s3_zip_uploader_Ivan_Yukish
│      ├── __main__.py
│      ├── uploader.py
├── tests
│      ├── test_arch.zip
│      ├── tests.py
├── .gitignore
├── config.py
├── conftest.py
├── LICENCE
├── pytest.ini
├── README.md
├── requirements.txt
├── setup.cfg
└── setup.py
```
