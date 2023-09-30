---
Author: Chat GPT (August 3 version)
tags:
  - CPP
  - DSA/Algorithms
  - Python
---

## C++
```cpp
void Find_Factor(int n, int k) {
    // 1 is always a factor
    ans.push_back(1); 
    // Start from 2 for even n, 3 for odd n
    int start = (n % 2 == 0) ? 2 : 3; 
    for (int f = start; f <= sqrt(n); f += 2) {
        if (n % f == 0) {
            ans.push_back(f);
            if (f != n / f) {
                ans.push_back(n / f);
            }
        }
    }
    if (ans.size() < k) {
        cout << 1;
    } else {
        cout << ans[k - 1];
    }
}

```

## Python
```py
import math

def find_factor(n, k):
    ans = [1]  # 1 is always a factor
    for f in range(2, math.isqrt(n) + 1):
        if n % f == 0:
            ans.extend([f, n // f] if f != n // f else [f])
    
    return ans[k - 1] if k <= len(ans) else 1

# Example usage:
n = int(input("Enter a number: "))
k = int(input("Enter k: "))
result = find_factor(n, k)
print(f"The {k}-th smallest factor of {n} is: {result}")

```

## Time complexity = `O(sqrt(n))`
The time complexity of the Find_Factor() function is: $\mathcal{O}(\sqrt{n})$ 



