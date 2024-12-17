from pytest import mark

from storages.backends.s3boto3 import S3Boto3Storage

from backends.storages import PublicStaticStorage, PublicMediaStorage


@mark.parametrize("storage", [PublicStaticStorage, PublicMediaStorage])
def test__public_sttorage__is_subclass_of_s3boto3(storage):
    assert issubclass(storage, S3Boto3Storage)


@mark.parametrize("cls", [PublicStaticStorage, PublicMediaStorage])
def test__public_sttorage__is_instance_s3boto3(cls):
    assert isinstance(cls(), S3Boto3Storage)
