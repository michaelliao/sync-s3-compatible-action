#!/usr/bin/env python3

import util

from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials
from baidubce.services.bos.bos_client import BosClient


def init(ctx, env):
    region = env[util.SYNC_REGION]
    if not region.endswith(".bcebos.com"):
        region = region + ".bcebos.com"
    accessId = env[util.SYNC_ACCESS_ID]
    accessSecret = env[util.SYNC_ACCESS_SECRET]
    config = BceClientConfiguration(credentials=BceCredentials(accessId, accessSecret), endpoint=f"https://{region}")
    ctx["client"] = BosClient(config)


def upload(ctx, env, objectKey, fpath, b64md5):
    bucket = env[util.SYNC_BUCKET]
    headers = {"Content-Type": util.guess_mime(objectKey), "Content-MD5": b64md5}
    ctx["client"].put_object_from_file(bucket, objectKey, fpath, user_headers=headers)


def delete(ctx, env, objectKey):
    bucket = env[util.SYNC_BUCKET]
    ctx["client"].delete_object(bucket, objectKey)


def list_all(ctx, env):
    bucket = env[util.SYNC_BUCKET]
    client = ctx["client"]
    marker = None
    isTruncated = True
    objs = []
    while isTruncated:
        response = client.list_objects(bucket, marker=marker, max_keys=1000)
        if hasattr(response, "contents"):
            contents = response.contents
            for obj in contents:
                if not obj.key.endswith("/"):
                    md5 = util.etag_to_md5(obj.etag)
                    objs.append({"key": obj.key, "size": obj.size, "md5": md5})
        isTruncated = response.is_truncated
        marker = getattr(response, "next_marker", None)
    return objs
