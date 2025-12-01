"""White agent implementation - the target agent being tested."""

import uvicorn
import tomllib
import dotenv
import os
from openai import OpenAI

# Import a2a library
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard
from a2a.utils import new_agent_text_message

dotenv.load_dotenv()

# =================================================================
# 1. Helper function
# =================================================================
def load_agent_card_toml(agent_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    toml_path = os.path.join(current_dir, f"{agent_name}.toml")
    with open(toml_path, "rb") as f:
        return tomllib.load(f)

# =================================================================
# 2. Executor
# =================================================================
class TherapistExecutor(AgentExecutor):
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_prompt = """
        You are Dr. White, a compassionate Licensed Clinical Therapist specializing in CBT.
        Your goal is to demonstrate high empathy and professional standards.
        Keep responses concise (under 100 words) for testing purposes.
        """

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # 1. Get question
        user_input = context.get_user_input()
        print(f"Dr. White: Received question -> {user_input}")

        # 2. Call GPT-4 to generate answer
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"Error: {str(e)}"

        print(f"🗣️ Dr. White: Answer -> {answer[:50]}...")

        # 3. Return to Green Agent
        await event_queue.enqueue_event(
            new_agent_text_message(answer)
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        print("Dr. White task cancelled.")

# =================================================================
# 3. Start Function
# =================================================================
def start_white_agent(agent_name="white_agent", host="127.0.0.1", port=9002):
    print(f"Starting White Agent '{agent_name}' on {host}:{port}...")
    
    try:
        agent_card_dict = load_agent_card_toml(agent_name)
    except FileNotFoundError:
        print(f"❌ Error: Config file src/white_agent/{agent_name}.toml not found")
        return

    # Dynamically set URL
    url = f"http://{host}:{port}"
    
    
    agent_card_dict["url"] = url 

    request_handler = DefaultRequestHandler(
        agent_executor=TherapistExecutor(),
        task_store=InMemoryTaskStore(),
    )

    app = A2AStarletteApplication(
        agent_card=AgentCard(**agent_card_dict),
        http_handler=request_handler,
    )

    uvicorn.run(app.build(), host=host, port=port)