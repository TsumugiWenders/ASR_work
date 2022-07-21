# Author: Sining Sun , Zhanheng Yang

import numpy as np
from utils import *
import scipy.cluster.vq as vq

num_gaussian = 5
num_iterations = 5


class GMM:
    # 1.GMM的初始化方法
    def __init__(self, D, K=5):
        assert(D>0)
        self.dim = D #MFCC 39维数据特征
        self.K = K #要形成的簇数以及要生成的质心数,即num_gaussian
        #Kmeans Initial
        self.mu , self.sigma , self.pi = self.kmeans_initial()

    # 2.使用kmeans聚类方法获得初始化参数
    def kmeans_initial(self):
        mu = []
        sigma = []
        data = read_all_data('train/feats.scp') # 句子id到特征数据真实路径和位置的映射
        (centroids, labels) = vq.kmeans2(data, self.K, minit="points", iter=100)
        clusters = [[] for i in range(self.K)]
        for (l,d) in zip(labels,data):
            clusters[l].append(d)

        for cluster in clusters:
            mu.append(np.mean(cluster, axis=0))
            sigma.append(np.cov(cluster, rowvar=0))
        pi = np.array([len(c)*1.0 / len(data) for c in clusters]) #每一类占总体的比重
        return mu , sigma , pi
    # 3.计算高斯混合分布 p10
    def gaussian(self , x , mu , sigma):
        """Calculate gaussion probability.
    
            :param x: The observed data, dim*1.
            :param mu: The mean vector of gaussian, dim*1
            :param sigma: The covariance matrix, dim*dim
            :return: the gaussion probability, scalor
        """
        D=x.shape[0]
        det_sigma = np.linalg.det(sigma)
        inv_sigma = np.linalg.inv(sigma)
        mahalanobis = np.dot(np.transpose(x-mu), inv_sigma)
        mahalanobis = np.dot(mahalanobis, (x-mu))
        const = 1/((2*np.pi)**(D/2))
        return const * (det_sigma)**(-0.5) * np.exp(-0.5 * mahalanobis)
    # 4.计算对数似然函数 p12
    def calc_log_likelihood(self, X):
        """Calculate log likelihood of GMM
            param: X: A matrix including data samples, num_samples * D
            return: log likelihood of current model 
        """
        log_llh = 0.0
        """
            FINISH by YOUSELF
        """
        N = X.shape[0]

        log_llh = np.sum([np.log(
            np.sum([self.pi[k] * self.gaussian(X[n], self.mu[k], self.sigma[k]) for k in range(self.K)])
        ) for n in range(N)])
        return log_llh

    # 5.EM算法实现 p13
    def em_estimator(self, X):
        """Update paramters of GMM
            param: X: A matrix including data samples, num_samples * D
            return: log likelihood of updated model 
        """

        log_llh = 0.0
        """
            FINISH by YOUSELF
        """
        N = X.shape[0]
        print(N)
        samgauss = [np.zeros(self.K) for i in range(N)]  # 构造样本和高斯函数的列表[N,(K,)]

        # E-step：计算后验概率
        for n in range(N):
            postprob = [self.pi[k] * self.gaussian(X[n], self.mu[k], self.sigma[k]) for k in range(self.K)]
            postprob = np.array(postprob)
            postprob_sum = np.sum(postprob)
            samgauss[n] = postprob / postprob_sum 
            # pdb.set_trace()

        # M-step：更新参数值
        for k in range(self.K):
            Nk = np.sum([samgauss[n][k] for n in range(N)])
            if Nk == 0:
                continue
            self.pi[k] = Nk / N
            self.mu[k] = (1.0 / Nk) * np.sum([samgauss[n][k] * X[n] for n in range(N)], axis=0)
            diffs = X - self.mu[k]
            self.sigma[k] = (1.0 / Nk) * np.sum(
                [samgauss[n][k] * diffs[n].reshape(self.dim, 1) * diffs[n] for n in range(N)],
                axis=0)
        log_llh = self.calc_log_likelihood(X)

        return log_llh


def train(gmms, num_iterations = num_iterations):
    dict_utt2feat, dict_target2utt = read_feats_and_targets('train/feats.scp', 'train/text')
    
    for target in targets:
        feats = get_feats(target, dict_utt2feat, dict_target2utt)
        for i in range(num_iterations): #训练迭代次数 5
            log_llh = gmms[target].em_estimator(feats)
    return gmms

def test(gmms):
    correction_num = 0
    error_num = 0
    acc = 0.0
    dict_utt2feat, dict_target2utt = read_feats_and_targets('test/feats.scp', 'test/text')
    dict_utt2target = {}
    for target in targets:
        utts = dict_target2utt[target]
        for utt in utts:
            dict_utt2target[utt] = target
    for utt in dict_utt2feat.keys():
        feats = kaldi_io.read_mat(dict_utt2feat[utt])
        scores = []
        for target in targets:
            scores.append(gmms[target].calc_log_likelihood(feats))
        predict_target = targets[scores.index(max(scores))]
        if predict_target == dict_utt2target[utt]:
            correction_num += 1
        else:
            error_num += 1
    acc = correction_num * 1.0 / (correction_num + error_num)
    return acc

targets = ['Z', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'O']

def main():
    gmms = {}
    for target in targets:
        gmms[target] = GMM(39, K=num_gaussian) #39维mfcc特征
    gmms = train(gmms)
    acc = test(gmms)
    print('Recognition accuracy: %f' % acc)
    fid = open('acc.txt', 'w')
    fid.write(str(acc))
    fid.close()


if __name__ == '__main__':
    main()