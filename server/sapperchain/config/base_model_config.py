import argparse
from typing import List, Optional, Dict, Any

from typing import NamedTuple

class ModelConfigArgs(NamedTuple):
    api_key: str
    base_url: str
    uuid: str
    server_url: str
    model: str
    messages: list
    parse_path:list
    content_type: str
    authorization: str

class ModelConfig():
    def __init__(self,api_key):
        self.api_key = api_key
        self.base_url = "https://api.rcouyi.com/v1"
        self.uuid = "123456"
        self.server_url = "https://api.rcouyi.com/v1/chat/completions"
        self.model = "gpt-4o"
        self.messages = []
        self.tool_model_parse_path = ["choices",0,"delta","content"]
        self.mag_model_parse_path = ["choices", 0]
        self.content_type = "application/json"
        self.authorization = f"Bearer {api_key}"


#     def setup_tool_model_args(self) -> ModelConfigArgs:
#             parser = argparse.ArgumentParser(description='model setting')
#             parser.add_argument("--api_key", type=str, default="sk-pAauG9ss64pQW9FVA703F1453b334eFb95B7447b9083BaBd", help='Radius of cylinder')
#             parser.add_argument("--base_url", type=str, default="https://api.rcouyi.com/v1",help="")
#             parser.add_argument("--uuid",type=str,default="123456")
#             parser.add_argument("--server_url",type=str,default="https://api.rcouyi.com/v1/chat/completions")
#             parser.add_argument("--model",type=str, default="gpt-4o")
#             parser.add_argument("--messages",type=list,default=[])
#             parser.add_argument("--parse_path",type=list, default=["choices",0,"delta","content"])
#             parser.add_argument("--content_type",type=str,default='application/json')
#             parser.add_argument("--authorization",type=str,default=f"Bearer sk-pAauG9ss64pQW9FVA703F1453b334eFb95B7447b9083BaBd")
#             return ModelConfigArgs(**vars(parser.parse_args()))
#
#
#     def setup_mag_model_args(self) ->ModelConfigArgs:
#         parser = argparse.ArgumentParser(description='model setting')
#         parser.add_argument("--api_key", type=str, default="sk-pAauG9ss64pQW9FVA703F1453b334eFb95B7447b9083BaBd",
#                             help='Radius of cylinder')
#         parser.add_argument("--base_url", type=str, default="https://api.rcouyi.com/v1", help="")
#         parser.add_argument("--uuid", type=str, default="123456")
#         parser.add_argument("--server_url", type=str, default="https://api.rcouyi.com/v1/chat/completions")
#         parser.add_argument("--model", type=str, default="gpt-4o")
#         parser.add_argument("--messages", type=list, default=[])
#         parser.add_argument("--parse_path", type=list, default=["choices", 0])
#         parser.add_argument("--content_type", type=str, default='application/json')
#         parser.add_argument("--authorization", type=str,
#                             default=f"Bearer sk-pAauG9ss64pQW9FVA703F1453b334eFb95B7447b9083BaBd")
#         return ModelConfigArgs(**vars(parser.parse_args()))
#
# tool_model_args = setup_tool_model_args()
# mag_model_args = setup_mag_model_args()







