import math
import random

# documentation

def eulerHelp():
    return """\
gcd(*arg)               greatest common divisor of all args
extendedGcd(a, b)       (x, y, gcd) such that ax + by = gcd
modInv(n, m)            multiplicative inverse of n mod m
crt(x, m, y, n, ...)    solve for a: a = x (mod m), a = y (mod n), ...
sieve(n)                sieve for primes (void return)
primeList()             return list of primes after sieve
isPrime(n)              is n prime?
isPrimeList()           return array v such that v[n] = isPrime(n)
probablePrime(n, k=30)  run Miller-Rabin primality test k times
factorize(n)            return a map from primes to exponents
                            in the prime factorization of n
primeExponents(n)       return the exponents of the prime factorization of n
                            if n includes a prime larger than the sieve size,
                            result[-1] will be 0
pollardRho(n, x=None)   attempts to find a non-trivial divisor of n using
                            Pollard's rho algorithm using x as the starting
                            value, return None if failed, if x is not given,
                            it is chosen randomly
divisors(n, s)          return a list of the divisors of n
                            sort if s is true
sigma(n, k)             return sum[d|n] d^k
omega(n, k)             return sum[p^e||n, e != 0] e^k
totient(n)              return the totient of n
mobius(n)               return the mobius of n
radical(n)              return the radical of n

factorial(n)            return the factorial of n
permute(n, r)           return n permute r
choose(n, r)            return n choose r
multinom(*v) or (v)     return the multinomial coefficient given a list v

toBase(n, b)            return an integer n as a string in base b
nextPermutation(v)      return the next permutation of v
prevPermutation(v)      return the previous permutation of v\
"""

# To add:
# general sieve algorithm (divisor and prime)
# specific sieves for divisor sums, totient, etc.
# Jordan totient and totient summatory functions
# prime pi function
# maybe sum[0 < d <= n] floor(n / d) f(d)


# number theory

def gcd(*arg):
    if len(arg) == 2:
        a, b = arg
        if a < 0:
            a = -a
        if b < 0:
            b = -b
        
        while a != 0 and b != 0:
            a, b = b, a%b
        return a+b
    
    r = gcd(arg[0], arg[1])
    for i in range(2, len(arg)):
        r = gcd(r, arg[i])
    return r

def extendedGcd(a, b):
    x, y, u, v = 0, 1, 1, 0
    while a != 0:
        q, r = b//a, b%a
        m, n = x-u*q, y-v*q
        b, a, x, y, u, v = a, r, u, v, m, n
        
    return x, y, b

def modInv(n, m):
    return extendedGcd(n, m)[0] % m

def crt(x, m, y, n, *args):
    if (len(args) == 0):
        return (x * n * modInv(n, m) + y * m * modInv(m, n)) % (m * n)
    else:
        return crt(crt(x, m, y, n), m*n, *args)

_isPrime = []
_primes = []
    
def sieve(n=1000000):
    global _isPrime, _primes
    _isPrime = [True] * n
    _isPrime[0] = _isPrime[1] = False
    
    i = 2
    while i*i < n:
        if _isPrime[i]:
            j = i*i
            while j < n:
                _isPrime[j] = False
                j += i
        i += 1
        
    _primes = []
    for i in range(n):
        if _isPrime[i]:
            _primes.append(i)

def primeList():
    global _primes
    if len(_primes) < 10:
        sieve()
    return _primes

def isPrime(n):
    global _isPrime
    if len(_isPrime) < 10:
        sieve()
    if n < 0:
        return False
    if n < len(_isPrime):
        return _isPrime[n]
    return sigma(n, 0) == 2

def isPrimeList():
    global _isPrime
    if len(_isPrime) < 10:
        sieve()
    return _isPrime

def _preProbablePrime(n, v):
    for d in v:
        if n % d == 0:
            return False
    return True

def probablePrime(n, k=30):
    smallPrimes = [2, 3, 5, 7, 11, 13, 17]
    if n in smallPrimes:
        return True
    if n < 2 or not _preProbablePrime(n, smallPrimes):
        return False

    d = n - 1
    r = 0

    while d % 2 == 0:
        d //= 2
        r += 1

    for i in range(k):
        a = random.randint(2, n-2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        composite = True
        for _ in range(r-1):
            x = x * x % n
            if x == n - 1:
                composite = False
                break
        if composite:
            return False
    return True

def factorize(n):
    primes = primeList()
    primeV = isPrimeList()
    
    r = {}
    for p in primes:
        if p ** 2 > n:
            break
        if n < len(primeV) and primeV[n]:
            break
        while n % p == 0:
            r[p] = r.get(p, 0) + 1
            n //= p
    if n != 1:
        f = rhoFactorize(n)
        for x in f:
            r[x] = r.get(x, 0) + f[x]
    return r

def primeExponents(n):
    primes = primeList()
    
    r = []
    for p in primes:
        r.append(0)
        while n % p == 0:
            r[-1] += 1
            n //= p
        if n == 1:
            break
    if n != 1:
        r.append(0)
    return r

def divisors(n, sort=True):
    if type(n) is int:
        return divisors(factorize(n))
    if len(n) == 0:
        return [1]
    
    p = next(iter(n))
    e = n[p]
    
    del n[p]
    rec = divisors(n, False)
    n[p] = e
    
    r = [d * p**i for d in rec for i in range(e+1)]
    
    if sort:
        r.sort()
    return r
    

def pollardRho(n, x=None):
    if n < 0: n = -n
    if n < 10**4:
        if n < 2 or isPrime(n):
            return None
        return next(iter(factorize(n)))

    if x == None:
        x = random.randint(2, n-2)

    def g(z):
        return (z**2 + 1) % n

    y = x
    d = 1

    while d == 1:
        x = g(x)
        y = g(g(y))
        d = gcd(abs(x-y), n)

    if d == n:
        return None
    return d

def rhoFactorize(n):
    if n == 1:
        return {}
    if probablePrime(n):
        return {n: 1}
    a = None
    while a == None:
        a = pollardRho(n)
    f = rhoFactorize(a)
    g = rhoFactorize(n//a)
    r = {}
    for x in f:
        r[x] = r.get(x, 0) + f[x]
    for x in g:
        r[x] = r.get(x, 0) + g[x]
    return r


def sigma(n, k):
    v = factorize(n)
    r = 1
    for p, e in v.items():
        if k != 0:
            r *= (p ** (k*(e+1)) - 1) // (p**k - 1)
        else:
            r *= e+1
    return r


def omega(n, k):
    v = factorize(n)
    r = 0
    for p, e in v.items(): 
        r += e ** k
    return r
    
def totient(n):
    v = factorize(n)
    r = n
    for p, e in v.items():
        r *= p-1
        r //= p
    return r

def mobius(n):
    r = 1
    v = factorize(n)
    for p, e in v.items():
        if e > 1:
            return 0
        r *= -1
    return r
    
def radical(n):
    v = factorize(n)
    r = 1
    for p in v:
        r *= p
        
    return r

    
# combinatorics

def factorial(n):
    r = 1
    for i in range(1, n+1):
        r *= i
    return r

def choose(n, r):
    if 2*r > n:
        return choose(n, n-r)
    if r < 0:
        return 0
    
    res = 1
    
    for i in range(0, r):
        res *= n-i
        res //= i+1
    
    return res

def permute(n, r):
    res = 1
    for i in range(n-r+1, n+1):
        res *= i
    return res

def multinom(*v):
    if len(v) == 1: v = v[0]
    j = v.index(max(v))
    r = permute(sum(v), sum(v) - v[j])
    for i in range(len(v)):
        if i != j:
            r //= factorial(v[i])
    return r


# computer science

def toBase(n, b):
    res = ""
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    while n > 0:
        res += digits[n % b]
        n //= b
    return res[::-1]

def nextPermutation(v):
    i = len(v) - 1
    while i > 0 and v[i-1] >= v[i]:
        i = i - 1
    if i <= 0:
        v[:] = v[::-1]
        return False

    j = len(v) - 1
    while v[j] <= v[i-1]:
        j = j - 1
    v[i-1], v[j] = v[j], v[i-1]

    v[i:] = v[len(v)-1 : i-1 : -1]
    return True

def prevPermutation(v):
    i = len(v) - 1
    while i > 0 and v[i-1] <= v[i]:
        i = i - 1
    if i <= 0:
        v[:] = v[::-1]
        return False

    j = len(v) - 1
    while v[j] >= v[i-1]:
        j = j - 1
    v[i-1], v[j] = v[j], v[i-1]

    v[i:] = v[len(v)-1 : i-1 : -1]
    return True

