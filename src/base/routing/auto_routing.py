import importlib.util
import logging
import os
from fastapi import FastAPI, APIRouter

logger = logging.getLogger(__name__)

def register_all_routers(app: FastAPI, base_path: str, base_module: str):
    """
    Automatically discovers and registers all APIRouter instances from modules in a given directory,
    adding the domain root folder as a tag.
    
    Args:
        app (FastAPI): The FastAPI application instance.
        base_path (str): The filesystem path where router modules are located.
        base_module (str): The base Python module name (e.g., "src.domains").
    """
    logger.info("registering routes from module {base_module}".format(base_module=base_module))
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module_path = os.path.join(root, file)
                
                # Convert file path to a module path (e.g., "src.domains.user")
                relative_path = os.path.relpath(module_path, base_path).replace(os.sep, ".")
                module_name = f"{base_module}.{relative_path[:-3]}"  # Remove ".py"

                try:
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)  # Load the module dynamically

                    # Extract the domain name (root folder) from the relative path
                    domain_name = relative_path.split(".")[0]

                    # If the module has an APIRouter instance, register it with a tag
                    if hasattr(module, "router") and isinstance(module.router, APIRouter):
                        # Add the domain name as a tag to the router
                        module.router.tags = module.router.tags or []
                        if domain_name not in module.router.tags:
                            module.router.tags.append(domain_name)

                        app.include_router(module.router)
                        logger.info(f"✔ Registered router from module: {module_name} with tag: {domain_name}")

                except Exception as e:
                    logger.error(f"❌ Failed to import module {module_name}: {str(e)}")