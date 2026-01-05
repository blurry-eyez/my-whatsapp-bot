import os
from config import SERVER_DOMAIN

def get_public_link(filename):
    """
    Returns the public link. 
    NOTE: The actual file server is now managed by systemd (pdfserver.service).
    """
    # Simply construct the string. The file is already in the 'reports' folder.
    clean_filename = os.path.basename(filename)
    return f"https://{SERVER_DOMAIN}/{clean_filename}"