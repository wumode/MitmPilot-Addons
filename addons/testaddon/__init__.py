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
    addon_icon = "Bilibili_E.png"
    addon_author = "wumode"
    author_url = "https://github.com/wumode"

    _enabled: bool = False
    def init_addon(self, config: dict = None):
        logger.info("init TestAddon ...")
        if config:
            self._enabled = bool(config.get('enabled'))
        self.update_config({'enabled': self._enabled})
        self.save_data('data', {1:1, 2:2})
        logger.info(f"cache test: {self.cache_test()}")

    def get_state(self) -> bool:
        """
        获取插件运行状态
        """
        return self._enabled

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
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '启用插件',
                                        }
                                    }
                                ]
                            },
                        ]
                    },
                ]
            }
        ], {
            "enabled": False,
        }

    def get_page(self) -> list[dict] | None:
        """
        拼装插件详情页面，需要返回页面配置，同时附带数据
        插件详情页面使用Vuetify组件拼装，参考：https://vuetifyjs.com/
        :return: 页面配置（vuetify模式）或 None（vue模式）
        """
        pass

    def get_dashboard(
        self, key: str, **kwargs
    ) -> tuple[dict[str, Any], dict[str, Any], list[dict] | None] | None:
        """
        获取插件仪表盘页面，需要返回：1、仪表板col配置字典；2、全局配置（布局、自动刷新等）；3、仪表板页面元素配置含数据json（vuetify）或 None（vue模式）
        1、col配置参考：
        {
            "cols": 12, "md": 6
        }
        2、全局配置参考：
        {
            "refresh": 10, // 自动刷新时间，单位秒
            "border": True, // 是否显示边框，默认True，为False时取消组件边框和边距，由插件自行控制
            "title": "组件标题", // 组件标题，如有将显示该标题，否则显示插件名称
            "subtitle": "组件子标题", // 组件子标题，缺省时不展示子标题
        }
        3、vuetify模式页面配置使用Vuetify组件拼装，参考：https://vuetifyjs.com/；vue模式为None

        kwargs参数可获取的值：1、user_agent：浏览器UA

        :param key: 仪表盘key，根据指定的key返回相应的仪表盘数据
        """
        pass

    def get_dashboard_meta(self) -> list[dict[str, str]] | None:
        """
        获取插件仪表盘元信息
        返回示例：
            [{
                "key": "dashboard1", // 仪表盘的key，在当前插件范围唯一
                "name": "仪表盘1" // 仪表盘的名称
            }, {
                "key": "dashboard2",
                "name": "仪表盘2"
            }]
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
                func_kwargs={'param': "hello"}
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

    async def test_service(self, param: str):
        logger.info(f"{self.addon_name}-{yaml.dump({"param": param}, allow_unicode=True)}")

    @cached(maxsize=1, ttl=3600)
    def cache_test(self) -> str:
        return "cache string"
