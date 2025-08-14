"""This file serves as the main entry point for the application.

It initializes the A2A server, defines the agent's capabilities,
and starts the server to handle incoming requests.
"""

import logging
import os

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent import PulmonologistSchedulingAgent
from agent_executor import PulmonologistSchedulingAgentExecutor
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """Exception for missing API key."""


def main():
    """Entry point for Pulmonologist's Scheduling Agent."""
    host = "localhost"
    port = 10003
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise MissingAPIKeyError("GOOGLE_API_KEY environment variable not set.")

        capabilities = AgentCapabilities(streaming=False)
        skill = AgentSkill(
            id="appointment_availability_checker",
            name="Appointment Availability Checker",
            description="Check the pulmonologist's schedule to see when appointment slots are available.",
            tags=["medical", "appointments", "pulmonology"],
            examples=[
                "Does the pulmonologist have any available appointment slots tomorrow?",
                "Can I schedule an appointment with the pulmonologist next Tuesday at 2pm?",
            ],
        )

        agent_host_url = os.getenv("HOST_OVERRIDE") or f"http://{host}:{port}/"
        agent_card = AgentCard(
            name="Pulmonologist Agent",
            description="A professional agent to help you schedule medical appointments with the pulmonologist.",
            url=agent_host_url,
            version="1.0.0",
            defaultInputModes=PulmonologistSchedulingAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=PulmonologistSchedulingAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        request_handler = DefaultRequestHandler(
            agent_executor=PulmonologistSchedulingAgentExecutor(),
            task_store=InMemoryTaskStore(),
        )
        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )

        uvicorn.run(server.build(), host=host, port=port)

    except MissingAPIKeyError as e:
        logger.error(f"Error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)


if __name__ == "__main__":
    main()
