def choose_initial_agent(goal: str) -> str:
    if "知识库" in goal:
        return "knowledge_agent"
    if "搜索" in goal or "联网" in goal:
        return "research_agent"
    return "planner_agent"
