# Property-Based Configuration System

## Overview

The property-based configuration system provides a flexible, environment-aware way to manage application settings. Inspired by Spring Boot's property management, this system allows for different configuration profiles and supports multiple sources of configuration with a clear precedence order.

## Key Features

- **Immutable Configuration**: Once loaded, configuration settings are immutable, preventing accidental changes during runtime.
- **Profile-Based Loading**: Different environments (development, docker, production) can have specific configurations.
- **Multiple Sources**: Configuration can come from environment variables, property files, and defaults.
- **Clear Precedence**: Environment variables override profile-specific properties, which override base properties.
- **Type Safety**: Pydantic models ensure type validation and conversion.

## File Structure

The configuration system uses three main property files:

1. **application.properties**: Base configuration with default values.
   - Located at: `src/main/resources/application.properties`
   - Contains default values for all settings
   - Used as a fallback when settings are not defined elsewhere

2. **application-{profile}.properties**: Profile-specific configuration.
   - Examples: `application-docker.properties`, `application-dev.properties`
   - Located at: `src/main/resources/application-{profile}.properties`
   - Override settings from the base properties file

3. **application-dev.properties**: Local development configuration (not in git).
   - Template available at: `src/main/resources/application-dev.properties.template`
   - Should be copied to `src/main/resources/application-dev.properties` for local development
   - Contains sensitive information like API keys and passwords
   - Added to `.gitignore` to prevent committing sensitive data

## How It Works

### PropertyManager

The `PropertyManager` class is responsible for loading and managing properties:

```python
class PropertyManager:
    @staticmethod
    def load_properties(active_profiles=None):
        # Load base properties
        base_props = PropertyManager._load_property_file("application.properties")
        
        # Load profile-specific properties
        profile_props = {}
        if active_profiles:
            for profile in active_profiles:
                profile_file = f"application-{profile}.properties"
                profile_props.update(PropertyManager._load_property_file(profile_file))
        
        # Merge properties with precedence: env vars > profile props > base props
        merged_props = {**base_props, **profile_props}
        
        # Override with environment variables
        for key in merged_props:
            env_key = key.replace(".", "_").upper()
            if env_key in os.environ:
                merged_props[key] = os.environ[env_key]
        
        # Convert to Settings object
        return Settings(**merged_props)
```

### Settings Model

The `Settings` class is a Pydantic model that defines all configuration properties with their types:

```python
class Settings(BaseModel):
    # General settings
    project_name: str = "API Project"
    application_name: str = "FastAPI App"
    application_owner: str = "Development Team"
    application_owner_email: str = "dev@example.com"
    environment: str = "development"
    api_key: str = "dev_api_key_change_in_production"
    port: int = 8000
    log_level: str = "INFO"
    allowed_admin_ips: List[str] = ["127.0.0.1", "::1"]
    
    # ... other settings ...
    
    model_config = ConfigDict(frozen=True)  # Make settings immutable
```

## Usage

### Loading Configuration

To load the configuration in your application:

```python
from src.base.config.property_manager import PropertyManager

# Determine active profiles (from environment variable or default)
active_profiles = os.environ.get("SPRING_PROFILES_ACTIVE", "dev").split(",")

# Load settings
settings = PropertyManager.load_properties(active_profiles)
```

### Accessing Configuration

Once loaded, you can access configuration values as attributes:

```python
# Access a string property
app_name = settings.application_name

# Access a numeric property
port = settings.port

# Access a list property
admin_ips = settings.allowed_admin_ips
```

### Docker Integration

For Docker environments:

1. Set the `SPRING_PROFILES_ACTIVE` environment variable to `docker` in your `docker-compose.yml`:
   ```yaml
   environment:
     - SPRING_PROFILES_ACTIVE=docker
   ```

2. Pass environment variables to override specific settings:
   ```yaml
   environment:
     - MONGODB_URI=mongodb://mongo:27017
     - REDIS_HOST=redis
   ```

## Environment Variables

Environment variables take precedence over property files. The naming convention is:
- Convert property name to uppercase
- Replace dots (`.`) with underscores (`_`)

Examples:
- `mongodb.uri` → `MONGODB_URI`
- `jwt.secret.key` → `JWT_SECRET_KEY`
- `email.smtp.server` → `EMAIL_SMTP_SERVER`

## Best Practices

1. **Sensitive Information**: Never commit sensitive information to git. Use environment variables or the `application-dev.properties` file (which should be in `.gitignore`).

2. **Default Values**: Always provide sensible default values in `application.properties`.

3. **Documentation**: Document all configuration properties, especially those that affect security or performance.

4. **Validation**: Use Pydantic validators to ensure configuration values are valid.

5. **Testing**: Create test configurations to verify your application works with different settings.

## Troubleshooting

### Common Issues

1. **Missing Properties**: If a required property is missing, Pydantic will raise a validation error. Check that all required properties are defined in at least one of: environment variables, profile properties, or base properties.

2. **Type Conversion Errors**: Pydantic attempts to convert values to the expected type. If conversion fails, it raises a validation error. Ensure property values match their expected types.

3. **Environment Variables Not Applied**: Check that environment variable names follow the correct convention (uppercase with underscores).

4. **Profile Not Loaded**: Verify that the `SPRING_PROFILES_ACTIVE` environment variable is set correctly.

### Debugging

To debug configuration loading, you can temporarily add logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("config")

# In PropertyManager.load_properties:
logger.debug(f"Base properties: {base_props}")
logger.debug(f"Profile properties: {profile_props}")
logger.debug(f"Merged properties: {merged_props}")
```

## Migration Guide

If you're migrating from an older configuration system:

1. Identify all configuration sources in your application
2. Map them to the appropriate property files
3. Update code to use the PropertyManager
4. Test thoroughly with different profiles

For Pydantic v1 to v2 migration:
- Replace `class Config` with `model_config = ConfigDict(...)`
- Replace `frozen=True` with `frozen=True` in ConfigDict
- Update any validators to use the new decorator syntax 