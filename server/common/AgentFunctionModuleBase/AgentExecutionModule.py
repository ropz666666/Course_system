import asyncio
import logging
import os
import re
import time

import requests

from common.AgentProperties import Variable
from abc import ABC
from common.AgentProperties import Session
from common.Tool import ReadTool, ConvertTool
import json
from public_tech_lib.client import main,init

class AgentExecutor(ABC):
    def __init__(self, VariablesManager, UnitExecutor):
        self.VariablesManager = VariablesManager
        self.UnitExecutor = UnitExecutor

    def SaveVariablesInAgent(self, Partial_SplPrompts, VariablesSpace):
        for Partial_SplPrompt in Partial_SplPrompts:
            Variables = self.VariablesManager.ExtractVariableNames(str(Partial_SplPrompt))
            for Variable in Variables:
                VariableInfo = self.VariablesManager.GetVariableInfoFromDataRep(Variable)
                self.VariablesManager.SaveVariableInAgent(VariableInfo, VariablesSpace)
        VariableInfo = self.VariablesManager.GetVariableInfoFromDataRep("TemporaryVariable")
        self.VariablesManager.SaveVariableInAgent(VariableInfo, VariablesSpace)
        VariableInfo = self.VariablesManager.GetVariableInfoFromDataRep("UserRequest")
        self.VariablesManager.SaveVariableInAgent(VariableInfo, VariablesSpace)

    def AssignUserInputInfoIntoVariable(self, InputUserInfo, VariablesSpace):
        # 这里的UserRequest是怎么取名的
        if InputUserInfo.File_Path is not None:
            if os.path.splitext(InputUserInfo.File_Path)[1] == '.txt':
                # 使用requests获取URL内容
                response = requests.get(InputUserInfo.File_Path)
                # 确保请求成功
                if response.status_code == 200:
                    content = response.text
                    VariablesSpace["UserRequest"]["TrueValue"] = content
                else:
                    print("Failed to download the file, status code:", response.status_code)
            else:
                VariablesSpace["UserRequest"]["TrueValue"] = InputUserInfo.File_Path
        elif InputUserInfo.Text is not None:
            VariablesSpace["UserRequest"]["TrueValue"] = InputUserInfo.Text

    def judge_res_type(self, reference):
        result_type_mapping = {
            "Text": 'text',
            "Url": 'image',
            "Image_Binary_Data": 'image',
            "Speech_Binary_Data": 'speech',
            "Image_B64_Data": 'image',
            "Speech_B64_Data": 'speech'
        }
        res_type = "text"
        if reference["RefPackage"] in ["RefAPI", "NativeAPI"]:
            print(reference["RefProperties"])
            res_type = result_type_mapping.get(reference["RefProperties"]["Return_Info"]['return_value_type'])
        return res_type

    async def GetResFromAgent(self, Agent, Request):
        self.AssignUserInputInfoIntoVariable(Request, self.VariablesManager.DataBase)
        self.SaveVariablesInAgent(Agent.AIChain, Agent.ShortTerm_Memory.Variables)
        AIChainSplPrompt = Agent.AIChain
        yield "[progress]: 正在执行操作步骤，请耐心等待..."
        for index, Unit in enumerate(AIChainSplPrompt):
            # if index < len(AIChainSplPrompt) - 1:
            yield f"[progress]: 正在执行操作步骤 {index + 1}，请耐心等待..."
            response_type = self.judge_res_type(Unit["References"][-1])
            is_streaming = response_type == 'text' and ("rcouyi" in str(Unit["References"][-1]) or 'api/v1/sapper/agent/' in str(Unit["References"][-1]))
            print(is_streaming)
            response_stream = self.UnitExecutor.GetResFromUnit(Unit, stream=is_streaming)
            async for chunk in response_stream:
                chunk = f"{f'[{response_type}]: [点击查看](' if response_type != 'text' else ''}{chunk}{f')' if response_type != 'text' else ''}"
                print(chunk, end='')
                yield chunk


class ToolAgentExecutor(AgentExecutor):
    def __init__(self, AgentVariableinitialization, UnitExecutor):
        super(ToolAgentExecutor, self).__init__(AgentVariableinitialization, UnitExecutor)


class MagAgentExecutor(AgentExecutor):
    def __init__(self, RequestSplitter, APIDispatcher, VariablesManager, UnitExecutor, MemoryManager, chat_session):
        super(MagAgentExecutor, self).__init__(VariablesManager, UnitExecutor)
        self.RequestSplitter = RequestSplitter
        self.APIDispatcher = APIDispatcher
        self.MemoryManager = MemoryManager
        self.chat_session = chat_session

    def judge_res_type(self, reference):
        result_type_mapping = {
            "Text": 'text',
            "Url": 'image',
            "Image_Binary_Data": 'image',
            "Speech_Binary_Data": 'speech',
            "Image_B64_Data": 'image',
            "Speech_B64_Data": 'speech'
        }
        res_type = "text"
        if reference["RefPackage"] in ["RefAPI", "NativeAPI"]:
            res_type = result_type_mapping.get(reference["RefProperties"]["Return_Info"]['return_value_type'])
        return res_type

    async def GetResFromAgent(self, Agent, Request):
        print(Request.Text)
        logging.info(f"API_Base:{self.APIDispatcher.APIBase}")
        yield "[progress]: 思考中，请耐心等待..."
        async for res in main(self.chat_session,Request.Text, self.APIDispatcher.APIBase):
            yield res

    def AddUsageRecordIntoMemory(self, Session):
        self.MemoryManager.AddMessageIntoMemory(Session)


class APIDispatcher():
    def __init__(self, APIBase, ExternalAPIHandleUtility):
        self.APIBase = APIBase
        self.ExternalAPIHandleUtility = ExternalAPIHandleUtility
        self.base_path = os.path.dirname(__file__).replace('\\common', "").replace('/common', "").replace(
            "\\AgentFunctionModuleBase", "").replace("/AgentFunctionModuleBase", "")
        self.APIAssignmentPrompt = ReadTool.Read_Txtfile(
            self.base_path + "/app/service/Prompts/RequestAnalyze/Decompose.txt")

    async def AssignAPI(self, UserInstruction):
        API_Calls = ""

        for APIName, API in self.APIBase.items():
            API_Calls = API_Calls + "\n    " + "@Term " + API.API_Name + ": " + API.Description
        AnalyzePrompt = self.APIAssignmentPrompt.replace("{External_API}", API_Calls)
        Analyzemessage = [
            {"role": "system", "content": AnalyzePrompt},
            {"role": "user", "content": UserInstruction},
        ]
        print(f"Analyze_prompt:{AnalyzePrompt}")
        self.ExternalAPIHandleUtility.API.API_Parameter["messages"] = Analyzemessage
        AnalyzeResult = await self.ExternalAPIHandleUtility.Run()

        try:
            print(AnalyzeResult)
            AnalyzeJsonResult = json.loads(AnalyzeResult)

            return AnalyzeJsonResult["API_Call"]
        except Exception as e:
            return "None"


class RequestSplitter():
    def __init__(self, ExternalAPIHandleUtility):
        self.ExternalAPIHandleUtility = ExternalAPIHandleUtility
        self.base_path = os.path.dirname(__file__).replace('\\common', "").replace('/common', "").replace(
            "\\AgentFunctionModuleBase", "").replace("/AgentFunctionModuleBase", "")
        self.SplitPrompt = ReadTool.Read_Txtfile(
            self.base_path + "/app/service/Prompts/RequestAnalyze/Spilt.txt")

    async def SplitRequest(self, Request):
        # for _ in range(3):  # 尝试最多3次
        try:
            Decomposemessage = [
                {"role": "system", "content": self.SplitPrompt},
                {"role": "user", "content": Request.Text},
            ]
            self.ExternalAPIHandleUtility.API.API_Parameter["messages"] = Decomposemessage
            split_result = await self.ExternalAPIHandleUtility.Run()
            JsonDecomposedReuqest = json.loads(split_result)
        except Exception as e:
            JsonDecomposedReuqest = json.loads(f'''{"Context": {Request.Text}, "Instruction": {Request.Text}}''')
        return JsonDecomposedReuqest


class UnitExecutor:
    def __init__(self, Pre_PromptHandle, PromptHander, Post_PromptHandle):
        self.Pre_PromptHandle = Pre_PromptHandle
        self.PromptHander = PromptHander
        self.Post_PromptHandle = Post_PromptHandle

    async def GetResFromUnit(self, UnitInfo, stream=False):
        UnitStatements = UnitInfo["References"]
        print(f"unit_statements:{UnitStatements}")
        for index, UnitStatement in enumerate(UnitStatements):
            UnitStatement = self.Pre_PromptHandle.AssignVariableValueToUnit(UnitStatement)
            response_stream = await self.PromptHander.HandlePrompt(UnitStatement, stream)
            if stream and index == len(UnitStatements) -1:
                collected_parts = []
                async for chunk in response_stream:
                    print(chunk)
                    collected_parts.append(chunk)
                    yield chunk
                Res = ''.join(collected_parts)
            elif not stream and index == len(UnitStatements) -1:
                Res = response_stream
                yield Res
            else:
                Res = response_stream
            self.Post_PromptHandle.AssignResToOutputVariables(UnitStatement["RefOutput"], Res)


class Pre_PromptHandle():
    def __init__(self, IExtractVarables, VariablesSpace):
        self.IExtractVariables = IExtractVarables
        self.VariablesSpace = VariablesSpace

    def AssignVariableValueToUnit(self, UnitStatement):
        print(f"unit:{UnitStatement}")
        output_var = UnitStatement["RefOutput"]
        Temp = json.dumps(UnitStatement)
        Variables = self.IExtractVariables.ExtractVariables(Temp)
        for Variable in Variables:
            ReplaceTargetPattern = fr"\${{{Variable}}}\$(?:~\w+\{{[^}}]*\}})*(?:\/\w+)?"
            ReplaceTarget = sorted(list(set(re.findall(ReplaceTargetPattern, Temp))), key=len, reverse=True)
            for Target in ReplaceTarget:
                try:
                    if self.VariablesSpace[Variable].TrueValue != "":
                        # 使用JSON序列化来处理变量值
                        value_json = json.dumps(self.VariablesSpace[Variable].TrueValue)
                        # 去掉序列化字符串两端的引号
                        value_json_unquoted = value_json.strip('"')
                        # 替换目标字符串为处理过的变量值
                        Temp = Temp.replace(Target, value_json_unquoted)
                except Exception as e:
                    print("no value", e)
        UnitStatement = json.loads(Temp)
        UnitStatement["RefOutput"] = output_var
        return UnitStatement


class PromptHander():
    def __init__(self, RefProcessUtility):
        self.RefProcessUtility = RefProcessUtility

    async def HandlePrompt(self, UnitStatement, stream=False):
        RefAPIUtility = self.RefProcessUtility.SetRefUtility(UnitStatement)
        Res = await self.RefProcessUtility.ExcuteRef(RefAPIUtility, stream)
        return Res


class Post_PromptHandle():
    def __init__(self, VariablesSpace):
        self.VariablesSpace = VariablesSpace

    def AssignResToOutputVariables(self, VaribaleName, Res):
        OutputNamePattern = r"\$\{(.*?)\}\$"
        OutputVariableName = re.findall(OutputNamePattern, str(VaribaleName))[0]
        try:
            self.VariablesSpace[OutputVariableName].TrueValue = Res
        except:
            self.VariablesSpace[OutputVariableName] = {}


class VariablesManager():
    def __init__(self, DataBase, IExtractVariables):
        self.DataBase = DataBase
        self.IExtractVariables = IExtractVariables

    def ExtractVariableNames(self, Content):
        Variables = self.IExtractVariables.ExtractVariables(Content)
        return Variables

    def GetVariableInfoFromDataRep(self, VariableName):
        try:
            RefInfo = self.DataBase[VariableName]
        except Exception as e:
            print("Error occurred while fetching variable info:", e)
            RefInfo = {
                "Name": VariableName,
                "Usage": "Prompt",
                "DataType": "String",
                "TrueValue": "",
                "ShowValue": "",
                "References": []
            }
        return RefInfo

    def SaveVariableInAgent(self, VariableInfo, VariablesSpace):
        variable = Variable(VariableInfo["Name"],
                            VariableInfo["Usage"],
                            VariableInfo["DataType"],
                            VariableInfo["TrueValue"],
                            VariableInfo["ShowValue"],
                            VariableInfo["References"])
        VariablesSpace[VariableInfo["Name"]] = variable
        VariableLoc = VariablesSpace[VariableInfo["Name"]]
        return VariableLoc


class IExtractVariables():
    def __init__(self):
        self.pattern = r'\$\{(.*?)\}\$'

    def ExtractVariables(self, Content):
        Variables = set(re.findall(self.pattern, str(Content)))
        return list(Variables)
