from flow import Flow


class constructFlowEcho(Flow):
    """
    This will construct bash script to run Echo command
    """
    def constructor(self, data: dict) -> str:
        command = data.pop("command")
        output = data.pop("file")
        arg_string = " ".join(f"'{key} {val}'" for (key, val) in data.items())
        final_string = f"{command} {arg_string}  >>./{output}"
        return final_string
