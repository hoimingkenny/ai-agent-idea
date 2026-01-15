from langchain_core.prompts import ChatPromptTemplate


def research_decision_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Analyze the task and context. If web research is needed, output a concise search query. Otherwise output 'NO_SEARCH'.",
            ),
            ("user", "Task: {task}\nContext: {context}"),
        ]
    )


def research_summarize_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", "Summarize the search results into actionable notes for coding."),
            ("user", "Task: {task}\nSearch Results:\n{results}"),
        ]
    )


def planning_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Create a step-by-step implementation plan.\n\nContext from past lessons:\n{context}{research_context}",
            ),
            ("user", "{task}"),
        ]
    )


def coding_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Write Python code to solve the task following the plan. Output ONLY the python code, no markdown.",
            ),
            (
                "user",
                "Task: {task}\n"
                "Plan: {plan}\n\n"
                "Research Notes:\n{research_notes}\n\n"
                "Previous Code: {code}\n\n"
                "Reflections/Errors: {reflections}\n\n"
                "Latest Reflection:\n{reflection}",
            ),
        ]
    )


def reflection_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Analyze the error and code and provide a concrete fix strategy.",
            ),
            ("user", "Code:\n{code}\n\nError:\n{error}\n\nOutput:\n{output}"),
        ]
    )
