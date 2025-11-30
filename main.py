import argparse
import asyncio
from orchestrator.agent import create_orchestrator_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

async def run_agent(app_name: str, user_id: str, session_id: str, prompt: str):
    """
    Initializes and runs the orchestrator agent.
    """
    print(f"---\nInitializing agents...\n---")
    orchestrator_agent = create_orchestrator_agent()
    
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    
    runner = Runner(
        agent=orchestrator_agent, app_name=app_name, session_service=session_service
    )
    
    print(f"---\nRunning with prompt: {prompt}\n---")
    
    content = types.Content(role="user", parts=[types.Part(text=prompt)])
    
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"{event.author}: {part.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AutoScraper Agent")
    parser.add_argument("--url", type=str, required=True, help="The target URL to scrape.")
    parser.add_argument("--prompt", type=str, required=True, help="The data to extract.")
    args = parser.parse_args()

    full_prompt = f"Create a scraper for the URL: {args.url}. The data to extract is: {args.prompt}"

    asyncio.run(run_agent("autoscraper", "user1", "session1", full_prompt))
