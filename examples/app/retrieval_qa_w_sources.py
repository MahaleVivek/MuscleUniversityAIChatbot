from functools import lru_cache
from typing import Callable

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel

from lanarky.responses import StreamingResponse
from lanarky.testing import mount_gradio_app
from lanarky.websockets import WebsocketConnection

load_dotenv()

app = mount_gradio_app(FastAPI(title="RetrievalQAWithSourcesChainDemo"))

templates = Jinja2Templates(directory="templates")


class QueryRequest(BaseModel):
    query: str


def retrieval_qa_chain_dependency() -> Callable[[], RetrievalQAWithSourcesChain]:
    @lru_cache(maxsize=1)
    def dependency() -> RetrievalQAWithSourcesChain:
        from langchain.embeddings import OpenAIEmbeddings
        from langchain.vectorstores import FAISS

        db = FAISS.load_local(
            folder_path="vector_stores/",
            index_name="langchain-python",
            embeddings=OpenAIEmbeddings(),
        )

        return RetrievalQAWithSourcesChain.from_chain_type(
            llm=ChatOpenAI(
                temperature=0,
                streaming=True,
            ),
            chain_type="stuff",
            retriever=db.as_retriever(),
            return_source_documents=True,
            verbose=True,
        )

    return dependency


retrieval_qa_chain = retrieval_qa_chain_dependency()


@app.post("/chat")
async def chat(
    request: QueryRequest,
    chain: RetrievalQAWithSourcesChain = Depends(retrieval_qa_chain),
) -> StreamingResponse:
    return StreamingResponse.from_chain(
        chain, request.query, media_type="text/event-stream"
    )


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    chain: RetrievalQAWithSourcesChain = Depends(retrieval_qa_chain),
):
    connection = WebsocketConnection.from_chain(chain=chain, websocket=websocket)
    await connection.connect()
