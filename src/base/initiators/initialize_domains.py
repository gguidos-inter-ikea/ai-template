import importlib.util
import os
from src.base.dependencies.di_container import Container as BaseContainer
from src.base.config.config import settings
import logging

logger = logging.getLogger(
    settings.textsNew.initializers.domains["logger_name"]
)

def initialize_domains(container: BaseContainer) -> BaseContainer:
    """
    Automatically discover and initialize all domain-specific containers
    by extending the base container.
    
    Args:
        container: The base container to extend
        
    Returns:
        The extended container with all domain-specific dependencies
    """
    domains_path = os.path.abspath("src/domains")  # Path to the `src/domains/` directory
    base_module = "src.domains"

    for root, _, files in os.walk(domains_path):
        for file in files:
            if file == "di_container.py":
                module_path = os.path.join(root, file)
                
                # Convert file path to a module path (e.g., "src.domains.user.dependencies.di_container")
                relative_path = os.path.relpath(module_path, domains_path).replace(os.sep, ".")
                module_name = f"{base_module}.{relative_path[:-3]}"  # Remove ".py"

                logger.info(
                    settings.textsNew.initializers.domains["initializing_di"]
                    .format(domains_path=module_name)
                )

                try:
                    # Dynamically import the module
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Check if the module has an `extend_container` function
                    if hasattr(module, "extend_container"):
                        extend_container = getattr(module, "extend_container")
                        container = extend_container(container)  # Extend the base container
                        
                        logger.info(
                            settings.textsNew.initializers.domains["extended_container"]
                            .format(module_name=module_name)
                        )

                except Exception as e:
                    logger.info(
                        settings.textsNew.initializers.domains["extended_container_error"]
                        .format(module_name=module_name, error=str(e))
                    )

    return container