#!/usr/bin/env python3

import util

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


def init(ctx, env):
    region = env[util.SYNC_REGION]
    accessId = env[util.SYNC_ACCESS_ID]
    accessSecret = env[util.SYNC_ACCESS_SECRET]
    config = CosConfig(Region=region, SecretId=accessId, SecretKey=accessSecret, Token=None)
    ctx["client"] = CosS3Client(config)


def upload(ctx, env, objectKey, fpath, b64md5):
    bucket = env[util.SYNC_BUCKET]
    ctx["client"].put_object_from_local_file(Bucket=bucket, Key=objectKey, LocalFilePath=fpath, ContentType=util.guess_mime(objectKey), ContentMD5=b64md5)


def delete(ctx, env, objectKey):
    bucket = env[util.SYNC_BUCKET]
    ctx["client"].delete_object(Bucket=bucket, Key=objectKey)


def list_all(ctx, env):
    bucket = env[util.SYNC_BUCKET]
    client = ctx["client"]
    marker = ""
    objs = []
    while True:
        resp = client.list_objects(Bucket=bucket, Marker=marker, MaxKeys=1000)
        if "Contents" in resp:
            contents = resp["Contents"]
            for obj in contents:
                if not obj["Key"].endswith("/"):
                    md5 = util.etag_to_md5(obj["ETag"])
                    objs.append({"key": obj["Key"], "size": int(obj["Size"]), "md5": md5})
        if resp["IsTruncated"] == "false":
            break
        else:
            marker = resp["NextMarker"]
    return objs
