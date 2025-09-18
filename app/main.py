from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import tasks

from fastapi import WebSocket
from .agent.agent import workflow
from langchain_core.messages import ToolMessage
from langchain_core.messages import AIMessage, HumanMessage

# Create tables on startup (simple for Day 1; you can switch to Alembic later)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Task Backend", version="0.1.0")

# permissive CORS for local Next.js dev; tighten in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.websocket("/ws/chat")
async def chat_endpoint(ws: WebSocket):
    await ws.accept()
    while True:
        try:
            user_text = await ws.receive_text()
            print(f">>> DEBUG: User said: {user_text!r}")

            # Always wrap input in HumanMessage
            state = {"messages": [HumanMessage(content=user_text)]}
            result = workflow.invoke(state)

            last = result["messages"][-1]
            print(f">>> DEBUG: Last message type={last.__class__.__name__}, content={getattr(last, 'content', None)}")

            if isinstance(last, AIMessage) and last.content:
                payload = {"response": last.content}
            elif isinstance(last, ToolMessage) and last.content:
                payload = {"response": last.content}
            else:
                payload = {"response": getattr(last, "content", str(last))}

            await ws.send_json(payload)

        except Exception as e:
            print(f">>> DEBUG ERROR: {e}")
            await ws.send_json({"error": str(e)})