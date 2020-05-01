import concurrent.futures


def map_threads(func, _iterable):
    """Map function with iterable object in using thread pools."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = executor.map(func, _iterable)
    return result


def map_processes(func, _iterable):
    """Map function with iterable object in using process pools."""
    with concurrent.futures.ProcessPoolExecutor() as executor:
        result = executor.map(func, _iterable)
    return result
