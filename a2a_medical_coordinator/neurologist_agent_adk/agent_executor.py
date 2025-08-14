import asyncio
import logging
from collections.abc import AsyncGenerator

from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    FilePart,
    FileWithBytes,
    FileWithUri,
    Part,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils.errors import ServerError
from google.adk import Runner
from google.adk.events import Event
from google.genai import types

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NeurologistAgentExecutor(AgentExecutor):
    """An AgentExecutor that runs the Neurologist office's ADK-based Agent."""

    def __init__(self, agent_runner: Runner):
        self.agent_runner = agent_runner
        self._active_sessions = {}

    def _execute_agent_session(
        self, session_id: str, user_message: types.Content
    ) -> AsyncGenerator[Event, None]:
        return self.agent_runner.run_async(
            session_id=session_id, user_id="neurologist_office", new_message=user_message
        )

    async def _process_appointment_request(
        self,
        patient_message: types.Content,
        session_id: str,
        task_updater: TaskUpdater,
    ) -> None:
        session_obj = await self._get_or_create_session(session_id)
        active_session_id = session_obj.id

        async for event in self._execute_agent_session(active_session_id, patient_message):
            if event.is_final_response():
                response_parts = self._convert_genai_parts_to_a2a(
                    event.content.parts if event.content and event.content.parts else []
                )
                logger.debug("Processing final appointment response: %s", response_parts)
                task_updater.add_artifact(response_parts)
                task_updater.complete()
                break
            if not event.get_function_calls():
                logger.debug("Processing intermediate appointment response")
                task_updater.update_status(
                    TaskState.working,
                    message=task_updater.new_agent_message(
                        self._convert_genai_parts_to_a2a(
                            event.content.parts
                            if event.content and event.content.parts
                            else []
                        ),
                    ),
                )
            else:
                logger.debug("Skipping function call event")

    async def execute(
        self,
        request_context: RequestContext,
        event_queue: EventQueue,
    ):
        if not request_context.task_id or not request_context.context_id:
            raise ValueError("RequestContext must have task_id and context_id")
        if not request_context.message:
            raise ValueError("RequestContext must have a message")

        task_updater = TaskUpdater(event_queue, request_context.task_id, request_context.context_id)
        if not request_context.current_task:
            task_updater.submit()
        task_updater.start_work()
        
        patient_content = types.UserContent(
            parts=self._convert_a2a_parts_to_genai(request_context.message.parts),
        )
        
        await self._process_appointment_request(
            patient_content,
            request_context.context_id,
            task_updater,
        )

    async def cancel(self, request_context: RequestContext, event_queue: EventQueue):
        raise ServerError(error=UnsupportedOperationError())

    async def _get_or_create_session(self, session_id: str):
        """Get existing session or create a new one for the neurologist office."""
        existing_session = await self.agent_runner.session_service.get_session(
            app_name=self.agent_runner.app_name, 
            user_id="neurologist_office", 
            session_id=session_id
        )
        
        if existing_session is None:
            new_session = await self.agent_runner.session_service.create_session(
                app_name=self.agent_runner.app_name,
                user_id="neurologist_office",
                session_id=session_id,
            )
            if new_session is None:
                raise RuntimeError(f"Failed to create session for neurologist office: {session_id}")
            return new_session
            
        return existing_session


    def _convert_a2a_parts_to_genai(self, message_parts: list[Part]) -> list[types.Part]:
        """Convert a list of A2A Part types into a list of Google Gen AI Part types."""
        return [self._convert_a2a_part_to_genai(part) for part in message_parts]

    def _convert_a2a_part_to_genai(self, message_part: Part) -> types.Part:
        """Convert a single A2A Part type into a Google Gen AI Part type."""
        part_root = message_part.root
        
        if isinstance(part_root, TextPart):
            return types.Part(text=part_root.text)
            
        if isinstance(part_root, FilePart):
            if isinstance(part_root.file, FileWithUri):
                return types.Part(
                    file_data=types.FileData(
                        file_uri=part_root.file.uri, 
                        mime_type=part_root.file.mimeType
                    )
                )
            if isinstance(part_root.file, FileWithBytes):
                return types.Part(
                    inline_data=types.Blob(
                        data=part_root.file.bytes.encode("utf-8"),
                        mime_type=part_root.file.mimeType or "application/octet-stream",
                    )
                )
            raise ValueError(f"Unsupported file type in medical request: {type(part_root.file)}")
            
        raise ValueError(f"Unsupported message part type: {type(message_part)}")

    def _convert_genai_parts_to_a2a(self, genai_parts: list[types.Part]) -> list[Part]:
        """Convert a list of Google Gen AI Part types into a list of A2A Part types."""
        return [
            self._convert_genai_part_to_a2a(part)
            for part in genai_parts
            if (part.text or part.file_data or part.inline_data)
        ]

    def _convert_genai_part_to_a2a(self, genai_part: types.Part) -> Part:
        """Convert a single Google Gen AI Part type into an A2A Part type."""
        if genai_part.text:
            return Part(root=TextPart(text=genai_part.text))
            
        if genai_part.file_data:
            if not genai_part.file_data.file_uri:
                raise ValueError("File URI is missing in medical response")
            return Part(
                root=FilePart(
                    file=FileWithUri(
                        uri=genai_part.file_data.file_uri,
                        mimeType=genai_part.file_data.mime_type,
                    )
                )
            )
            
        if genai_part.inline_data:
            if not genai_part.inline_data.data:
                raise ValueError("Inline data is missing in medical response")
            return Part(
                root=FilePart(
                    file=FileWithBytes(
                        bytes=genai_part.inline_data.data.decode("utf-8"),
                        mimeType=genai_part.inline_data.mime_type,
                    )
                )
            )
            
        raise ValueError(f"Unsupported GenAI part type in medical response: {genai_part}")
