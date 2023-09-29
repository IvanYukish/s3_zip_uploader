# Zip to S3 file uploader with concurrency support
## How to start the application

**The commands:**

First you have to install package:
```
$ pip install s3-zip-uploader-Ivan-Yukish
```

Then run the uploader:
```
$ python3 -m s3_zip_uploader_Ivan_Yukish https://example.com/path-to-zip-archive bucket_example_name s3_key_prefix --concurrency 8 --verbose

```

## Application description

Before running app you should set up your AWS CLI account credentials: [docs](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).

## Running tests:
```
pytest
```

## File structure

Our file structure is:
```
├── s3_zip_uploader_Ivan_Yukish
│      ├── __init__.py
│      ├── main.py
│      ├── uploader.py
├── tests
│      ├── fixtures.py
│      ├── tests.py
├── .gitignore
├── LICENCE
├── pytest.ini
├── README.md
├── requirements.txt
└── setup.py
```
