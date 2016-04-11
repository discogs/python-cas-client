# -*- encoding: utf-8 -*-
import six

if six.PY3:
    from .cas_client import *
    from ._version import __version__, __version_info__
else:
    from cas_client import *
    from _version import __version__, __version_info__
