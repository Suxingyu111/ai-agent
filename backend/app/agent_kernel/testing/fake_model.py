class FakeModel:
    async def ainvoke(self, prompt: str) -> str:
        return prompt
