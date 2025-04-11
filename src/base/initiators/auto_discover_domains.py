from importlib import import_module
from pathlib import Path
from src.base.dependencies.di_container import Container  # our root container

def auto_discover_and_initialize(container: Container):
    domain_root = Path("src/domains")
    # Find all 'di_container.py' files in the domains subdirectories.
    for di_container_path in domain_root.glob("*/dependencies/di_container.py"):
        # Convert the file path into a module path.
        relative_path = di_container_path.relative_to(Path(".")).with_suffix("")
        module_path = str(relative_path).replace("/", ".")
        module = import_module(module_path)
        if hasattr(module, "extend_container"):
            extend_func = getattr(module, "extend_container")
            domain_name, domain_container = extend_func(container)
            # Get the actual DomainsHolder instance and attach the domain.
            setattr(container.domains(), domain_name, domain_container)
    return container