from __future__ import print_function
import torch
import numpy as np
import scipy.sparse
import numba

def plsa(count, n_topics, n_iter, learning_rate=1e-2):
    n_docs = count.shape[0]
    n_terms = count.shape[1]
    nnz = count._nnz()

    count = count.to_dense()
    count = torch.autograd.Variable(count)

    L = np.random.rand(n_docs, n_topics)
    L /= L.sum(axis=1, keepdims=True)
    L = torch.FloatTensor(L)
    L = torch.autograd.Variable(L, requires_grad=True)

    R = np.random.rand(n_topics, n_terms)
    R /= R.sum(axis=1, keepdims=True)
    R = torch.FloatTensor(R)
    R = torch.autograd.Variable(R, requires_grad=True)

    for t in range(n_iter):
        # Forward pass: compute predicted y using operations on Variables; these
        # are exactly the same operations we used to compute the forward pass using
        # Tensors, but we do not need to keep references to intermediate values since
        # we are not implementing the backward pass by hand.
        count_pred = L.mm(R)

        # Compute and print loss using operations on Variables.
        # Now loss is a Variable of shape (1,) and loss.data is a Tensor of shape
        # (1,); loss.data[0] is a scalar value holding the loss.
        loss = (count_pred - count).pow(2).sum()
        if t % 100 == 0:
            print(t, loss.data[0] / n_docs / n_terms)

        # Use autograd to compute the backward pass. This call will compute the
        # gradient of loss with respect to all Variables with requires_grad=True.
        # After this call w1.grad and w2.grad will be Variables holding the gradient
        # of the loss with respect to w1 and w2 respectively.
        loss.backward()

        # Update weights using gradient descent; w1.data and w2.data are Tensors,
        # w1.grad and w2.grad are Variables and w1.grad.data and w2.grad.data are
        # Tensors.
        L.data -= learning_rate * L.grad.data
        R.data -= learning_rate * R.grad.data

        # Manually zero the gradients after updating weights
        L.grad.data.zero_()
        R.grad.data.zero_()

    return L, R


def init_matrix(n_docs, n_terms, sparsity):
    m = int(n_docs * n_terms * sparsity)

    ind = torch.LongTensor(2, m)
    ind[0] = torch.LongTensor(np.random.choice(n_docs, m))
    ind[1] = torch.LongTensor(np.random.choice(n_terms, m))
    v = torch.FloatTensor(np.ones(m, np.int64))

    count = torch.sparse.FloatTensor(ind, v, torch.Size([n_docs, n_terms]))
    count = count.coalesce()
    return count

def main():
    n_docs, n_terms, sparsity = 100, 1000, 0.01

    count = init_matrix(n_docs, n_terms, sparsity)

    plsa(count, 5, 1000)

if __name__ == "__main__":
    main()