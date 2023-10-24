from time import time


def timeme(func):

    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        end = time()
        print(f"{func.__name__} - Time: {end - start}")
        return result

    return wrapper
