from collections import OrderedDict
from typing import Any


class Setting(object):

    def __init__(self):
        self._configuration: OrderedDict = OrderedDict({})
        self.run_loaders()

    def get_loaders(self) -> list:
        import re
        from inspect import getmembers, isroutine

        from server import config

        mod_routines = getmembers(config, isroutine)
        routine_names = [routine[0] for routine in mod_routines]
        ungrouped_loader = list(filter(lambda m: m != '', [(
            re.match(r'^_load_[a-zA-Z0-9_]*', name) or "") for name in routine_names]))
        loaders = list(map(lambda x: x.group(), ungrouped_loader))
        return loaders

    def get(self, k: str) -> Any:
        return self.configuration.get(k)

    @property
    def configuration(self) -> OrderedDict:
        return self._configuration

    def update_configuration(self, value: OrderedDict) -> None:
        if isinstance(value, dict):
            value = OrderedDict(value)
        self._configuration.update(value)

    def run_loaders(self) -> None:
        from server import config

        loaders = self.get_loaders()
        for loader in loaders:
            loader_result = getattr(config, loader)()
            self.update_configuration(OrderedDict(loader_result))
