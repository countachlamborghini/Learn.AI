from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


def ensure_directory(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


DATA_DIR = Path(os.getenv("API_DATA_DIR", "/workspace/data"))
UPLOADS_DIR = DATA_DIR / "uploads"
ensure_directory(UPLOADS_DIR)


class SignupRequest(BaseModel):
    email: str
    password: str
    tenant_code: Optional[str] = None


class SignupResponse(BaseModel):
    user_id: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user_id: str


class TutorChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    level: Optional[str] = Field(default="HS")
    scope: Optional[dict] = None


class TutorChatResponse(BaseModel):
    reply: str
    citations: List[dict]
    session_id: str


class BoostStartRequest(BaseModel):
    timebox: int = Field(default=10, ge=5, le=30)


class QuizItem(BaseModel):
    id: str
    type: str
    prompt: str
    options: Optional[List[str]] = None
    answer: Optional[str] = None
    explanation: Optional[str] = None
    source_refs: Optional[List[str]] = None


class BoostStartResponse(BaseModel):
    quiz_id: str
    items: List[QuizItem]


class BoostAnswerRequest(BaseModel):
    quiz_id: str
    item_id: str
    answer: str


class BoostAnswerResponse(BaseModel):
    correct: bool
    explanation: str
    next_item: Optional[QuizItem] = None


class ProgressOverview(BaseModel):
    mastery: Dict[str, int]
    streak_days: int
    time_saved_minutes_this_week: int


class DocumentMetadata(BaseModel):
    id: str
    user_id: str
    s3_uri: Optional[str] = None
    path: Optional[str] = None
    status: str
    mime: Optional[str] = None
    tokens: Optional[int] = 0
    created_at: datetime


class Flashcard(BaseModel):
    id: str
    document_id: str
    chunk_id: Optional[str] = None
    front: str
    back: str
    difficulty: Optional[int] = 1


from .analytics import log_event
from .db import engine  # ensures DB init side-effect


app = FastAPI(title="Global Brain API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory stores for MVP demo/dev
FAKE_DB: Dict[str, dict] = {
    "users": {},
    "documents": {},
    "flashcards_by_doc": {},
    "sessions": {},
    "quizzes": {},
    "progress": {},
}


def get_current_user_id() -> str:
    # For MVP dev, return a fixed user id
    user_id = "demo-user"
    if user_id not in FAKE_DB["users"]:
        FAKE_DB["users"][user_id] = {"email": "demo@example.com"}
    return user_id


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# Auth
@app.post("/v1/auth/signup", response_model=SignupResponse)
def signup(payload: SignupRequest) -> SignupResponse:
    user_id = str(uuid.uuid4())
    FAKE_DB["users"][user_id] = {"email": payload.email, "tenant_code": payload.tenant_code}
    return SignupResponse(user_id=user_id)


@app.post("/v1/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    # Always succeed for MVP dev; issue a fake token
    user_id = next((uid for uid, u in FAKE_DB["users"].items() if u.get("email") == payload.email), None)
    if not user_id:
        user_id = str(uuid.uuid4())
        FAKE_DB["users"][user_id] = {"email": payload.email}
    token = f"fake-token-{user_id}"
    return LoginResponse(token=token, user_id=user_id)


# Documents
@app.post("/v1/docs/upload")
async def upload_document(file: UploadFile = File(...), user_id: str = Depends(get_current_user_id), request: Request = None) -> dict:
    doc_id = str(uuid.uuid4())
    safe_name = file.filename.replace("/", "_")
    dest_path = UPLOADS_DIR / f"{doc_id}-{safe_name}"
    content = await file.read()
    dest_path.write_bytes(content)
    FAKE_DB["documents"][doc_id] = DocumentMetadata(
        id=doc_id,
        user_id=user_id,
        path=str(dest_path),
        status="processing",
        mime=file.content_type,
        created_at=datetime.utcnow(),
    ).model_dump()
    # Seed stub flashcards for demo
    FAKE_DB["flashcards_by_doc"][doc_id] = [
        Flashcard(id=str(uuid.uuid4()), document_id=doc_id, front="What is the main idea?", back="Stub answer.").model_dump(),
        Flashcard(id=str(uuid.uuid4()), document_id=doc_id, front="Define key term X.", back="Definition stub.").model_dump(),
    ]
    # Pretend processing completes shortly
    FAKE_DB["documents"][doc_id]["status"] = "ready"
    log_event("doc_uploaded", {"user_id": user_id, "doc_id": doc_id, "filename": file.filename})
    return {"document_id": doc_id}


@app.get("/v1/docs/{doc_id}", response_model=DocumentMetadata)
def get_document(doc_id: str, user_id: str = Depends(get_current_user_id)) -> DocumentMetadata:
    doc = FAKE_DB["documents"].get(doc_id)
    if not doc or doc.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentMetadata(**doc)


@app.get("/v1/docs/{doc_id}/flashcards", response_model=List[Flashcard])
def get_flashcards(doc_id: str, user_id: str = Depends(get_current_user_id)) -> List[Flashcard]:
    doc = FAKE_DB["documents"].get(doc_id)
    if not doc or doc.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Document not found")
    cards = FAKE_DB["flashcards_by_doc"].get(doc_id, [])
    return [Flashcard(**c) for c in cards]


# Tutor Chat
@app.post("/v1/tutor/chat", response_model=TutorChatResponse)
def tutor_chat(payload: TutorChatRequest, user_id: str = Depends(get_current_user_id)) -> TutorChatResponse:
    session_id = payload.session_id or str(uuid.uuid4())
    FAKE_DB["sessions"].setdefault(session_id, {"user_id": user_id, "messages": []})
    FAKE_DB["sessions"][session_id]["messages"].append({"role": "user", "content": payload.message})
    reply_text = (
        "This is a stub tutor reply. In production, responses will cite sources and adapt to your level."
    )
    citations = []
    FAKE_DB["sessions"][session_id]["messages"].append({"role": "assistant", "content": reply_text, "citations": citations})
    log_event("tutor_chat", {"user_id": user_id, "session_id": session_id})
    return TutorChatResponse(reply=reply_text, citations=citations, session_id=session_id)


# Brain Boost
@app.post("/v1/tutor/boost/start", response_model=BoostStartResponse)
def boost_start(payload: BoostStartRequest, user_id: str = Depends(get_current_user_id)) -> BoostStartResponse:
    quiz_id = str(uuid.uuid4())
    items = [
        QuizItem(
            id=str(uuid.uuid4()),
            type="mcq",
            prompt="What is photosynthesis?",
            options=["Energy release", "Energy storage via light", "Cell division", "DNA repair"],
            answer="Energy storage via light",
            explanation="Plants convert light energy into chemical energy.",
        ),
        QuizItem(
            id=str(uuid.uuid4()),
            type="open",
            prompt="Explain Newton's second law in one sentence.",
        ),
    ]
    FAKE_DB["quizzes"][quiz_id] = {"user_id": user_id, "items": [i.model_dump() for i in items], "index": 0}
    log_event("boost_start", {"user_id": user_id, "quiz_id": quiz_id, "count": len(items)})
    return BoostStartResponse(quiz_id=quiz_id, items=items)


@app.post("/v1/tutor/boost/answer", response_model=BoostAnswerResponse)
def boost_answer(payload: BoostAnswerRequest, user_id: str = Depends(get_current_user_id)) -> BoostAnswerResponse:
    quiz = FAKE_DB["quizzes"].get(payload.quiz_id)
    if not quiz or quiz.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Quiz not found")
    items = [QuizItem(**i) for i in quiz["items"]]
    current = next((i for i in items if i.id == payload.item_id), None)
    if not current:
        raise HTTPException(status_code=404, detail="Item not found")
    correct = current.answer is not None and payload.answer.strip() == current.answer
    # Advance to next item if exists
    try:
        idx = items.index(current)
    except ValueError:
        idx = -1
    next_item = items[idx + 1] if idx + 1 < len(items) else None
    explanation = current.explanation or ("Thanks! Review model feedback coming soon.")
    return BoostAnswerResponse(correct=bool(correct), explanation=explanation, next_item=next_item)


# Progress
@app.get("/v1/progress/overview", response_model=ProgressOverview)
def progress_overview(user_id: str = Depends(get_current_user_id)) -> ProgressOverview:
    # Stubbed values
    mastery = {"Kinematics": 62, "Photosynthesis": 70}
    streak_days = 3
    time_saved_minutes_this_week = 24
    return ProgressOverview(
        mastery=mastery,
        streak_days=streak_days,
        time_saved_minutes_this_week=time_saved_minutes_this_week,
    )


@app.get("/v1/progress/topics")
def progress_topics(user_id: str = Depends(get_current_user_id)) -> Dict[str, int]:
    return {"Kinematics": 62, "Photosynthesis": 70, "Stoichiometry": 45}

