try:
    import structlog
    import rich.logging
    import logging
    from rich.console import Console

    console = Console()

    structlog.configure(
        processors=[
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    log = structlog.get_logger()

    # Pretty printing for development
    def pretty_log(event: str, **kwargs):
        console.print(f"[bold cyan][{event}][/bold cyan]", kwargs)
except Exception:
    # Fallback to built-in logging when structlog/rich are not installed
    import logging

    log = logging.getLogger("agentforge")
    if not log.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        log.addHandler(handler)
    log.setLevel(logging.INFO)

    def pretty_log(event: str, **kwargs):
        log.info("%s %s", event, kwargs)