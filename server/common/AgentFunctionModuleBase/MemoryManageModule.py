from ..Tool import ConvertTool,ReadTool
from abc import ABC,abstractmethod

class MemoryManager(ABC):
    def __init__(self, LongTerm_Memory, ShortTerm_Memory, ExternalAPIHandleUtility):
        self.LongTerm_Memory = LongTerm_Memory
        self.ShortTerm_Memory = ShortTerm_Memory
        self.ExternalAPIHandleUtility = ExternalAPIHandleUtility
    @abstractmethod
    def AddMessageIntoMemory(self,Message):
        pass

class MemoryManager_Compression(MemoryManager):
    def __init__(self,LongTerm_Memory,ShortTerm_Memory,ExternalAPIHandleUtility):
        super(MemoryManager_Compression, self).__init__(LongTerm_Memory, ShortTerm_Memory, ExternalAPIHandleUtility)

    def AddMessageIntoMemory(self,Message):
        if len(self.ShortTerm_Memory.ChatHistory) < self.ShortTerm_Memory.Memory_Depth:
            self.ShortTerm_Memory.ChatHistory.append(Message)
        else:
            Compress_Prompt = f"{self.ShortTerm_Memory.ChatHistory}\nPlease chat histories the above into one sentence."
            Compress_Message = [
                {"role": "system", "content": "You are a Helpful assistant"}, #这里需要换成SPL prompt
                {"role": "user", "content": Compress_Prompt},
            ]
            self.ExternalAPIHandleUtility.API.API_Parameter["messages"] = Compress_Message
            Compress_History = self.ExternalAPIHandleUtility.Run()
            self.ShortTerm_Memory.ChatHistory.clear()
            self.ShortTerm_Memory.ChatHistory.append(Compress_History)


class MemoryManager_Window(MemoryManager):
    def __init__(self,LongTerm_Memory,ShortTerm_Memory,ExternalAPIHandleUtility):
        super(MemoryManager_Window, self).__init__(LongTerm_Memory, ShortTerm_Memory, ExternalAPIHandleUtility)
        self.preference_prompt = '''ConvertTool.JSON2SPL(ReadTool.Read_Jsonfile("../Prompt/Memory/Longmemory.json"))'''
    def AddMessageIntoMemory(self,Message):
        if len(self.ShortTerm_Memory.ChatHistory) < self.ShortTerm_Memory.Memory_Depth:
            self.ShortTerm_Memory.ChatHistory.append(Message)
        else:
            if len(self.ShortTerm_Memory.ChatHistory) > self.LongTerm_Memory.Memory_Depth:
                ChatHistory = ""
                for item in self.ShortTerm_Memory.ChatHistory:
                    ChatHistory = ChatHistory + "Q:" + item.Request.Text + "\n" + "A:" + item.Response
                message = [
                    {"role": "system", "content": self.preference_prompt},
                    {"role": "user", "content": ChatHistory},
                ]

                self.ExternalAPIHandleUtility.API.API_Parameter["messages"] = message
                preference_response = self.ExternalAPIHandleUtility.Run()

                #注意下这里
                self.LongTerm_Memory.Preference = preference_response.strip()
            else:
                pass
            self.ShortTerm_Memory.ChatHistory.pop(0)



