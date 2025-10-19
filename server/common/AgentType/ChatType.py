from ...common.AgentProperties import Agent


class ChatAgent(Agent):
    def __init__(self,Model,Name,Description,Prompt,API_Call,LongMemory,ShortMemory):
        super(ChatAgent, self).__init__(Model,Name,Description,Prompt,API_Call)
        self.LongMemory = LongMemory
        self.ShortMemory = ShortMemory
