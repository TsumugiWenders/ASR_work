import sys
path = "./testword.txt"   #数据来源
f = open(path, mode='r', encoding='utf-8')
line = f.readline()
list = []
while line:
    a = line.split( )
    b = a[1:]
    list.append(b)
    line = f.readline()
f.close
 
with open('newtestword.txt', 'a') as month_file:    #提取后的数据文件
    for tag in list:
        for i in tag:
            month_file.write(str(i))
            month_file.write(' ')
        month_file.write('\n')
