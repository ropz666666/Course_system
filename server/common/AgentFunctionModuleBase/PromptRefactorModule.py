class PromptRefactorer:
    def __init__(self,DecomposeUtility):
        self.DecomposeUtility = DecomposeUtility
    async def RefactorPrompt(self,Partial_SplPrompts):
        #这里是刘那边的五步，五个步骤对应相应的函数
        async for response in self.DecomposeUtility.DecomposeBaseAPI(Partial_SplPrompts):
            yield response
