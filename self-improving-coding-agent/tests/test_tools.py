from src.agent.tools import perform_web_search


class _DummyDDGS:
    def __init__(self, results):
        self._results = results

    def text(self, query, max_results=5):
        return self._results[:max_results]


class _FailingDDGS:
    def text(self, query, max_results=5):
        raise RuntimeError("boom")


def test_perform_web_search_formats_results():
    ddgs_client = _DummyDDGS(
        [
            {"title": "A", "href": "https://a", "body": "snippet-a"},
            {"title": "B", "href": "https://b", "body": "snippet-b"},
        ]
    )
    out = perform_web_search("query", ddgs_client=ddgs_client)
    assert "Title: A" in out
    assert "Link: https://a" in out
    assert "snippet-b" in out


def test_perform_web_search_handles_errors():
    out = perform_web_search("query", ddgs_client=_FailingDDGS())
    assert out.startswith("Search failed:")

