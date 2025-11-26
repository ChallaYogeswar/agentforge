"""src/core/observability.py

Provides a lightweight observability layer. If `structlog` and `rich` are
available they will be used; otherwise this module falls back to the
standard library `logging` with a compatible `trace_agent_call` API so the
rest of the app can run without installing optional dependencies.
"""

from datetime import datetime

try:
    import structlog
    from rich.console import Console
    from rich.theme import Theme
    from rich.logging import RichHandler
    import logging

    console = Console(theme=Theme({"logging.level.info": "cyan", "logging.level.error": "bold red"}))

    # Configure structlog + rich for nicer logs
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.BoundLogger,
        logger_factory=structlog.PrintLoggerFactory(console),
    )

    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, show_path=False, markup=True)]
    )

    log = structlog.get_logger()

    def trace_agent_call(agent_name: str, user_input: str, output: str, tokens_used: int = None):
        log.info(
            "agent.invocation",
            agent=agent_name,
            input_preview=user_input[:100] + "..." if len(user_input) > 100 else user_input,
            output_preview=output[:120] + "..." if len(output) > 120 else output,
            tokens=tokens_used or "unknown",
            timestamp=datetime.now().isoformat()
        )
except Exception:
    # Fallback implementation using stdlib logging
    import logging

    log = logging.getLogger("agentforge.observability")
    if not log.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        log.addHandler(handler)
    log.setLevel(logging.INFO)

    def trace_agent_call(agent_name: str, user_input: str, output: str, tokens_used: int = None):
        preview_in = user_input[:100] + "..." if len(user_input) > 100 else user_input
        preview_out = output[:120] + "..." if len(output) > 120 else output
        log.info(
            "agent.invocation - agent=%s input=%s output=%s tokens=%s",
            agent_name,
            preview_in,
            preview_out,
            tokens_used or "unknown"
        )