from __future__ import annotations

from typing import List

from langchain_core.output_parsers import StrOutputParser

from .prompts import research_decision_prompt, research_summarize_prompt
from .tools import perform_web_search


def run_research(*, task: str, retrieved_context: str, llm: object) -> List[str]:
    decision_chain = research_decision_prompt() | llm | StrOutputParser()
    query = decision_chain.invoke({"task": task, "context": retrieved_context})

    if "NO_SEARCH" in query:
        return []

    results = perform_web_search(query)
    summarize_chain = research_summarize_prompt() | llm | StrOutputParser()
    summary = summarize_chain.invoke({"task": task, "results": results})
    return [summary]

