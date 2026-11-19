"""Worker lifecycle boundary; API boot does not require optional worker services."""
async def start_workers() -> None:
    return None

async def stop_workers() -> None:
    return None
