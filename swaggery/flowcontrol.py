'''Exception to "return" a value from the coroutines/endpoints'

These functions are designed to simplify the design of the various endpoints,
transparently making them concurrent via a wrapping coroutine mechanism.

Also, this level of indirection masks the implementation details of the
concurrent mechanism, that might be changed when uWSGI will natively support
asyncio loops.
'''


class Respond(Exception):

    '''A self-rising exception for terminating the coroutine execution.'''

    def __init__(self, status, payload=None):
        super().__init__(self)
        self.status = status
        self.payload = payload
        raise self
