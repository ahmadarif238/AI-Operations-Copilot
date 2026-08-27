import pytest
from app.agents.agents_definitions import WeeklySummaryAgent, NotificationAgent, MockLLM, QueryAgent
from unittest.mock import MagicMock, patch

def test_mock_llm():
    llm = MockLLM()
    # Test Classify
    msg = MagicMock()
    msg.content = "Classify the query: How to restart server?"
    res = llm.invoke([msg])
    assert "route" in res.content
    
    # Test Answer
    msg.content = "Answer the user's question: What is safety?"
    res = llm.invoke([msg])
    assert "mock response" in res.content

def test_notification_agent():
    agent = NotificationAgent()
    res = agent.send_alert({"ticket_id": "123"})
    assert res["notification_sent"] is True

@patch("app.agents.agents_definitions.SessionLocal")
@patch("app.agents.agents_definitions.crud")
def test_weekly_summary_agent(mock_crud, mock_session):
    # Mock DB return
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    mock_crud.get_logs_by_range.return_value = [
        MagicMock(type="ERROR"), MagicMock(type="INFO")
    ]
    
    agent = WeeklySummaryAgent()
    res = agent.generate({})
    
    assert "summary_stats" in res
    assert res["summary_stats"]["total_logs_analyzed"] == 2
    assert "Critical Issues: 1" in res["answer"]
