### 第七章作业

运行THCHS30的kaldi 代码，在数据准备阶段，data/train 和 test文件夹中会生成 word.txt 文件，去除第一列 id 标识，使用train作LM model的计数和训练文件，Test做测试。

问题1：使用SRILM 获得经过 interpolation 式的 Kneser Ney 平滑的 3gram 以上的语言模型执行
```shell
ngram-count trainword.text.count -order 3 -lm LM_train -interpolate –kndiscount –debug 1
```
出现以下错误，这是由于数据集太小，导致打折出现负值退出。
```shell
Kneser-Ney smoothing 1-grams
n1 = 5185
n2 = 1059
D = 0.709982
using KneserNey for 2-grams
modifying 2-gram counts for Kneser-Ney smoothing
Kneser-Ney smoothing 2-grams
n1 = 13942
n2 = 298
D = 0.959004
using KneserNey for 3-grams
modifying 3-gram counts for Kneser-Ney smoothing
Kneser-Ney smoothing 3-grams
n1 = 0
n2 = 0
one of required KneserNey count-of-counts is zero
```
问题2：

使用 SRILM SRILM 计算在识别测试集上计算计算在识别测试集上计算 PPL=60.5506

```shell
file textword.text.count: 12969 sentences, 40314 words, 23777 OOVs
10440 zeroprobs, logprob= -33977.87 ppl= 60.5506 ppl1= 374010.2
```