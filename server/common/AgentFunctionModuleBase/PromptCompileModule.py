import copy
from collections import deque
import re
import json
from common.Tool import ConvertTool


class PromptCompiler:
    def __init__(self,SplPromptTranslator):
        self.SplPromptTranslator = SplPromptTranslator

    def Compile(self, Partial_SplPrompts):
        UnitChain = []
        Units = self.DecomposeByInstructionType(Partial_SplPrompts)
        for unit in Units:
            Instruction = [section for section in unit if section.get("sectionType") == "Instruction"][0]
            OutputStatement = [section for section in Instruction["section"] if section.get("subSectionType") == "OutputVariable"][0]["content"]
            InputStatement = [section for section in Instruction["section"] if section.get("subSectionType") == "InputVariable"][0]["content"]

            #Unit中可能有多条需要翻译的Statement
            StandardizedUnitStatements = self.TranslateSplPrompt(unit)
            UnitChain.append({
                "Input": InputStatement,
                "Output": OutputStatement,
                "References": copy.deepcopy(StandardizedUnitStatements),
                "SourcePartial_SplPrompts": unit
            })
        return deque(UnitChain)

    @staticmethod
    def DecomposeByInstructionType(Partial_SplPrompts):
        temp = []
        Partial_SplPrompt_Instructions = [section for section in Partial_SplPrompts if section.get("sectionType") == "Instruction"]
        OtherSplPromptProperties = [section for section in Partial_SplPrompts if section.get("sectionType") != "Instruction"]

        for instruction in Partial_SplPrompt_Instructions:
            if "refAPI" in json.dumps(instruction):
                temp.append([instruction])
            else:
                OtherSplPromptProperties.append(instruction)
                temp.append(OtherSplPromptProperties)
                OtherSplPromptProperties = [section for section in Partial_SplPrompts if
                                            section.get("sectionType") != "Instruction"]
        return temp

    def DecomposeByAPI(self, Partial_SplPrompts):
        pass

    def TranslateSplPrompt(self, Partial_SplPrompt):
        StandardizedUnitStatements = self.SplPromptTranslator.spl_translate(Partial_SplPrompt)
        return StandardizedUnitStatements


class SplPromptTranslator:
    def __init__(self,StringStatementMatcher, VariableMatcher, RefMatcher, RefStandardizationDevice):
        self.statement_matcher = StringStatementMatcher
        self.VariableMatcher = VariableMatcher
        self.RefMatcher = RefMatcher
        self.RefStandardizationDevice = RefStandardizationDevice

    def spl_translate(self, Partial_SplPrompts):
        standard_statements = []
        # 采用集合保持唯一
        variables = set()
        # spl unit 中每一个子模块中匹配翻译ref语句
        for partial_spl in Partial_SplPrompts:
            # 从partial_spl 中匹配出 ~ref 语句，包括refAPI, refData, ref...
            partial_spl_token = SplPromptTranslator.spl_split(json.dumps(partial_spl))
            is_native_api_flag = False
            if partial_spl.get("sectionType") == "Instruction":
                is_native_api_flag = True
            for token in partial_spl_token:
                if token[0] == 'var':
                    # ${var}$
                    variables.add(token[1])
                elif token[0] == 'refAPI':
                    is_native_api_flag = False
                    ref_statement = self.RefStandardizationDevice.standardize_ref(token[1])
                    Output = [section for section in partial_spl["section"] if
                              section.get("subSectionType") == "OutputVariable"][0]
                    ref_statement["RefOutput"] = Output["content"]
                    standard_statements.append(ref_statement)
                elif token[0] == 'refData':
                    ref_statement = self.RefStandardizationDevice.standardize_ref(token[1])
                    if ref_statement["RefOutput"] is None:
                        variables.add(ref_statement["RefOutput"])

                    standard_statements.append(ref_statement)

            if is_native_api_flag:
                Input = [section for section in partial_spl["section"] if
                         section.get("subSectionType") == "InputVariable"][0]
                Output = [section for section in partial_spl["section"] if
                          section.get("subSectionType") == "OutputVariable"][0]
                NativeAPI = self.RefStandardizationDevice.RefTools["NativeAPI"]
                NativeAPI.API_Parameter["messages"][0]["content"] = ConvertTool.JSON2SPL(Partial_SplPrompts)
                NativeAPI.API_Parameter["messages"][1]["content"] = Input["content"]
                StandardizedStatement = {
                    "RefPackage": "NativeAPI",
                    "RefMethod": NativeAPI.API_Name,
                    "RefProperties": {
                        "Name": NativeAPI.API_Name,
                        "Description": NativeAPI.Description,
                        "Server_Url": NativeAPI.Server_Url,
                        "Header_Info": NativeAPI.Header_Info,
                        "Return_Info": NativeAPI.Return_Info,
                        "API_Parameter": NativeAPI.API_Parameter
                    },
                    "RefOutput": Output["content"]
                }
                standard_statements.append(StandardizedStatement)

        return standard_statements

    @staticmethod
    def spl_split(spl):
        pattern = r'(\~refData\{.*?\}.*?\/refData|\~refAPI\{.*?\}.*?\/refAPI|\$\{.*?\}\$)'
        parts = re.split(pattern, spl)

        result = []
        for part in parts:
            if re.match(r'\~refData\{.*?\}.*?\/refData', part):
                result.append(('refData', part))
            elif re.match(r'\~refAPI\{.*?\}.*?\/refAPI', part):
                result.append(('refAPI', part))
            elif re.match(r'\$\{.*?\}\$', part):
                result.append(('var', part))
            else:
                result.append(('text', part))

        return result

class RefMatcher():
    def __init__(self):
        self.Pattern = r'~(ref(?:API|Data|Check|Guardrail)){(.*?)}/\1'

    def MatchRefs(self, StringStatement):
        StringRef = re.search(self.Pattern, StringStatement)[0]
        return StringRef

class VariableMatcher():
    def __init__(self):
        self.Pattern = r'\$\{(.*?)\}\$~ref'

    def MatchVariable(self, StringStatement):

        StringVariable = re.findall(self.Pattern, StringStatement)
        if StringVariable !=[]:
            return "${"+StringVariable[0]+"}$"
        return ""

class StatementMatcher():
    def __init__(self):
        self.Pattern = r"(?:\$\{\w+\}\$)?(?:~\w+{[^{}]*}{(?:[^\/]+)}/\w+)+"

    def MatchStatements(self, Partial_SplPrompt):
        StringStatements = re.findall(self.Pattern, str(Partial_SplPrompt))
        return StringStatements


class RefStandardizeDevice:
    def __init__(self, RefTools):
        self.RefTools = RefTools

    def standardize_ref(self, StringRef):
        if "~refAPI" in StringRef:
            # 匹配 ~refAPI{...} 的正则表达式
            pattern = r'\~refAPI\{(.*?)\}\[(.*?)\]\[(.*?)\]/refAPI'
            match = re.match(pattern, StringRef)

            if not match:
                raise ValueError("The input text does not match the required pattern", StringRef)

            api_uuid, api_param_str, ref_output = match.groups()

            if api_uuid not in self.RefTools["APIBase"]:
                raise ValueError("API UUID not found in RefTools, api: ", api_uuid, self.RefTools["APIBase"].keys())

            API = self.RefTools["APIBase"][api_uuid]
            api_param_str = api_param_str.replace("\\", "")
            APIParameter = json.loads(api_param_str)
            Ref = {
                "RefPackage": "RefAPI",
                "RefMethod": API.API_Name,
                "RefProperties": {
                    "Name": API.API_Name,
                    "Description": API.Description,
                    "Server_Url": API.Server_Url,
                    "Header_Info": API.Header_Info,
                    "Return_Info": API.Return_Info,
                    "API_Parameter": APIParameter
                },
                "RefOutput": ref_output
            }
            return Ref

        elif "~refData" in StringRef:
            # 匹配 ~refData{...} 的正则表达式
            pattern = r'\~refData\{(.*?)\}\[(.*?)\]\[(.*?)\]/refData'
            match = re.match(pattern, StringRef)

            if not match:
                raise ValueError("The input text does not match the required pattern", StringRef)

            data_source, ref_input, ref_output = match.groups()

            if ref_output == "":
                # ref_output = "${" + data_source + "}$"
                ref_output = str(data_source)
            Ref = {
                "RefPackage": "RefData",
                "RefMethod": "Search",
                "RefProperties": {
                    "data_source": data_source,
                    "search_query": ref_input
                },
                "RefOutput": ref_output
            }
            return Ref

        elif "~refGuardrail" in StringRef:
            RefGuardrailTypeParttern = r'~refGuardrail{(.*?)}'
            RefGuardrailTypeName = re.findall(RefGuardrailTypeParttern, StringRef)[0]
            Ref = {
                "RefPackage": "RefGuardrail",
                "RefMethod" : RefGuardrailTypeName,
                "RefProperties": {}
            }
            return Ref
        elif "~refCheck" in StringRef:
            RefCheckTypeParttern = r'~RefCheck{(.*?)}'
            RefCheckTypeName = re.findall(RefCheckTypeParttern, StringRef)[0]
            Ref = {
                "RefPackage": "RefCheck",
                "RefMethod": RefCheckTypeName,
                "RefProperties": {}
            }
            return Ref
        else:
            pass
