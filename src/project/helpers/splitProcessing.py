from __future__ import annotations
from typing import Iterable, Any
from threading import Thread


def splitProcess(process, iter: Iterable, chunks: int, args: Any = None):

    splitSize = len(iter) // chunks
    threads = []

    for i in range(chunks):
        start = i * splitSize
        end = None if i + 1 == chunks else (i + 1) * splitSize

        threads.append(Thread(target=runFunc, args=(process, iter[start:end])))
        threads[-1].start()

    for thread in threads:
        thread = thread.join()

    return threads


def runFunc(func, iter):
    return [func(item) for item in iter]
