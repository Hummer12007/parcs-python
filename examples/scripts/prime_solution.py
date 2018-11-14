# import gmpy2
from Pyro4 import expose
import random


class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers
        print("Inited")

    def solve(self):
        print("Job Started")
        print("Workers %d" % len(self.workers))

        (n, k) = self.read_input()
        a = 1 << n
        b = 1 << (n + 1)
        step_n = (b - a) / len(self.workers)
        step_k = k / len(self.workers)

        # map
        mapped = []
        for i in xrange(0, len(self.workers)):
            print("map %d" % i)
            mapped.append(self.workers[i].mymap(str(a + i * step_n), str(a + (i + 1) * step_n), step_k))

        # reduce
        primes = self.myreduce(mapped)

        # output
        self.write_output(primes)

        print("Job Finished")

    @staticmethod
    @expose
    def mymap(a, b, count):
        print(a)
        print(b)
        print(count)
        a = int(a)
        b = int(b)
        primes = []

        if a % 2 == 0:
            a += 1

        while len(primes) < count and a < b:
            if Solver.is_probable_prime(a):
                primes.append(str(a))
            a += 2

        return primes

    @staticmethod
    @expose
    def myreduce(mapped):
        print("reduce")
        output = []

        for primes in mapped:
            print("reduce loop")
            output = output + primes.value
        print("reduce done")
        return output

    def read_input(self):
        f = open(self.input_file_name, 'r')
        n = int(f.readline())
        k = int(f.readline())
        f.close()
        return n, k

    def write_output(self, output):
        f = open(self.output_file_name, 'w')
        f.write(', '.join(output))
        f.write('\n')
        f.close()
        print("output done")

    @staticmethod
    @expose
    def is_probable_prime(n):
        """
        Miller-Rabin primality test.

        A return value of False means n is certainly not prime. A return value of
        True means n is very likely a prime.

        >>> is_probable_prime(1)
        Traceback (most recent call last):
            ...
        AssertionError
        >>> is_probable_prime(2)
        True
        >>> is_probable_prime(3)
        True
        >>> is_probable_prime(4)
        False
        >>> is_probable_prime(5)
        True
        >>> is_probable_prime(123456789)
        False

        >>> primes_under_1000 = [i for i in range(2, 1000) if is_probable_prime(i)]
        >>> len(primes_under_1000)
        168
        >>> primes_under_1000[-10:]
        [937, 941, 947, 953, 967, 971, 977, 983, 991, 997]

        >>> is_probable_prime(6438080068035544392301298549614926991513861075340134\
    3291807343952413826484237063006136971539473913409092293733259038472039\
    7133335969549256322620979036686633213903952966175107096769180017646161\
    851573147596390153)
        True

        >>> is_probable_prime(7438080068035544392301298549614926991513861075340134\
    3291807343952413826484237063006136971539473913409092293733259038472039\
    7133335969549256322620979036686633213903952966175107096769180017646161\
    851573147596390153)
        False
        """
        assert n >= 2
        # special case 2
        if n == 2:
            return True
        # ensure n is odd
        if n % 2 == 0:
            return False
        # write n-1 as 2**s * d
        # repeatedly try to divide n-1 by 2
        s = 0
        d = n - 1
        while True:
            quotient, remainder = divmod(d, 2)
            if remainder == 1:
                break
            s += 1
            d = quotient
        assert (2 ** s * d == n - 1)

        # test the base a to see whether it is a witness for the compositeness of n
        def try_composite(a):
            if pow(a, d, n) == 1:
                return False
            for i in range(s):
                if pow(a, 2 ** i * d, n) == n - 1:
                    return False
            return True  # n is definitely composite

        for i in range(1):
            a = random.randrange(2, n)
            if try_composite(a):
                return False

        return True  # no base tested showed n as composite
