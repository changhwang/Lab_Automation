from .device import Device

class UtilityCommands(Device):
    def __init__(self, name: str):
        super().__init__(name)

    def get_init_args(self) -> dict:
        return {"name": self._name}
    
    def update_init_args(self, args_dict: dict):
        self._name = args_dict["name"]