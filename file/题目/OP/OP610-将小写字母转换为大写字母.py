'''题目描述
给定一个字符串，将其中所有的小写字母转换成大写字母。

输入
输入一行，包含一个字符串（长度不超过100，可能包含空格）。

输出
输出转换后的字符串。

样例
输入数据 1
helloworld123Ha
输出数据 1
HELLOWORLD123HA
'''
#以下为代码：
s = input()
def t(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
l = []
for i in s:
    l.append(i)
for i in l:
    if t(i):
        continue
    ss = l.index(i)
    l[ss] = i.upper()
print(*l, sep = "")