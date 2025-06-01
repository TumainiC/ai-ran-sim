def get_first_paragraph(text: str) -> str:
    return text.split('\n\n')[0] if text else ''

def bytes_pretty_printer(service_disk_size_bytes: int) -> str:
    # Handle negative or None input gracefully
    if service_disk_size_bytes is None or service_disk_size_bytes < 0:
        return "N/A"
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(service_disk_size_bytes)
    for unit in units:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"