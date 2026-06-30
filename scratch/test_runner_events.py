import asyncio
from google.adk.runners import Runner
from google.adk.cli.utils.service_factory import (
    create_session_service_from_options,
    create_artifact_service_from_options,
    create_memory_service_from_options
)
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types

from app.agent import app as adk_app

async def main():
    agents_dir = "app"
    session_service = create_session_service_from_options(base_dir=agents_dir)
    artifact_service = create_artifact_service_from_options(base_dir=agents_dir)
    memory_service = create_memory_service_from_options(base_dir=agents_dir)
    credential_service = InMemoryCredentialService()

    runner = Runner(
        app=adk_app,
        session_service=session_service,
        artifact_service=artifact_service,
        memory_service=memory_service,
        credential_service=credential_service,
        auto_create_session=True
    )

    new_message = types.Content(
        role="user",
        parts=[types.Part.from_text(text="Vision Transformers in Medical Imaging")]
    )

    print("Starting agent execution...")
    async for event in runner.run_async(
        user_id="user",
        session_id="test-session-12345",
        new_message=new_message,
        run_config=RunConfig(streaming_mode=StreamingMode.SSE)
    ):
        print(f"EVENT: partial={event.partial}, node_name={event.node_name}")
        calls = event.get_function_calls()
        if calls:
            print("  Function Calls:", [c.name for c in calls])
        responses = event.get_function_responses()
        if responses:
            print("  Function Responses:", [r.name for r in responses])
        # If it contains text content
        if event.content and event.content.parts:
            text_parts = [p.text for p in event.content.parts if p.text]
            if text_parts:
                print("  Text Parts:", "".join(text_parts)[:100])

if __name__ == "__main__":
    asyncio.run(main())
