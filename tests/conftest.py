# tests/conftest.py
from typing import Any, Dict, Optional
from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

import deps  # our DI seam
import main  # the FastAPI app module we’ve built
import database  # to monkeypatch ping_db in tests


# ---- Fake Mongo (async) ------------------------------------------------------
class _InsertOneResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id

class _UpdateResult:
    def __init__(self, matched_count, modified_count):
        self.matched_count = matched_count
        self.modified_count = modified_count

class FakeAsyncTickets:
    """
    Minimal in-memory collection that *looks like* Motor’s async API:
    - insert_one, find_one, update_one are 'async def'
    - stores documents in a dict keyed by 'ObjectId-like' strings
    """
    def __init__(self):
        self._docs: Dict[str, Dict[str, Any]] = {}

    async def insert_one(self, doc: Dict[str, Any]):
        # simulate Mongo’s ObjectId as a hex-ish id (string good enough for tests)
        oid = uuid4().hex[:24]
        to_store = deepcopy(doc)
        to_store["_id"] = oid
        self._docs[oid] = to_store
        return _InsertOneResult(inserted_id=oid)

    async def find_one(self, filt: Dict[str, Any]):
        # Expect {"_id": <id>} or other simple filters (we only need _id for tests)
        _id = filt.get("_id")
        if _id is None:
            return None
        doc = self._docs.get(str(_id))
        return deepcopy(doc) if doc else None

    async def update_one(self, filt: Dict[str, Any], update: Dict[str, Any]):
        _id = filt.get("_id")
        if _id is None or str(_id) not in self._docs:
            return _UpdateResult(0, 0)
        "$set" in update or update.update({"$set": {}})  # ensure key exists
        for k, v in update["$set"].items():
            self._docs[str(_id)][k] = v
        return _UpdateResult(1, 1)


# ---- Fake Queue / Job object -------------------------------------------------
class _FakeJob:
    """Represents a queued job with an id only (enough for create/requeue tests)."""
    def __init__(self):
        self.id = uuid4().hex

class FakeQueue:
    """Tiny stand-in for RQ’s Queue with just an enqueue() that returns a job id."""
    def __init__(self):
        self.enqueued = []

    def enqueue(self, func, *args, **kwargs):
        job = _FakeJob()
        # record a tuple for introspection if needed
        self.enqueued.append((job.id, func.__name__, args, kwargs))
        return job

    @property
    def connection(self):
        """
        For /jobs/{job_id} tests we’ll monkeypatch Job.fetch, so we don’t need
        a real Redis connection. Providing a dummy attribute keeps code happy.
        """
        class _Dummy:
            def ping(self): return True
        return _Dummy()


# ---- Pytest fixtures ---------------------------------------------------------
@pytest.fixture
def fake_db():
    """Fresh in-memory tickets collection per test."""
    return FakeAsyncTickets()

@pytest.fixture
def fake_queue():
    """Fresh in-memory queue per test."""
    return FakeQueue()

@pytest.fixture
def client(monkeypatch, fake_db, fake_queue):
    """
    Build a TestClient with our DI seam pointing at fakes, *without* running lifespan.
    We disable lifespan so main.lifespan doesn’t overwrite deps.* with real clients.
    """
    # 1) Ensure /health/db doesn’t try to ping a real Mongo during tests
    monkeypatch.setattr(database, "ping_db", lambda: True)

    # 2) Wire fakes into the DI seam before the app starts
    deps.ticket_collection = fake_db
    deps.job_queue = fake_queue

    # 3) Create the TestClient with lifespan OFF so startup doesn’t reassign deps.*
    #    Starlette’s TestClient supports lifespan="off" to skip startup/shutdown.
    tc = TestClient(main.app, raise_server_exceptions=True)
    return tc
