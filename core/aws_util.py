import boto3

def get_aws_profiles():
    """
    Retorna a lista de profiles disponíveis na configuração AWS do usuário,
    ou ['default'] caso não encontre nenhum.
    """
    try:
        session = boto3.Session()
        return session.available_profiles
    except Exception:
        return ['default']