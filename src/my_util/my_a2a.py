import httpx
import asyncio
import uuid

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    Part,
    TextPart,
    MessageSendParams,
    Message,
    Role,
    SendMessageRequest,
    SendMessageResponse,
)

async def get_agent_card(url: str) -> AgentCard | None:
    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=url)
        try:
            card: AgentCard | None = await resolver.get_agent_card()
            return card
        except:
            return None

async def wait_agent_ready(url, timeout=10):
    retry_cnt = 0
    while retry_cnt < timeout:
        retry_cnt += 1
        print(f"Waiting for agent at {url} ({retry_cnt}/{timeout})...")
        try:
            card = await get_agent_card(url)
            if card is not None:
                return True
        except Exception:
            pass
        await asyncio.sleep(1)
    return False

async def send_message(url, message, task_id=None, context_id=None) -> SendMessageResponse:
    card = await get_agent_card(url)
    if not card:
        raise ValueError(f"Cannot connect to agent at {url}")
        
    async with httpx.AsyncClient(timeout=120.0) as httpx_client:
        client = A2AClient(httpx_client=httpx_client, agent_card=card)

        message_id = uuid.uuid4().hex
        params = MessageSendParams(
            message=Message(
                role=Role.user,
                parts=[Part(TextPart(text=message))],
                message_id=message_id,
                task_id=task_id,
                context_id=context_id,
            )
        )
        request_id = uuid.uuid4().hex
        req = SendMessageRequest(id=request_id, params=params)
        response = await client.send_message(request=req)
        return response