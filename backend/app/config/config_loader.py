
from pathlib import Path
import yaml
def load_yaml_configs(
        config_dir: Path
) -> dict:
    """
    加载指定目录下所有yaml配置文件

    config_dir:
        yaml文件所在目录

    return:
        合并后的配置字典
    """
    configs = {}

    for file in config_dir.glob("*.yaml"):

        with open(file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data:
            configs.update(data)
    return configs


