from dependency_injector import containers, providers
from src.base.dependencies.di_container import Container as BaseContainer
from src.domains.writer_assistant.services.chat_service import ChatService
from src.domains.writer_assistant.handlers.chat_handler import ChatHandler
from src.domains.writer_assistant.handlers.prompts.generate_prompts import generate_prompts
from src.domains.writer_assistant.services.utils.generate_history_file import generate_docx_file
from src.domains.writer_assistant.services.chat_history_service import ChatHistoryService

class WriterAssistantContainer(containers.DeclarativeContainer):
    """
    Dependency injection container for the Writer Assistant domain.
    """
    # Enable auto-wiring for better compatibility with FastAPI's
    # dependency injection
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.domains.writer_assistant.dependencies.get_chat_service",
            "src.domains.writer_assistant.interfaces.api.v1.controller",
        ]
    )

    chat_history_service = providers.Singleton(
        ChatHistoryService,
        generate_history_file=generate_docx_file,
    )

    chat_handler = providers.Singleton(
        ChatHandler
    )

    chat_service = providers.Singleton(
        ChatService,
        chat_handler=chat_handler,
        generate_prompts=generate_prompts,
    )

def extend_container(base_container: BaseContainer) -> BaseContainer:
    writer_assistant_container = WriterAssistantContainer()# <-- safe override here

    writer_assistant_container.wire(modules=[
        "src.domains.user.dependencies.get_user_service",
        "src.domains.user.interfaces.api.v1.controller",
    ])

    base_container.chat_service = writer_assistant_container.chat_service

    return base_container