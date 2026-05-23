import asyncio
import io

import pytest

from apps.api.fastapi_compat import HTTPException, UploadFile
from apps.api.routes import admin, chat, documents, memory


@pytest.mark.parametrize(
    ("callable_obj", "args"),
    [
        (chat.chat_stream_endpoint, ()),
        (memory.get_memories, ()),
        (memory.refresh_memories, ()),
        (documents.upload_document, (UploadFile(filename="demo.txt", file=io.BytesIO(b"demo")),)),
        (admin.reindex, ()),
        (admin.rebuild_memory, ()),
        (admin.rollback, ()),
    ],
)
def test_deferred_routes_raise_not_implemented(callable_obj, args):
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(callable_obj(*args))

    assert exc_info.value.status_code == 501


def test_admin_health_returns_ok():
    response = asyncio.run(admin.health())

    assert response.message == "ok"
