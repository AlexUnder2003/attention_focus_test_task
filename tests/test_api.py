import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "update_data, expected_title, expected_description, expected_status",
    [
        ({"title": "Updated Title"}, "Updated Title", "Test Desc", "pending"),
        (
            {"description": "New Description"},
            "Test Task",
            "New Description",
            "pending",
        ),
        ({"status": "done"}, "Test Task", "Test Desc", "done"),
        (
            {
                "title": "New Title",
                "description": "New Desc",
                "status": "in_progress",
            },
            "New Title",
            "New Desc",
            "in_progress",
        ),
    ],
)
async def test_update_task_various_fields(
    async_client,
    test_task,
    update_data,
    expected_title,
    expected_description,
    expected_status,
):
    response = await async_client.patch(
        f"/tasks/{test_task.id}", json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == expected_title
    assert data["description"] == expected_description
    assert data["status"] == expected_status


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "task_payload",
    [
        {"title": "Task 1", "description": "Desc 1", "status": "pending"},
        {"title": "Task 2", "description": "Desc 2", "status": "pending"},
        {"title": "Task 3", "description": "Desc 3", "status": "pending"},
    ],
)
async def test_create_task_various_data(async_client, task_payload):
    response = await async_client.post("/tasks/", json=task_payload)
    assert response.status_code == 200
    data = response.json()
    for key, val in task_payload.items():
        assert data[key] == val


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status, expected_task_key",
    [
        ("pending", "1"),
        ("in_progress", "2"),
        ("done", "3"),
    ],
)
async def test_read_tasks_with_status(
    async_client, test_tasks, status, expected_task_key
):
    response = await async_client.get(f"/tasks/?status={status}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(task["status"].lower() == status for task in data)
    assert any(task["id"] == test_tasks[expected_task_key].id for task in data)


@pytest.mark.asyncio
async def test_read_tasks(async_client, test_tasks):
    response = await async_client.get("/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(task["id"] == test_tasks["1"].id for task in data)
    assert any(task["id"] == test_tasks["2"].id for task in data)
    assert any(task["id"] == test_tasks["3"].id for task in data)


@pytest.mark.asyncio
async def test_read_task(async_client, test_task):
    response = await async_client.get(f"/tasks/{test_task.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_task.id
    assert data["title"] == test_task.title


@pytest.mark.asyncio
async def test_delete_task(async_client, test_task):
    response = await async_client.delete(f"/tasks/{test_task.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Task deleted successfully"

    response = await async_client.get(f"/tasks/{test_task.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_read_nonexistent_task(async_client):
    response = await async_client.get("/tasks/9999")
    assert response.status_code == 404
