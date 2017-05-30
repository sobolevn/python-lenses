from .. import hooks
from .. import typeclass

from .base import *


def multiap(func, *args):
    '''Applies `func` to the data inside the `args` functors
    incrementally. `func` must be a curried function that takes
    `len(args)` arguments.

        >>> func = lambda a: lambda b: a + b
        >>> multiap(func, [1, 10], [100])
        [101, 110]
    '''
    functor = typeclass.fmap(args[0], func)
    for arg in args[1:]:
        functor = typeclass.apply(arg, functor)
    return functor


def collect_args(n):
    '''Returns a function that can be called `n` times with a single
    argument before returning all the args that have been passed to it
    in a tuple. Useful as a substitute for functions that can't easily be
    curried.

        >>> collect_args(3)(1)(2)(3)
        (1, 2, 3)
    '''
    args = []

    def arg_collector(arg):
        args.append(arg)
        if len(args) == n:
            return tuple(args)
        else:
            return arg_collector

    return arg_collector


class BothTraversal(Traversal):
    '''A traversal that focuses both items [0] and [1].

        >>> BothTraversal()
        BothTraversal()
        >>> BothTraversal().to_list_of([1, 2, 3])
        [1, 2]
        >>> BothTraversal().set([1, 2, 3], 4)
        [4, 4, 3]
    '''

    def func(self, f, state):
        def multisetter(items):
            s = hooks.setitem_immutable(state, 0, items[0])
            s = hooks.setitem_immutable(s, 1, items[1])
            return s

        f0 = f(state[0])
        f1 = f(state[1])
        return typeclass.fmap(multiap(collect_args(2), f0, f1), multisetter)

    def __repr__(self):
        return 'BothTraversal()'


class EachTraversal(Traversal):
    '''A traversal that iterates over its state, focusing everything it
    iterates over. It uses `lenses.hooks.fromiter` to reform the state
    afterwards so it should work with any iterable that function
    supports. Analogous to `iter`.

        >>> from lenses import lens
        >>> state = [1, 2, 3]
        >>> EachTraversal()
        EachTraversal()
        >>> EachTraversal().to_list_of(state)
        [1, 2, 3]
        >>> EachTraversal().over(state, lambda n: n + 1)
        [2, 3, 4]

    For technical reasons, this lens iterates over dictionaries by their
    items and not just their keys.

        >>> state = {'one': 1}
        >>> EachTraversal().to_list_of(state)
        [('one', 1)]
    '''

    def func(self, f, state):
        items = list(hooks.to_iter(state))

        def build_new_state_from_iter(a):
            return hooks.from_iter(state, a)

        if items == []:
            return f.pure(build_new_state_from_iter(items))

        collector = collect_args(len(items))
        applied = multiap(collector, *map(f, items))
        return typeclass.fmap(applied, build_new_state_from_iter)

    def __repr__(self):
        return 'EachTraversal()'


class GetZoomAttrTraversal(Traversal):
    '''A traversal that focuses an attribute of an object, though if
    that attribute happens to be a lens it will zoom the lens. This
    is used internally to make lenses that are attributes of objects
    transparent. If you already know whether you are focusing a lens or
    a non-lens you should be explicit and use a ZoomAttrTraversal or a
    GetAttrLens respectively.
    '''

    def __init__(self, name):
        from lenses.optics import GetattrLens
        self.name = name
        self._getattr_cache = GetattrLens(name)

    def func(self, f, state):
        attr = getattr(state, self.name)
        try:
            sublens = attr._underlying_lens()
        except AttributeError:
            sublens = self._getattr_cache
        return sublens.func(f, state)

    def __repr__(self):
        return 'GetZoomAttrTraversal({!r})'.format(self.name)



class ItemsTraversal(Traversal):
    '''A traversal focusing key-value tuples that are the items of a
    dictionary. Analogous to `dict.items`.

        >>> from collections import OrderedDict
        >>> state = OrderedDict([(1, 10), (2, 20)])
        >>> ItemsTraversal()
        ItemsTraversal()
        >>> ItemsTraversal().to_list_of(state)
        [(1, 10), (2, 20)]
        >>> ItemsTraversal().over(state, lambda n: (n[0], n[1] + 1))
        OrderedDict([(1, 11), (2, 21)])
    '''

    def func(self, f, state):
        items = list(state.items())
        if items == []:
            return f.pure(state)

        def dict_builder(args):
            data = state.copy()
            data.clear()
            data.update(a for a in args if a is not None)
            return data

        collector = collect_args(len(items))
        return typeclass.fmap(multiap(collector, *map(f, items)), dict_builder)

    def __repr__(self):
        return 'ItemsTraversal()'


class ZoomAttrTraversal(Traversal):
    '''A lens that looks up an attribute on its target and follows it as
    if were a bound `Lens` object. Ignores the state, if any, of the
    lens that is being looked up.
    '''

    def __init__(self, name):
        # type: (str) -> None
        self.name = name

    def func(self, f, state):
        l = getattr(state, self.name)
        return l._underlying_lens().func(f, state)

    def __repr__(self):
        return 'ZoomAttrTraversal({!r})'.format(self.name)


class ZoomTraversal(Traversal):
    '''Follows its state as if it were a bound `Lens` object.

        >>> from lenses import lens
        >>> ZoomTraversal()
        ZoomTraversal()
        >>> state = lens([1, 2])[1]
        >>> ZoomTraversal().view(state)
        2
        >>> ZoomTraversal().set(state, 3)
        [1, 3]
    '''

    def func(self, f, state):
        return state._underlying_lens().func(f, state._state)

    def __repr__(self):
        return 'ZoomTraversal()'
