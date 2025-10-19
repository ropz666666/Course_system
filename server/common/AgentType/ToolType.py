from common.AgentProperties import Agent


class ToolAgent(Agent):
    def __init__(self,Name,Description,Model,Prompt,APIBase,AIChain,LongTerm_Memory,ShortTerm_Memory):
        super(ToolAgent, self).__init__(Name,Description,Model,Prompt,APIBase,AIChain,LongTerm_Memory,ShortTerm_Memory)
        self.AIChain = AIChain


