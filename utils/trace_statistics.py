import time


def time_tracer(func):
    def on_call(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print('take %s millisecond to call [%s]' % ((end - start) * 1000, func.__name__))
        return res
    return on_call
