# -*- encoding: utf-8 -*-
import six


if six.PY3:
    from .cas_client import *
else:
    from cas_client import *
