import storage.postgres as postgres_module


class RecordingJson:
    def __init__(self, value, dumps):
        self.value = value
        self.dumps = dumps


class StubCursor:
    def __init__(self, result=None, should_fail=False):
        self.result = result or []
        self.should_fail = should_fail
        self.description = [("id",)] if result is not None else None
        self.executed = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, query, params):
        self.executed.append((query, params))
        if self.should_fail:
            raise RuntimeError("boom")

    def fetchall(self):
        return self.result


class StubConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self, cursor_factory=None):
        return self._cursor

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


def test_execute_commits_for_returning_queries(monkeypatch):
    cursor = StubCursor(result=[{"id": "123"}])
    connection = StubConnection(cursor)
    database = postgres_module.PostgresConnection()

    monkeypatch.setattr(database, "connect", lambda: connection)

    result = database.execute("INSERT INTO table VALUES (%s) RETURNING id", ("value",))

    assert result == [{"id": "123"}]
    assert connection.committed is True
    assert connection.rolled_back is False
    assert connection.closed is True


def test_execute_rolls_back_on_failure(monkeypatch):
    cursor = StubCursor(result=[], should_fail=True)
    connection = StubConnection(cursor)
    database = postgres_module.PostgresConnection()

    monkeypatch.setattr(database, "connect", lambda: connection)

    try:
        database.execute("INSERT INTO table VALUES (%s)", ("value",))
    except RuntimeError:
        pass
    else:
        raise AssertionError("database.execute should re-raise cursor failures")

    assert connection.committed is False
    assert connection.rolled_back is True
    assert connection.closed is True


def test_prepare_params_wraps_json_values(monkeypatch):
    database = postgres_module.PostgresConnection()

    monkeypatch.setattr(postgres_module, "Json", RecordingJson)

    prepared = database._prepare_params(("value", {"status": "ok"}, [1, 2, 3]))

    assert prepared[0] == "value"
    assert isinstance(prepared[1], RecordingJson)
    assert isinstance(prepared[2], RecordingJson)
