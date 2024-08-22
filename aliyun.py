#!/usr/bin/env python3

import util

import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider


def init(ctx, env):
    region = env[util.SYNC_REGION]
    if not region.endswith(".aliyuncs.com"):
        region = region + ".aliyuncs.com"
    bucket = env[util.SYNC_BUCKET]
    env["OSS_ACCESS_KEY_ID"] = env[util.SYNC_ACCESS_ID]
    env["OSS_ACCESS_KEY_SECRET"] = env[util.SYNC_ACCESS_SECRET]
    auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())
    ctx["bucket"] = oss2.Bucket(auth, f"https://{region}", bucket)


def upload(ctx, env, objectKey, fpath, b64md5):
    bucket = ctx["bucket"]
    headers = {"Content-Type": util.guess_mime(objectKey), "Content-MD5": b64md5}
    bucket.put_object_from_file(objectKey, fpath, headers=headers)


def delete(ctx, env, objectKey):
    bucket = ctx["bucket"]
    bucket.delete_object(objectKey)


def list_all(ctx, env):
    bucket = ctx["bucket"]
    objs = []
    for obj in oss2.ObjectIterator(bucket):
        key = obj.key
        size = obj.size
        md5 = util.etag_to_md5(obj.etag)
        objs.append({"key": key, "size": size, "md5": md5})
    return objs
