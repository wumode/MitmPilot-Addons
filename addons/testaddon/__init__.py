import yaml
from typing import Any
from mitmproxy import http

from app.addons import _AddonBase
from app.schemas import HookData, AddonService, AddonApi
from app.schemas.types import HookEventType
from app.log import logger
from app.core.cache import cached


class TestAddon(_AddonBase):
    addon_name = "Test Addon"
    addon_order = 1
    addon_version = "0.1.1"

    _enabled = False
    def init_addon(self, config: dict = None):
        logger.info("init TestAddon ...")
        if config:
            self._enabled = config.get('enabled')
        self.update_config({'enabled': self._enabled})
        self.save_data('data', {1:1, 2:2})
        logger.info(f"cache test: {self.cache_test()}")

    def get_state(self) -> bool:
        """
        获取插件运行状态
        """
        return True

    @staticmethod
    def get_render_mode() -> tuple[str, str | None]:
        """
        获取插件渲染模式
        :return: 1、渲染模式，支持：vue/vuetify，默认vuetify；2、vue模式下编译后文件的相对路径，默认为`dist/asserts`，vuetify模式下为None
        """
        return "vuetify", None

    def get_api(self) -> list[AddonApi]:
        """
        注册插件API
        """
        pass

    def get_form(self) -> tuple[list[dict] | None, dict[str, Any]]:
        """
        拼装插件配置页面，插件配置页面使用Vuetify组件拼装，参考：https://vuetifyjs.com/
        :return: 1、页面配置（vuetify模式）或 None（vue模式）；2、默认数据结构
        """
        pass

    def get_page(self) -> list[dict] | None:
        """
        拼装插件详情页面，需要返回页面配置，同时附带数据
        插件详情页面使用Vuetify组件拼装，参考：https://vuetifyjs.com/
        :return: 页面配置（vuetify模式）或 None（vue模式）
        """
        pass

    def get_service(self) -> list[AddonService]:
        """
        注册插件公共服务
        """
        return [
            AddonService(
                id=f'{self.__class__.__name__}.{self.test_service.__name__}',
                name=f"{self.test_service.__name__}",
                trigger="cron",
                func=self.test_service,
                kwargs={'minute':'*'},
                func_kwargs={'p': "hello"}
            )
        ]

    def get_hooks(self) -> dict[HookEventType, list[HookData]]:
        return {
            HookEventType.request: [
                HookData(
                    condition_string='DOMAIN-SUFFIX,misskey-hub.net',
                    func=self.handle_misskey_request,
                )
            ],
            HookEventType.response: [
                HookData(
                    condition_string='DOMAIN-SUFFIX,misskey-hub.net',
                    func=self.misskey_response,
                )
            ]
        }

    def handle_misskey_request(self, flow: http.HTTPFlow):
        logger.info(f"{self.addon_name} {flow.request.pretty_host}")
        print(flow.request.pretty_host)

    async def misskey_response(self, flow: http.HTTPFlow):
        logger.info(f"{self.addon_name} {flow.request.pretty_host} async")

    async def test_service(self, p: str):
        logger.info(f"{self.addon_name}: {p}")

    @cached(maxsize=1, ttl=3600)
    def cache_test(self) -> str:
        return "cache string"
