import os

from dotenv import load_dotenv
from volcenginesdkarkruntime import Ark

load_dotenv()

ark_client = Ark(base_url=os.getenv('ARK_BASE_URL'), api_key=os.getenv("ARK_API_KEY"), region=os.getenv("ARK_REGION"))
ark_model = os.getenv("ARK_MODEL_NAME")
