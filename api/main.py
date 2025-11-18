from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select
from api.database import engine, get_session
from api.models import ChatSession, ChatMessage
from api.pricing import calculate_cost
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-4o-mini"
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = FastAPI(title="AI Cost Tracker Chatbot")

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@app.post("/sessions")
async def create_session(db: AsyncSession = Depends(get_session)):
    session = ChatSession(name="New Chat")
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return {"session_id": session.id}


@app.post("/sessions/{session_id}/chat")
async def chat(
    session_id: int,
    user_input: str = Query(...),  # <- очікуємо query параметр
    db: AsyncSession = Depends(get_session)
):
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    history_msgs = result.all()

    if not history_msgs:
        session_check = await db.get(ChatSession, session_id)
        if not session_check:
            raise HTTPException(status_code=404, detail="Session not found")

    messages = [{"role": msg.role, "content": msg.content} for msg in history_msgs]
    messages.append({"role": "user", "content": user_input})

    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages
    )

    content = response.choices[0].message.content
    usage = response.usage
    p_tokens = usage.prompt_tokens
    c_tokens = usage.completion_tokens
    cost = calculate_cost(MODEL, p_tokens, c_tokens)

    db.add(ChatMessage(session_id=session_id, role="user", content=user_input))
    db.add(ChatMessage(
        session_id=session_id,
        role="assistant",
        content=content,
        model_name=MODEL,
        prompt_tokens=p_tokens,
        completion_tokens=c_tokens,
        cost_usd=cost
    ))

    await db.commit()

    return {
        "response": content,
        "cost_usd": cost,
        "tokens": {"input": p_tokens, "output": c_tokens}
    }


@app.get("/sessions/{session_id}/history")
async def get_history(session_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    total_cost = sum(msg.cost_usd or 0 for msg in messages)

    return {
        "session_id": session_id,
        "total_cost_usd": round(total_cost, 6),
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "cost_usd": msg.cost_usd or 0
            } for msg in messages
        ]
    }

