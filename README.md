# Sync S3-Compatible Action

The `sync-s3-compatible-action` is a GitHub action which can sync a directory to an S3-compatible storage. Currently supports:

- AWS S3
- CloudFlare R2
- Aliyun OSS
- QCloud COS
- Baidu Cloud BOS

## Environment Variables

The `sync-s3-compatible-action` takes the following environment variables as inputs:

| Name               | Default Value | Required | Description                   |
|--------------------|---------------|----------|-------------------------------|
| SYNC_DIR           | `_site`       | No       | Source directory to sync      |
| SYNC_TYPE          | `aws`         | No       | Cloud storage provider        |
| SYNC_BUCKET        |               | Yes      | Bucket name.                  |
| SYNC_REGION        |               | Yes      | Region name.                  |
| SYNC_ACCESS_ID     |               | Yes      | Access id for API access.     |
| SYNC_ACCESS_SECRET |               | Yes      | Aceess secret for API access. |
| SYNC_OPT_UNUSED    | `keep`        | No       | How to process files exist on cloud storage but not exist in local. |

## Notes

- `SYNC_ACCESS_SECRET` and `SYNC_ACCESS_SECRET` are confidential and should NOT be public. Add these values as [encrypted secrets](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions) and pass the secrets as inputs.
- Files which exist on cloud storage but not exist in local directory will be keeped by default. To remove unused files you must set `SYNC_OPT_UNUSED` to `delete` explicitly.
- Default value of `SYNC_DIR` is `_site`, which is useful to sync generated GitHub page to cloud storage.

## Example

An example of GitHub action shows how to generate GitHub pages and sync `_site` to AWS S3:

```yaml
# build-and-sync.yml
name: Build static site and sync to cloud storage.

on:
  push:
    branches: [$default-branch]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Ruby
        uses: ruby/setup-ruby@8575951200e472d5f2d95c625da0c7bec8217c42 # v1.161.0
        with:
          ruby-version: '3.1'
          bundler-cache: true
          cache-version: 0
      - name: Build with Jekyll
        # Outputs to the './_site' directory by default
        run: bundle exec jekyll build --baseurl "${{ steps.pages.outputs.base_path }}"
        env:
          JEKYLL_ENV: production
      - name: Sync to Cloud Storage
        uses: michaelliao/sync-s3-compatible-action@v1
        env:
          SYNC_OPT_UNUSED: delete # force delete unused files on cloud storage:
          SYNC_DIR: _site # '_site' is default value
          SYNC_TYPE: aws
          # bucket must be created in region:
          SYNC_REGION: us-west-1
          SYNC_BUCKET: gh-s3-sync-action-example
          # set at: Settings - Secrets and variables - Actions - Repository secrets:
          SYNC_ACCESS_ID: ${{ secrets.SYNC_ACCESS_ID }}
          SYNC_ACCESS_SECRET: ${{ secrets.SYNC_ACCESS_SECRET }}
```

## Configurations

### AWS

AWS regions can be found on [this page](https://docs.aws.amazon.com/general/latest/gr/s3.html):

![AWS](aws.png)

### CloudFlare

The region of CloudFlare R2 must be set to your account id which can be found on R2 page:

![CloudFlare](cloudflare.png)

### Aliyun

Aliyun regions can be found on [this page](https://help.aliyun.com/document_detail/40654.html):

![Aliyun](aliyun.png)

### QCloud

The region of QCloud bucket can be found in bucket list page:

![QCloud](qcloud.png)

### Baidu Cloud

Baidu cloud regions can be found on [this page](https://cloud.baidu.com/doc/BOS/s/akrqd2wcx):

![Baidu Cloud](baidu.png)
