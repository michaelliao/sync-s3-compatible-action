#!/usr/bin/env python3

import os, json, base64, hashlib, shutil, zipfile, subprocess

ENV_BUCKET = 'bucket'
ENV_REGION = 'region'
ENV_ACCESS_KEY_ID = 'access_key_id'
ENV_ACCESS_KEY_SECRET = 'access_key_secret'

META_MD5_KEY = 'x-meta-md5'

def file_md5(fpath: str) -> str:
    md5 = hashlib.md5()
    with open(fpath, "rb") as fp:
        md5.update(fp.read())
    return base64.b64encode(md5.digest()).decode("utf-8")
