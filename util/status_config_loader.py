import yaml
import os
from pathlib import Path
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()

def load_config():
    env = os.getenv("env", "local")
    BASE_DIR = Path(__file__).resolve().parent.parent
    config_path = Path(f"{BASE_DIR}/config/{env}.yaml")

    if not config_path.exists():
        raise FileNotFoundError(f"{config_path} not found")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.load(f, Loader=yaml.SafeLoader)

CONFIG = load_config()
