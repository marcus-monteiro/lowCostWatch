import boto3
import gzip
from botocore.exceptions import ProfileNotFound

class S3Manager:
    def __init__(self, profile_name: str = None):
        self.profile_name = profile_name
        self.s3 = None
        self.bucket_name = ""

    def connect(self):
        """
        Cria uma sessão S3 a partir do profile_name.
        """
        session = boto3.Session(profile_name=self.profile_name)
        self.s3 = session.client('s3')

    def list_files(self, bucket_name: str, prefix: str):
        """
        Lista arquivos no bucket/prefix fornecidos.
        Retorna a lista de chaves (file keys).
        """
        self.bucket_name = bucket_name
        response = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if 'Contents' not in response:
            return []
        return [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.log.gz')]

    def download_and_decompress(self, file_key: str) -> str:
        """
        Faz o download de um arquivo .log.gz do S3 e retorna o conteúdo de texto descomprimido.
        """
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=file_key)
            compressed_content = response['Body'].read()
            return gzip.decompress(compressed_content).decode('utf-8')
        except Exception as e:
            print(f"Erro ao carregar {file_key}: {str(e)}")
            return ""