import boto3
import pytest


class TestMoto:

    def test_s3(self, s3_client):
        # resp = s3_client.list_objects_v2(Bucket='bucket')
        resp = s3_client.list_buckets()

    def test_ddb(self, ddb_client):
        ddb_client.list_tables()
        breakpoint()