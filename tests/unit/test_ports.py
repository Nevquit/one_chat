"""端口与测试替身的一致性测试。

``runtime_checkable`` 的 Protocol 只检查方法是否存在，不检查签名；
签名一致性依赖 mypy 静态检查，这里只兜住"漏实现方法"这类错误。
"""

import asyncio

import pytest

from wanchain_agent.core.ports import BridgePort, KnowledgePort, LLMPort, TracePort
from tests.unit.fakes import FakeBridge, FakeKnowledge, FakeLLM, FakeTrace


@pytest.mark.parametrize(
    ("fake", "port"),
    [
        (FakeLLM, LLMPort),
        (FakeKnowledge, KnowledgePort),
        (FakeBridge, BridgePort),
        (FakeTrace, TracePort),
    ],
)
def test_fake_satisfies_port(fake, port):
    assert isinstance(fake(), port)


def test_fake_knowledge_applies_top_k():
    knowledge = FakeKnowledge()
    result = asyncio.run(knowledge.retrieve("跨链原理", top_k=1))
    assert len(result) == 1
    assert knowledge.queries == [("跨链原理", 1)]


def test_fake_trace_records_spans():
    trace = FakeTrace()
    with trace.span("router", intent="rag"):
        pass
    assert trace.spans == [{"name": "router", "attributes": {"intent": "rag"}}]
