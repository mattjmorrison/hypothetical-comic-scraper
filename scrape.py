#!python

from concurrent.futures import ProcessPoolExecutor as Pool
from funcs import download_series
from config import TITLES


if __name__ == '__main__':
    with Pool(len(TITLES)) as pool:
        pool.map(download_series, TITLES)
    print("Complete")
