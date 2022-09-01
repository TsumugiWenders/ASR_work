### 第七章作业

```text
ngram-count
##功能
#读取分词后的text文件或者count文件，然后用来输出最后汇总的count文件或者语言模型
##参数
#输入文本：
#  -read 读取count文件
#  -text 读取分词后的文本文件
#词典文件：
#  -vocab 限制text和count文件的单词，没有出现在词典的单词替换为<unk>；
#         如果没有加该选项，所有的单词将会被自动加入词典
#  -limit-vocab 只限制count文件的单词（对text文件无效）；
#               没有出现在词典里面的count将会被丢弃
#  -write-vocab 输出词典
#语言模型：
#  -lm 输出语言模型
#  -write-binary-lm 输出二进制的语言模型
#  -sort 输出语言模型gram排序
```

```text
ngram
##功能
#用于评估语言模型的好坏，或者是计算特定句子的得分，用于语音识别的识别结果分析。
##参数
#计算得分：
#  -order 模型阶数，默认使用3阶
#  -lm 使用的语言模型
#  -ppl 后跟需要打分的句子（一行一句，已经分词），ppl表示所有单词，ppl1表示除了</s>以外的单词
#    -debug 0 只输出整体情况
#    -debug 1 具体到句子
#    -debug 2 具体每个词的概率
#产生句子：
#  -gen 产生句子的个数
#  -seed 产生句子用到的random seed
ngram -lm ${lm} -order 3 -ppl ${file} -debug 1 > ${ppl}
```

运行THCHS30的kaldi 代码，在数据准备阶段，data/train 和 test文件夹中会生成 word.txt 文件，去除第一列 id 标识，使用train作LM model的计数和训练文件，Test做测试。

问题1：使用SRILM 获得经过 interpolation 式的 Kneser Ney 平滑的 3gram 以上的语言模型执行

>共有两种训练方法:
>
>1. 训练文本 ——> count文件 ——> lm模型
>2. 训练文本——> lm模型

```shell
#计数功能——生成计数文件
ngram-count -text -order 3 newtrainword.txt -limit-vocab lexicon.txt -no-sos -no-eos -write trainword.text.count –debug 1
```
```shell
#从计数文件构建语言模型
ngram-count -read trainword.text.count -order 3 -lm LM_train -interpolate –kndiscount –debug 1
```
```shell
#直接结合上面两步，接利用训练语料构建语言模型
ngram-count -text newtrainword.txt -order 3  -lm train.lm -interpolate –kndiscount –debug 1
```

问题2：

使用 SRILM SRILM 计算在识别测试集上计算计算在识别测试集上计算 PPL=32266.1
```shell
ngram -ppl testword.text.count -order 3 -lm train.lm 
```

```shell
file testword.text.count: 12025 sentences, 37441 words, 22213 OOVs
2577 zeroprobs, logprob= -111258 ppl= 32266.1 ppl1= 6.22859e+08
```

[^1]:[简话语音识别] 语言模型（一）ngram基础 - Manto的文章 - 知乎](https://zhuanlan.zhihu.com/p/273606445)