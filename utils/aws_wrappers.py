import os

import boto3


class S3:
    def __init__(self, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY):
        self.s3 = boto3.resource(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

    def put_object_to_s3(self, byte_data, bucket_name, folder_name, file_name):
        key_name = folder_name + '/' + file_name
        self.s3.Bucket(bucket_name).put_object(Key=key_name, Body=byte_data)

    def list_buckets_and_objects_in_s3(self):
        for bucket in self.s3.buckets.all():
            print(bucket.name)
            for obj in bucket.objects.all():
                print(obj.key)

    def list_objects_in_s3_bucket(self, bucket_name):
        for obj in self.s3.Bucket(bucket_name).objects.all():
            print(obj.key)

    def list_objects_in_s3_bucket_and_folder(self, bucket_name, folder_name):
        for obj in self.s3.Bucket(bucket_name).objects.filter(Prefix=f'{folder_name}/'):
            print(obj.key)

    def delete_object_in_s3_bucket(self, bucket_name, key_name):
        self.s3.Object(bucket_name, key_name).delete()

    def delete_objects_in_s3_bucket(self, bucket_name):
        self.s3.Bucket(bucket_name).objects.delete()

    def get_object_in_s3_bucket(self, bucket_name, key_name):
        print(self.s3.Object(bucket_name, key_name).get()['Body'].read())


# if __name__ == '__main__':
#     s3 = S3("AKIAXJRWZPQ4MIDRLQNS", "rQTxctXF/UIp0Viq1i8Myv3QChfPtsPvSJ2h7lxq")
    # data = open('README.md', 'rb')
    # s3.put_object_to_s3(data, "renforce-assets", "dev", "README.md")
    # s3.list_buckets_and_objects_in_s3()
    # s3.list_objects_in_s3_bucket("renforce-assets")
    # s3.list_objects_in_s3_bucket_and_folder("renforce-assets", "dev5")
    # s3.delete_object_in_s3_bucket("renforce-assets", "dev/README.md")
    # s3.delete_objects_in_s3_bucket("renforce-assets")
    # s3.get_object_in_s3_bucket("renforce-assets", "dev/README.md")
