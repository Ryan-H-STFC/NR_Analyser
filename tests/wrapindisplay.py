from pyvirtualdisplay import Display


def wrapindisplay(func):
    def wrapper(*args, **kwagrs):
        with Display(visible=False) as disp:
            disp.start()
            func(*args, **kwagrs)
            disp.stop()
    return wrapper
