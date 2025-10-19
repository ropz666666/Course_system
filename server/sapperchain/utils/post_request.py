import httpx
from httpx import Timeout, AsyncClient
import json
from sapperchain.data_model.unit import Statement

timeout = Timeout(30.0, read=30.0)
import requests
import shutil
from functools import reduce
import tempfile


class IPostRequest:
    @staticmethod
    async def post_request(statement: Statement):
        if statement.input.stream:
            try:
                API_URL = statement.input.server_url
                headers = {
                    "Content-Type": statement.input.content_type,
                    "Authorization": statement.input.authorization
                }
                data = None
                if headers["Content-Type"] == "application/json":
                    data = statement.input.api_parameter.copy()
                    data['stream'] = True
                    data = json.dumps(data, ensure_ascii=False)
                async with httpx.AsyncClient(timeout=timeout) as client:
                    async with client.stream("POST", API_URL, headers=headers, data=data) as response:
                        async for part in response.aiter_lines():
                            if part and not part.isspace():
                                part_str = part
                                if part_str.startswith('data: '):
                                    part_str = part_str[6:]
                                    if part_str == '[DONE]':
                                        break
                                    try:
                                        decoded_part = json.loads(part_str)
                                        result = decoded_part

                                        result = reduce(lambda d, k: d[k], statement.input.parse_path,result)
                                        if result:
                                            yield result
                                    except Exception as e:
                                        print(e)
                                else:
                                    print('part', part)
                                    pass
            except Exception as e:
                # 异常处理应根据具体情况来定
                print(e)

        else:
            API_URL = statement.input.server_url
            data = None
            # =============输入处理================
            if statement.input.content_type == "application/json":
                data = statement.input.api_parameter
            # ========发送请求===================
            headers = {
                "Content-Type": statement.input.content_type,
                "Authorization": statement.input.authorization
            }
            # async with AsyncClient(timeout=timeout) as client:
            async with AsyncClient(timeout=timeout) as client:
                response = await client.post(API_URL, headers=headers, content=json.dumps(data))
                result = response.json()
                parsed_result = reduce(lambda d, k: d[k], statement.input.parse_path, result)
                # ======处理======
                if statement.input.return_value_type == "Text":
                    yield parsed_result
                elif statement.input.return_value_type == "Url":
                    yield parsed_result
                elif statement.input.return_value_type == "Speech_Url":
                    with requests.get(parsed_result, stream=True) as r:
                        r.raise_for_status()
                        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                            with open(temp_file.name, 'wb') as f:
                                shutil.copyfileobj(r.raw, f)
                    yield temp_file.name
