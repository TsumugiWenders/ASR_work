# Author: Sining Sun, Zhanheng Yang, Binbin Zhang

# Author: Sining Sun, Zhanheng Yang, Binbin Zhang

import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import kaldi_io
from utils import *

targets_list = ['Z', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'O']
targets_mapping = {}
for i, x in enumerate(targets_list):
    targets_mapping[x] = i

def plot_spectrogram(spec, file_name):
    fig = plt.figure(figsize=(20, 10))
    plt.plot(spec)
    plt.xlabel('epochs')
    plt.ylabel('loss')
    plt.savefig(file_name)
    plt.show()

class Layer(object):
    def forward(self, input):
        ''' Forward function by input
        Args:
            input: input, B * N matrix, B for batch size
        Returns:
            output when applied this layer
        '''
        raise 'Not implement error'

    def backward(self, input, output, d_output):
        ''' Compute gradient of this layer's input by (input, output, d_output)
            as well as compute the gradient of the parameter of this layer
        Args:
            input: input of this layer
            output: output of this layer
            d_output: accumulated gradient from final output to this
                      layer's output
        Returns:
            accumulated gradient from final output to this layer's input
        '''
        raise 'Not implement error'

    def set_learning_rate(self, lr):
        ''' Set learning rate of this layer'''
        self.learning_rate = lr

    def update(self):
        ''' Update this layers parameter if it has or do nothing
        '''


class ReLU(Layer):
    def forward(self, input):
        # BEGIN_LAB
        tem_mat = np.maximum(0, input)
        assert (tem_mat.shape == input.shape)
        #         print('1',tem_mat.T.shape)
        return tem_mat.T

        # END_LAB

    def backward(self, input, output, d_output):
        # BEGIN_LAB
        d_mat = np.array(d_output, copy=True)
        #         if input.any() <=0:
        #             d_mat= 0
        d_mat[input <= 0] = 0
        assert (d_mat.shape == input.shape)
        #         print('2',d_mat.T.shape)
        return d_mat.T

        # END_LAB


class FullyConnect(Layer):
    def __init__(self, in_dim, out_dim):
        self.w = np.random.randn(out_dim, in_dim) * np.sqrt(2.0 / in_dim)
        self.b = np.zeros((out_dim, 1))
        self.dw = np.zeros((out_dim, in_dim))
        self.db = np.zeros((out_dim, 1))

    def forward(self, input):
        # BEGIN_LAB
        out_mat = np.dot(self.w, input.T) + self.b
        assert out_mat.shape == (self.w.shape[0], input.shape[0])
        #         print('3',out_mat.shape)
        return out_mat
        # END_LAB

    def backward(self, input, output, d_output):
        batch_size = input.shape[0]
        in_diff = None
        # BEGIN_LAB, compute in_diff/dw/db here
        self.dw = np.dot(d_output, input) / batch_size
        self.db = np.sum(d_output, axis=1, keepdims=True) / batch_size
        outt_mat = np.dot(self.w.T, d_output)

        assert (outt_mat.shape == input.T.shape)
        assert (self.dw.shape == self.w.shape)
        assert (self.db.shape == self.b.shape)
        #         print('4',outt_mat.T.shape)
        in_diff = outt_mat.T
        # END_LAB
        # Normalize dw/db by batch size
        self.dw = self.dw / batch_size
        self.db = self.db / batch_size
        return in_diff

    def update(self):
        self.w = self.w - self.learning_rate * self.dw
        self.b = self.b - self.learning_rate * self.db


class Softmax(Layer):
    def forward(self, input):
        _input = input.T
        row_max = _input.max(axis=1).reshape(_input.shape[0], 1)
        x = _input - row_max
        return np.exp(x) / np.sum(np.exp(x), axis=1).reshape(x.shape[0], 1)

    def backward(self, input, output, d_output):
        ''' Directly return the d_output as we show below, the grad is to
            the activation(input) of softmax
        '''
        return d_output


class DNN(object):
    def __init__(self, in_dim, out_dim, hidden_dim, num_hidden):
        self.layers = []
        self.layers.append(FullyConnect(in_dim, hidden_dim))
        self.layers.append(ReLU())
        for i in range(num_hidden):
            self.layers.append(FullyConnect(hidden_dim, hidden_dim))
            self.layers.append(ReLU())
        self.layers.append(FullyConnect(hidden_dim, out_dim))
        self.layers.append(Softmax())

    def set_learning_rate(self, lr):
        for layer in self.layers:
            layer.set_learning_rate(lr)

    def forward(self, input):
        self.forward_buf = []
        out = input
        self.forward_buf.append(out)
        for i in range(len(self.layers)):
            out = self.layers[i].forward(out)
            self.forward_buf.append(out)
        assert (len(self.forward_buf) == len(self.layers) + 1)
        return out

    def backward(self, grad):
        '''
        Args:
            grad: the grad is to the activation before softmax
        '''
        self.backward_buf = [None] * len(self.layers)
        self.backward_buf[len(self.layers) - 1] = grad
        for i in range(len(self.layers) - 2, -1, -1):
            grad = self.layers[i].backward(self.forward_buf[i],
                                           self.forward_buf[i + 1],
                                           self.backward_buf[i + 1].T)
            self.backward_buf[i] = grad

    def update(self):
        for layer in self.layers:
            layer.update()


def one_hot(labels, total_label):
    output = np.zeros((labels.shape[0], total_label))
    for i in range(labels.shape[0]):
        output[i][labels[i]] = 1.0
    return output


def train(dnn):
    utt2feat, utt2target = read_feats_and_targets('train/feats.scp',
                                                  'train/text')
    inputs, labels = build_input(targets_mapping, utt2feat, utt2target)
    num_samples = inputs.shape[0]
    print('input', num_samples)
    # Shuffle data
    permute = np.random.permutation(num_samples)
    inputs = inputs[permute]
    labels = labels[permute]
    num_epochs = 200
    batch_size = 100
    avg_loss = np.zeros(num_epochs)
    for i in range(num_epochs):
        cur = 0
        while cur < num_samples:
            end = min(cur + batch_size, num_samples)
            input = inputs[cur:end]
            label = labels[cur:end]
            #             print('input',input.shape)
            #             print('label',label.shape)
            # Step1: forward
            out = dnn.forward(input)
            #             print('out',out.shape)
            one_hot_label = one_hot(label, out.shape[1])
            # Step2: Compute cross entropy loss and backward
            #             print(one_hot_label.shape)
            #
            loss = -np.sum(np.log(out + 1e-20) * one_hot_label) / out.shape[0]
            # The grad is to activation before softmax
            grad = out - one_hot_label
            dnn.backward(grad)
            # Step3: update parameters
            dnn.update()
            print('Epoch {} num_samples {} loss {}'.format(i, cur, loss))
            avg_loss[i] += loss
            cur += batch_size
            avg_loss[i] /= math.ceil(num_samples / batch_size)
    plot_spectrogram(avg_loss, 'loss.png')


def test(dnn):
    utt2feat, utt2target = read_feats_and_targets('test/feats.scp',
                                                  'test/text')
    total = len(utt2feat)
    correct = 0
    for utt in utt2feat:
        t = utt2target[utt]
        ark = utt2feat[utt]
        mat = kaldi_io.read_mat(ark)
        mat = splice(mat, 5, 5)
        posterior = dnn.forward(mat)
        posterior = np.sum(posterior, axis=0) / float(mat.shape[0])
        predict = targets_list[np.argmax(posterior)]
        if t == predict: correct += 1
        print('label: {} predict: {}'.format(t, predict))
    print('Acc: {}'.format(float(correct) / total))


def main():
    np.random.seed(777)
    # We splice the raw feat with left 5 frames and right 5 frames
    # So the input here is 39 * (5 + 1 + 5) = 429
    dnn = DNN(429, 11, 128, 1)
    dnn.set_learning_rate(1e-2)
    train(dnn)
    test(dnn)


if __name__ == '__main__':
    main()
