from abc import ABC, abstractmethod
import os

webcode = """
const socket = new WebSocket("<url>");

socket.addEventListener('open', () => {
    console.log('WebSocket Connected.');

    const request = {
        message: [{"role": "user", "content": "What can you help me?"}]
    };
    socket.send(JSON.stringify(request));
});

socket.addEventListener('message', (event) => {
    console.log('Received:', event.data);
});
"""
wechatCode = """
// Create a connection.
createSocketServer(){
    wx.connectSocket({ url: '<url>'})
    wx.onSocketOpen(()=>{
        wx.showToast({
          title: 'Server successfully connected!',
          icon: 'success'
      })
    })
    // Receive the response.
    wx.onSocketMessage((msg)=>{
        var response = msg.data;
    })
    wx.onSocketClose(()=>{
        wx.showToast({
            title: 'The connection to the server is closed.',
            icon: 'error'
        })
    })
    wx.onSocketError((err)=>{
        console.log('Error!',err);
    })
}

// Send the request.
handleSend(request){
    var send_request = JSON.stringify({
      message: [{role: "user", content: request}]
    });
    wx.sendSocketMessage({data: send_request})
}
"""

robotcode = """
import asyncio
import websockets
import json

async def clientLLMresponse()->str:
    connect = await websockets.connect("<url>")
    message = [{"role": "user", "content": "what can you do for me?"}]
    data = {"message": message}
    replayMessage = ""
    await connect.send(json.dumps(data))
    try:
        while True:
            response = await connect.recv()
            replayMessage += response
            if response == "__END_OF_RESPONSE__":
                break
            else:
                print(f"{response}")
        return replayMessage
    finally:
        await connect.close()


result = asyncio.run(clientLLMresponse())
result = result[:-len("__END_OF_RESPONSE__")]
print("result:" + result)
"""
class IClientCodeGen(ABC):
    def __init__(self, url="wss://www.jxselab.com:8000/ws/sapperchain/ClientLLMResponse") -> None:
        self.url = url

    @abstractmethod
    def gen_client_code(self, agentId):
        pass

    @staticmethod
    def get_code(name: str):
        base_path = os.path.dirname(__file__)  # 获取当前文件的目录
        # base_path = "/www/wwwroot/agentdy/app/services"
        # print("hdsadcsd")
        path = os.path.join(base_path, 'Prompts', 'ClientCodeGen', name)
        print(path)
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return "File not found."
        except Exception as e:
            return f"An error occurred: {e}"

class WeixinCodeGen(IClientCodeGen):
    def gen_client_code(self, agentId):
        # code_template = self.get_code("WeChat")  # 使用实例方法调用
        code_template = wechatCode
        GenUrl = self.url + "?agent_uuid=" + agentId
        code = code_template.replace("<url>", GenUrl).replace("<agentId>", agentId)
        return code

class WebCodeGen(IClientCodeGen):
    def gen_client_code(self, agentId):
        # code_template = self.get_code("Web")  # 使用实例方法调用
        code_template = webcode
        GenUrl = self.url + "?agent_uuid=" + agentId
        code = code_template.replace("<url>", GenUrl).replace("<agentId>", agentId)
        return code

class RobotCodeGen(IClientCodeGen):
    def gen_client_code(self, agentId):
        # code_template = self.get_code("Robot")  # 使用实例方法调用
        code_template = robotcode
        GenUrl = self.url + "?agent_uuid=" + agentId
        code = code_template.replace("<url>", GenUrl).replace("<agentId>", agentId)
        return code

class ClientCodeGen:
    @staticmethod
    def get_client_codegen(client_type):
        if client_type == "WeChat":
            return WeixinCodeGen()
        elif client_type == "Web":
            return WebCodeGen()
        elif client_type == "Robot":
            return RobotCodeGen()
        else:
            raise ValueError("Unknown client type")
