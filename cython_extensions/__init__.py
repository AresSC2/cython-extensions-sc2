__version__ = "0.8.11"

# bootstrap is the only module which
# can be loaded with default Python-machinery
# because the resulting extension is called `bootstrap`:
from . import bootstrap

# injecting our finders into sys.meta_path
# after that all other submodules can be loaded
bootstrap.bootstrap_cython_submodules()

# Import configuration functions from the safe module
from cython_extensions.type_checking import (
    enable_safe_mode,
    disable_safe_mode,
    is_safe_mode_enabled,
    get_safe_mode_status,
    safe_mode_context,
)

# Import all functions from the safe wrappers module
# These handle the conditional validation internally
from cython_extensions.type_checking.wrappers import *
