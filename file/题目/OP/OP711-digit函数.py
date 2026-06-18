'''题目描述
在程序中定义一函数digit(n,k)，它能分离出整数n从右边数第k个数字。

输入
正整数n和k。

输出
一个数字。

样例
输入数据 1
31859 3
输出数据 1
8'''
#以下为代码部分
n, k = input().split()
k = int(k)
l = list(n)
l.reverse()
n = ""
for i in l:
    n += i
ii = 0
for i in n:
    ii += 1
    if k == ii:
        print(i)
        break