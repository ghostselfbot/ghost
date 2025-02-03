"""
This module contains runtime hooks that are used to suppress warnings and other runtime issues
"""

import warnings


def suppress_imk_warnings() -> None:
    """
    Suppresses the warnings that are raised by the Input Method Kit (IMK) on macOS/Linux.
    """
    warnings.filterwarnings(
        "ignore", category=UserWarning, message=r".*IMKClient_Legacy.*"
    )
    warnings.filterwarnings(
        "ignore", category=UserWarning, message=r".*IMKInputSession_Legacy.*"
    )


suppress_imk_warnings()
