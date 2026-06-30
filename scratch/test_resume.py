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

    session_id = "test-resume-session-8888"
    captured_invocation_id = None

    # Step 1: Start the run
    print("--- FIRST RUN ---")
    new_message1 = types.Content(
        role="user",
        parts=[types.Part.from_text(text="Vision Transformers in Medical Imaging")]
    )
    async for event in runner.run_async(
        user_id="user",
        session_id=session_id,
        new_message=new_message1,
        run_config=RunConfig(streaming_mode=StreamingMode.SSE)
    ):
        print(f"EVENT: node={event.node_name}, partial={event.partial}, invocation_id={event.invocation_id}")
        if event.invocation_id:
            captured_invocation_id = event.invocation_id

    # Step 2: Resume with the FunctionResponse part
    print(f"\n--- SECOND RUN (RESUME) with invocation_id={captured_invocation_id} ---")
    new_message2 = types.Content(
        role="user",
        parts=[
            types.Part(
                function_response=types.FunctionResponse(
                    name="adk_request_input",
                    id="approval",
                    response={"result": "approve"}
                )
            )
        ]
    )
    async for event in runner.run_async(
        user_id="user",
        session_id=session_id,
        invocation_id=captured_invocation_id,
        new_message=new_message2,
        run_config=RunConfig(streaming_mode=StreamingMode.SSE)
    ):
        print(f"EVENT: node={event.node_name}, partial={event.partial}")
        if event.content and event.content.parts:
            text_parts = [p.text for p in event.content.parts if p.text]
            if text_parts:
                print("  Text:", "".join(text_parts)[:150].encode('utf-8'))

if __name__ == "__main__":
    asyncio.run(main())
