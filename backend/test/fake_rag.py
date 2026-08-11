class FakeRagChain:
    """
    测试环境使用的假RAG链

    不调用真实LLM，只返回固定结果
    """

    def invoke(self, data):
        return {
            "answer": "这是测试回答",
            "context": []
        }

    async def astream(self, inputs):

        yield {
            "answer": "测试"
        }
