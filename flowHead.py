from flow import Flow


class constructFlowHead(Flow):
    """
    This will construct bash script to run Head command
    """
    def constructor(self, data: dict) -> str:
        command = data.pop("command")
        input_file = data.pop("file")
        arg_dict = {"-n": data.pop("number")}
        arg_string = " ".join(f"{key} {val}" for (key, val) in arg_dict.items())
        final_string = f"{command} {arg_string} {input_file}"
        return final_string
