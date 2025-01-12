"""methods related to the storage account"""

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta, UTC


class BlobStorageUrlBuilder:
    """builder for blob urls with sas token based on a file name.

    this is used by the app to convert the blob name from the database into a URL."""

    def __init__(self, blob_service_client: BlobServiceClient, container_name, timedelta=15):

        self._client = blob_service_client
        self._container_name = container_name
        self._container_client = self._client.get_container_client(container_name)
        self.timedelta = timedelta

    def get_url(self, blob_name):
        account_name = self._client.account_name
        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=self._container_client.container_name,
            blob_name=blob_name,
            account_key=self._client.credential.account_key,
            permission=BlobSasPermissions(read=True, write=True),
            expiry=datetime.now(UTC) + timedelta(minutes=self.timedelta),  # Short expiry time
        )

        blob_url = f"https://{account_name}.blob.core.windows.net/{self._container_name}/{blob_name}?{sas_token}"
        return blob_url

