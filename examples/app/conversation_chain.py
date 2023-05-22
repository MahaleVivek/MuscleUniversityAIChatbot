from functools import lru_cache
from typing import Callable


from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates
from langchain import ConversationChain, OpenAI, PromptTemplate
from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel
import uvicorn


from lanarky.responses import StreamingResponse
from lanarky.testing import mount_gradio_app
from lanarky.websockets import WebsocketConnection




load_dotenv()


app = mount_gradio_app(FastAPI(title="ConversationChainDemo"))
templates = Jinja2Templates(directory="templates")




class QueryRequest(BaseModel):
   query: str




def conversation_chain_dependency() -> Callable[[], ConversationChain]:
   @lru_cache(maxsize=1)
   def dependency() -> ConversationChain:


       template = """You are a muscle university fitness chatbot having a conversation with a fitness enthusiast who is trying improve his fitness journey.
       you can answer the question related to fitness/ workout plans/ diet/ grocery for healthy diet. add bullet points. you can answer the user queries
       in Hinglish and use jeet selal's style to respond. restrcit the answers to fitness/ workout plans/ diet/ grocery for healthy diet. if you don't know the answer,
       don't try to make up the answer, add detailed answers and add bullet points if needed.


       {history}


       Human: {input}
       Chatbot:"""


       PROMPT = PromptTemplate(
           input_variables=["input", "history"],
           template=template
           )
  
       return ConversationChain(
           llm=OpenAI(
               temperature=0,
               streaming=True,
           ),
           verbose=True,
           prompt=PROMPT,
       )


   return dependency




conversation_chain = conversation_chain_dependency()




@app.post("/chat")
async def chat(
   request: QueryRequest,
   chain: ConversationChain = Depends(conversation_chain),
) -> StreamingResponse:
   return StreamingResponse.from_chain(
       chain, request.query, media_type="text/event-stream"
   )




@app.get("/")
async def get(request: Request):
   return templates.TemplateResponse("index.html", {"request": request})




@app.websocket("/ws")
async def websocket_endpoint(
   websocket: WebSocket, chain: ConversationChain = Depends(conversation_chain)
):
   connection = WebsocketConnection.from_chain(chain=chain, websocket=websocket)
   await connection.connect()




if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8000)