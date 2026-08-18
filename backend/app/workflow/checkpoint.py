from langgraph.checkpoint.postgres import PostgresSaver
from app.core.config import settings

_context = PostgresSaver.from_conn_string(settings.checkpoint_database_url)

checkpointer = _context.__enter__()

checkpointer.setup()