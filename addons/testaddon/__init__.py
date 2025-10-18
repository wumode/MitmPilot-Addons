from mitmproxy import http

from app.addons import _AddonBase
from app.schemas import HookData
from app.schemas.types import HookEventType

from app.log import logger


class TestAddon(_AddonBase):
    addon_name = "Test Addon"
    addon_order = 1
    addon_version = "0.1.0"

    _enabled = False
    def init_addon(self, config: dict = None):
        logger.info("init TestAddon ...")
        if config:
            self._enabled = config.get('enabled')
        self.update_config({'enabled': self._enabled})
        self.save_data('data', {1:1, 2:2})

    def get_state(self) -> bool:
        """
        获取插件运行状态
        """
        return True

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
