#!/usr/bin/env python3

import boto3

import util


def init(ctx, env):
    """
    init R2 client using S3 SDK.
    """
    # get region
    region = env[util.SYNC_REGION]
    if not region.endswith(".r2.cloudflarestorage.com"):
        region = region + ".r2.cloudflarestorage.com"
    # get access keys from env:
    accessId = env[util.SYNC_ACCESS_ID]
    accessSecret = env[util.SYNC_ACCESS_SECRET]
    # build client:
    client = boto3.client("s3", aws_access_key_id=accessId, aws_secret_access_key=accessSecret, endpoint_url=f"https://{region}")
    # put client into ctx for later use:
    ctx["client"] = client


def upload(ctx, env, objectKey, fpath, b64md5):
    """
    upload a file to R2.
    """
    # get bucket from env:
    bucket = env[util.SYNC_BUCKET]
    # read file content as bytes:
    with open(fpath, "rb") as fp:
        body = fp.read()
    # call s3 put_object:
    ctx["client"].put_object(Bucket=bucket, Key=objectKey, Body=body, ContentType=util.guess_mime(objectKey), ContentMD5=b64md5)


def delete(ctx, env, objectKey):
    """
    delete a file from R2.
    """
    # get bucket from env:
    bucket = env[util.SYNC_BUCKET]
    # call s3 delete_object:
    ctx["client"].delete_object(Bucket=bucket, Key=objectKey)


def list_all(ctx, env):
    """
    list all objects from R2.
    """
    # get bucket from env:
    bucket = env[util.SYNC_BUCKET]
    # get s3 client from ctx:
    client = ctx["client"]
    # get all objects by pagination:
    isTruncated = True
    cToken = None
    objs = []
    while isTruncated:
        kw = dict(Bucket=bucket, MaxKeys=1000)
        if cToken:
            kw["ContinuationToken"] = cToken
        response = client.list_objects_v2(**kw)
        if "Contents" in response:
            contents = response["Contents"]
            for obj in contents:
                if not obj["Key"].endswith("/"):
                    md5 = util.etag_to_md5(obj["ETag"])
                    objs.append({"key": obj["Key"], "size": obj["Size"], "md5": md5})
        isTruncated = response["IsTruncated"]
        cToken = response.get("NextContinuationToken", None)
    return objs
