"""Launcher module - initiates and coordinates the evaluation process."""

import multiprocessing
import asyncio
import time
import sys
import os


sys.path.append(os.getcwd())

from src.green_agent.agent import start_green_agent
from src.white_agent.agent import start_white_agent
from src.my_util import my_a2a

async def launch_evaluation():

    print("\n🚀 Launching Green Agent (Port 9001)...")
    green_address = ("127.0.0.1", 9001)
    green_url = f"http://{green_address[0]}:{green_address[1]}"
    
    p_green = multiprocessing.Process(
        target=start_green_agent, 
        args=("empa_green", *green_address)
    )
    p_green.start()
    
 
    if not await my_a2a.wait_agent_ready(green_url):
        print("Green agent failed to start.")
        p_green.terminate()
        return
    print("Green agent is ready.")

  
    print("\n🚀 Launching White Agent (Port 9002)...")
    white_address = ("127.0.0.1", 9002)
    white_url = f"http://{white_address[0]}:{white_address[1]}"
    
    p_white = multiprocessing.Process(
        target=start_white_agent, 
        args=("white_agent", *white_address)
    )
    p_white.start()
    
  
    if not await my_a2a.wait_agent_ready(white_url):
        print("White agent failed to start.")
        p_green.terminate()
        p_white.terminate()
        return
    print("White agent is ready.")

  
    print("\n Sending task to Green Agent...")
    

    task_text = f"""
    Please evaluate the following agent:
    <white_agent_url>
    {white_url}
    </white_agent_url>
    """
    
    try:
        response = await my_a2a.send_message(green_url, task_text)
        print("\n📩 Response from Green Agent:")
        print(response)
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")


    print("\n🛑 Evaluation complete. Terminating agents...")
    p_green.terminate()
    p_green.join()
    p_white.terminate()
    p_white.join()
    print("✅ All agents terminated.")