from unittest.mock import Mock

from plane import AgentMembershipRequest, AgentMembershipResponse
from plane.client import PlaneClient


def test_apply_agent_membership_sends_idempotency_header() -> None:
    client = PlaneClient(base_url="https://plane.example", api_key="lifecycle-token")
    response = Mock(
        status_code=200,
        content=b"{}",
        headers={"content-type": "application/json"},
    )
    response.json.return_value = {
        "membership_id": "00000000-0000-0000-0000-000000000001",
        "user_id": "00000000-0000-0000-0000-000000000002",
        "workspace_id": "00000000-0000-0000-0000-000000000003",
        "state": "active",
        "project_ids": [],
        "credential": None,
        "replayed": True,
    }
    client.workspaces.session.put = Mock(return_value=response)

    result = client.workspaces.apply_agent_membership(
        "workspace",
        "agent-a",
        AgentMembershipRequest(display_name="Agent A", project_ids=[]),
        idempotency_key="operation-1",
    )

    assert result.replayed is True
    call = client.workspaces.session.put.call_args
    assert call.args[0].endswith("/workspaces/workspace/agent-memberships/agent-a/")
    assert call.kwargs["headers"]["Idempotency-Key"] == "operation-1"


def test_agent_membership_response_preserves_new_fields() -> None:
    response = AgentMembershipResponse(
        membership_id="membership",
        user_id="user",
        workspace_id="workspace",
        state="active",
        project_ids=[],
        replayed=False,
        lifecycle_revision=2,
    )

    assert response.lifecycle_revision == 2
