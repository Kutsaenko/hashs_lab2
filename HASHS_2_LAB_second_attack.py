import hashlib
import random
import csv
import math
from multiprocessing import Pool

def init_r(r_len):
    return random.randbytes(r_len)

def r_function(x, r):

    return x + r

def find_hash(data, n):

    hasher = hashlib.sha3_224()
    hasher.update(data)
    return hasher.digest()[:n]

percentage = 10

def generator_worker(args):

    k_start, k_end, l, r, n = args
    results = []

    for _ in range(k_start, k_end):
        init_val = random.randbytes(n)
        current_val = init_val

        for _ in range(l):
            current_val = find_hash(r_function(current_val, r), n)

        results.append((init_val, current_val))

    return results

def generate_table(k, l, worker_count, r, n):

    pool = Pool(worker_count)
    chunk_size = k // worker_count
    args = [(i * chunk_size, (i + 1) * chunk_size, l, r, n) for i in range(worker_count)]

    results = pool.map(generator_worker, args)
    pool.close()
    pool.join()

    flat_results = [item for sublist in results for item in sublist]
    flat_results.sort(key=lambda x: x[1])
    return flat_results

def binary_search(value, table):

    low, high = 0, len(table) - 1

    while low <= high:
        mid = (low + high) // 2
        if table[mid][1] == value:
            return mid, True
        elif table[mid][1] < value:
            low = mid + 1
        else:
            high = mid - 1

    return -1, False

def find_preimage(l, table, h, r, n):
    current_hash = h

    for j in range(l):
        index, found = binary_search(current_hash, table)
        if found:
            x = table[index][0]
            for _ in range(l - j - 1):
                x = find_hash(r_function(x, r), n)
            return r_function(x, r)

        current_hash = find_hash(r_function(current_hash, r), n)

    raise ValueError

def main():
    n = 2  
    r_len = 16 - n  
    worker_count = 4 
    N = 2**16

    K = [2**10, 2**11, 2**12]
    L = [2**5, 2**6, 2**7]

    for k in K:
        for l in L:
            r = init_r(r_len)
            table = generate_table(k, l, worker_count, r, n)
            teor_otsinka = (1 - math.exp(-k * l**2 / N))*100
            success_count = 0
            test_cases = 10000

            for _ in range(test_cases):
                random_vector = random.randbytes(n)
                h = find_hash(random_vector, n)

                try:
                    preimage = find_preimage(l, table, h, r, n)
                    if find_hash(preimage, n) == h:
                        success_count += 1
                except ValueError:
                    continue

            print("K:", k)
            print("L:", l)
            print(f"Випадковий вектор довжини 256 бітів його геш значення: {random_vector.hex()}")
            print(f"Знайдений прообраз: {preimage.hex()}")
            print(f"Ймовірність успіху: {success_count / test_cases * 100:.2f}%")
            print(f"Теоретичне значення успіху: {teor_otsinka}% \n" )

    # SECOND_ATTACK
    for k in K:
        for l in L:
            r = init_r(r_len)
            table = generate_table(k, l, worker_count, r, n)
            teor_otsinka = 1 - math.exp(-k * l**2 / N)

            for _ in range(10):
                r = init_r(r_len)
                success_count = 0
                test_cases = 10000

                for _ in range(test_cases):
                    random_vector = random.randbytes(n)
                    h = find_hash(random_vector, n)

                    try:
                        preimage = find_preimage(l, table, h, r, n)
                        if find_hash(preimage, n) == h:
                            success_count += 1
                    except ValueError:
                        continue


if __name__ == "__main__":
    main()
