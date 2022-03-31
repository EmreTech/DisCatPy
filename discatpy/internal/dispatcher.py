"""
The MIT License (MIT)

Copyright (c) 2022-present EmreTech

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import asyncio
from typing import Any, Callable, Coroutine, Optional, TypeVar

__all__ = (
    "Dispatcher",
)

CoroFunc = Callable[..., Coroutine[Any, Any, Any]]

class Dispatcher:
    """
    Runs coroutines based on if an event is dispatched.
    """

    def __init__(self):
        pass

    async def run(self, coro: CoroFunc, name: str, one_shot: bool, *args: Any, **kwargs: Any):
        """
        Runs the given coroutine. Do not run this yourself, `dispatch` takes care of that.

        Parameters
        ----------
        coro: :type:`Callable[..., Coroutine[Any, Any, Any]]`
            The coroutine to run
        name: :type:`str`
            The name of the event
        one_shot: :type:`bool`
            If the event containing the coroutine should be deleted or not
            after execution
        *args: :type:`Any`
            Arguments to pass into the coroutine
        **kwargs: :type:`Any`
            More arguments to pass into the coroutine
        """
        if one_shot:
            self.remove_listener(name)

        try:
            await coro(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception:
            raise

    async def dispatch(self, name: str, *args: Any, **kwargs: Any):
        """
        Dispatches a event. This will trigger the listener's callback
        with the same name and if set, will also trigger the listener's
        overloaded callback.

        Parameters
        ----------
        name: :type:`str`
            The name of the event to dispatch
        *args: :type:`Any`
            Arguments to pass into the event callback
        **kwargs: :type:`Any`
            More arguments to pass into the event callback
        """
        event = getattr(self, name)
        funcs = event.get("callback")
        one_shot = event.get("one_shot", False)

        await self.run(funcs.get("original"), name, one_shot, *args, **kwargs)

        overloaded_func = funcs.get("overloaded")
        if overloaded_func:
            await self.run(overloaded_func, name, one_shot, *args, **kwargs)

    def add_listener(self, func: CoroFunc, overloaded_func: Optional[CoroFunc], name: Optional[str] = None, one_shot: bool = False):
        """
        Adds a new listener for an event. This listener can have an 
        overloaded variant that performs different operations, 
        however it must have the same name and accept the same 
        parameters.

        Parameters
        ----------
        func: :type:`Callable[..., Coroutine[Any, Any, Any]]`
            The callback function for this listener
        overloaded_func: :type:`Optional[Callable[..., Coroutine[Any, Any, Any]]]`
            The (optional) overloaded function for this listener
        name: :type:`Optional[str]`
            The name of this event. If not set, then it uses the name of 
            the callback function
        one_shot: :type:`bool`
            If this event should be deleted or not. Set to False
            by default
        """
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Function provided is not a coroutine.")
        
        if overloaded_func is not None:
            if not asyncio.iscoroutinefunction(overloaded_func):
                raise TypeError("Overloaded function provided is not a coroutine.")
            if not name and (overloaded_func.__name__ != func.__name__):
                raise RuntimeError("Overloaded function does not have the same name as the original function!")

        event_name = func.__name__ if not name else name
        setattr(self, event_name, {"callback": {"original": func, "overloaded": overloaded_func}, "one_shot": one_shot})

    def remove_listener(self, name: str):
        """
        Removes a listener for an event.

        Parameters
        ----------
        name: :type:`str`
            The name of the listener to remove
        """
        delattr(self, name)
    
