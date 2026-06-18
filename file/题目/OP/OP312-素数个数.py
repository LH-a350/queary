'''题目内容​：编程求2到n(n为大于2的正整数)中有多少个素数。

​输入描述​：输入一个正整数n(n<=1000)。

​输出描述​：2到n之间的素数个数。

​输入用例​：

10
​输出用例​：

4'''
#以下为代码部分:
n = int(input())
c = 0
for i in range(2, n):
    for j in range(2, i):
        if i%j == 0:
            break
    else:
        c += 1
print(c)