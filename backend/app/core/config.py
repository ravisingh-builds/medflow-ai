from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    checkpoint_database_url: str
    gemini_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

settings = Settings()

#------------------------------------------------------------------
# You actually have two configuration mechanisms working together:
""""
.env
 │
 ├──────────────► Docker environment
 │                       │
 │                       ▼
 │                Pydantic Settings
 │
 └──────────────► Pydantic Settings

# ----------------------------------------------------------------

             Configuration source
                    │
          .env / Docker / cloud
                    │
                    ▼
             config.py
                    │
                    ▼
              settings         
           ▼             ▼
      database.py    checkpoint.py
           │             │
           ▼             ▼
        SQLAlchemy    LangGraph

# Docker compose:
env_file:
  - ./backend/.env

# So Docker makes the environment variables available to your backend container.
# Then pydantic-settings can read those environment variables.
Your laptop
   │
   │ .env
   ▼
Docker container
   │
   │ environment variables
   ▼
Pydantic Settings
   │
   ▼
settings.database_url

"""