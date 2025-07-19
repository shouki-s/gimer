"""Internationalization utilities for gimer."""

import gettext
from pathlib import Path

# Initialize gettext
LOCALE_DIR = Path(__file__).parent / "locale"
gettext.bindtextdomain("gimer", str(LOCALE_DIR))
gettext.textdomain("gimer")

# Create translation function
_ = gettext.gettext
