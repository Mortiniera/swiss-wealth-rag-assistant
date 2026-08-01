"""API tests for demo actors and workspace context."""

from uuid import uuid4

import app.api.actors as actors_api


class _FakeRole:
    code = "relationship_manager"
    name = "Relationship Manager"


class _FakeEmployee:
    employee_code = "EMP-0001"
    full_name = "Ada RM"
    email = "ada@helvetia.example"
    role = _FakeRole()


def test_list_actors(client, monkeypatch):
    monkeypatch.setattr(actors_api, "list_actors", lambda *_: [_FakeEmployee()])
    monkeypatch.setattr(
        actors_api,
        "build_actor_out",
        lambda emp: {
            "employee_code": emp.employee_code,
            "full_name": emp.full_name,
            "email": emp.email,
            "role_code": emp.role.code,
            "role_name": emp.role.name,
        },
    )

    response = client.get("/actors")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["employee_code"] == "EMP-0001"
    assert body[0]["role_code"] == "relationship_manager"


def test_get_actor_workspace(client, monkeypatch):
    monkeypatch.setattr(
        actors_api, "get_employee_by_code", lambda *_: _FakeEmployee()
    )
    monkeypatch.setattr(
        actors_api,
        "build_workspace_context",
        lambda emp: {
            "actor": {
                "employee_code": emp.employee_code,
                "full_name": emp.full_name,
                "email": emp.email,
                "role_code": emp.role.code,
                "role_name": emp.role.name,
            },
            "client_scope": "assigned",
            "panel_layout": {
                "focus_hint": "Relationship view",
                "primary": ["profile", "accounts"],
                "secondary": [],
            },
            "note": "Demo identity only",
        },
    )

    response = client.get("/actors/EMP-0001/workspace")
    assert response.status_code == 200
    body = response.json()
    assert body["client_scope"] == "assigned"
    assert body["actor"]["full_name"] == "Ada RM"


def test_get_actor_workspace_not_found(client, monkeypatch):
    monkeypatch.setattr(actors_api, "get_employee_by_code", lambda *_: None)
    response = client.get("/actors/EMP-UNKNOWN/workspace")
    assert response.status_code == 404
