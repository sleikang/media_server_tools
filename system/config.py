import yaml
from system.log import log
import os


class config:
    path = None
    configdata = None
    defaultconfig = None
    apidata = None
    systemdata = None

    def __init__(self, path: str) -> None:
        try:
            # 打开文件
            self.defaultconfig = yaml.load(
                open("config.default.yaml", "r", encoding="utf-8"),
                Loader=yaml.FullLoader,
            )
            self.path = path
            self.configdata = yaml.load(
                open(self.path, "r", encoding="utf-8"), Loader=yaml.FullLoader
            )

            # 递归检查配置文件是否包含默认配置文件的所有配置项
            for key in self.defaultconfig:
                self.__config_check__(self.configdata, key, self.defaultconfig[key])

            self.systemdata = self.configdata["system"]
            self.apidata = self.configdata["api"]

        except Exception as result:
            log().info("配置异常错误, {}".format(result))

    def __config_check__(self, config, key, defaultvalue):
        try:
            if key not in config:
                log().info("配置项[{}]不存在, 创建默认值[{}]".format(key, defaultvalue))
                config[key] = defaultvalue
                with open(file=self.path, mode="w", encoding="utf-8") as file:
                    yaml.safe_dump(
                        self.configdata,
                        file,
                        default_flow_style=False,
                        allow_unicode=True,
                    )
            if isinstance(defaultvalue, dict):
                for subkey in defaultvalue:
                    self.__config_check__(config[key], subkey, defaultvalue[subkey])

        except Exception as result:
            log().info("配置异常错误, {}".format(result))
