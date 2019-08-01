import sys

if sys.version_info[:2] < (2, 6):
    # Python 2.5 doesn't have operator.methodcaller, which six
    # relies on in a few places (six doesn't technically support
    # Python 2.5 anymore either but this is one of the only major
    # stumbling blocks)

    # As a special case, also creates emulators for dict.viewkeys
    # dict.viewvalues and dict.viewitems, for which six uses methodcaller,
    # though these are not supported on Python 2.5; this isn't really
    # quite correct, but is sufficient for any cases that are likely to
    # arise

    def methodcaller(name, *args, **kwargs):
        if name in ('viewkeys', 'viewvalues', 'viewitems'):
            name = name[4:]

        def methodcaller(obj):
            return getattr(obj, name)(*args, **kwargs)

        return methodcaller

    import operator
    operator.methodcaller = methodcaller

    from . import six

    # Now that six has been loaded we can get rid of the sneaky monkeypatched
    # operator.methodcaller
    del operator.methodcaller
else:
    from . import six
