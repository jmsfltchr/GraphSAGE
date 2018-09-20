from __future__ import division
from __future__ import print_function

from graphsage.layers import Layer

import tensorflow as tf
flags = tf.app.flags
FLAGS = flags.FLAGS


"""
Classes that are used to sample node neighborhoods
"""

class UniformNeighborSampler(Layer):
    """
    Uniformly samples neighbors.
    Assumes that adj lists are padded with random re-sampling
    """
    def __init__(self, adj_info, **kwargs):
        super(UniformNeighborSampler, self).__init__(**kwargs)
        self.adj_info = adj_info

    def _call(self, inputs):
        # We provide a set of inputs as ids of nodes we want to sample, and how many samples we want of each
        ids, num_samples = inputs
        # Look up all of the neighbours for a given node id to create a matrix filtered as such
        adj_lists = tf.nn.embedding_lookup(self.adj_info, ids)
        # Randomly shuffle those neighbours all at once given that they're all in a matrix
        # tf.random_shuffle operates along the first dimension, so transposing before and after is seemingly necessary!
        adj_lists = tf.transpose(tf.random_shuffle(tf.transpose(adj_lists)))
        # Now that the neighbours are in a random order, we can just take a slice of size equal to the number of
        # samples we need
        # Note there's a more pythonic way to write this in the tf.slice code docs
        adj_lists = tf.slice(adj_lists, [0,0], [-1, num_samples])

        # Returns a tensor of random neighbour ids, of shape (len(ids), num_samples)
        return adj_lists
