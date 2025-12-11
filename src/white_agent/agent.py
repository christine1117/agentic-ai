"""
White Agent: CBT Therapist (Improved Version)
"""
import os
import tomllib
import uvicorn
from openai import OpenAI

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard
from a2a.utils import new_agent_text_message
from starlette.responses import JSONResponse  # For /status

def load_agent_card_toml(name):
    path = os.path.join(os.path.dirname(__file__), f"{name}.toml")
    print(f"📄 Loading TOML from: {path}")
    with open(path, "rb") as f:
        return tomllib.load(f)

class TherapistExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        user_input = context.get_user_input()
        print(f"\n🟦 [White Agent] Received: {user_input[:50]}...") 

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
       
        system_prompt = """
        You are a supportive CBT therapist. 
        Give concise, empathetic, and professional responses.
        """
        
        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7
            )
            reply = res.choices[0].message.content
        except Exception as e:
            print(f"❌ OpenAI Error: {e}")
            reply = f"[WhiteAgent Error] {e}"

        print(f"🗣️ [White Agent] Reply: {reply[:50]}...")
        await event_queue.enqueue_event(new_agent_text_message(reply))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        print("⚠️ White agent cancelled.")

def start_white_agent(name="white_agent", host="127.0.0.1", port=9002):
    print(f"Starting White Agent '{name}' on {host}:{port}...")
    
    try:
        card_dict = load_agent_card_toml(name)
    except FileNotFoundError:
        print(f"❌ Error: Config file {name}.toml not found")
        return

   
    env_url = os.getenv("WHITE_AGENT_URL")
    if env_url:
        url = env_url
    else:
        url = f"http://{host}:{port}"
        
    card_dict["url"] = url
    print(f"🌍 Public Identity: {url}")

    app = A2AStarletteApplication(
        agent_card=AgentCard(**card_dict),
        http_handler=DefaultRequestHandler(
            agent_executor=TherapistExecutor(),
            task_store=InMemoryTaskStore(),
        ),
    )
    
 
    starlette_app = app.build()
    async def force_status(request):
        return JSONResponse({"status": "ok", "agent": name})
    starlette_app.add_route("/status", force_status, methods=["GET"])

    uvicorn.run(starlette_app, host=host, port=port)

if __name__ == "__main__":
   
    start_white_agent()