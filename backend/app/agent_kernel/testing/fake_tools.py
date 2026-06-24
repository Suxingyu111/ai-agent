class FakeTool:
    key = "fake.tool"

    async def ainvoke(self, arguments: dict) -> dict:
        return {"arguments": arguments}
