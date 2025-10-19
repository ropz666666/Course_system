from common.AgentProperties import Agent


class MagAgent(Agent):
    def __init__(self,Name,Description,Model,Prompt,APIBase,AIChain,LongTerm_Memory,ShortTerm_Memory):
        super(MagAgent, self).__init__(Name,Description,Model,Prompt,APIBase,AIChain,LongTerm_Memory, ShortTerm_Memory)
