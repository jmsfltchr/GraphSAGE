
import tensorflow as tf

"""
Outline for how to use Grakn with TensorFlow/ML
"""


# class GraknEmbedder(tf.estimator.Estimator):
#     pass
#
#
# class SupervisedGraknEmbedder(GraknEmbedder):
#     pass


class UnSupervisedGraknEmbedder(tf.estimator.Estimator):
    # def train(self, grakn_concepts, excluded_concept_types=None):
    #     pass
    #
    # def get_embeddings(self, grakn_concepts):
    #     pass

    def __init__(self, model_dir=None, config=None, params=None, warm_start_from=None):
        def _model_fn(features, labels, mode, config):
            """Call the defined shared _dnn_model_fn."""
            return _unsupervised_grakn_embedder_model_fn(
                features=features,
                labels=labels,
                mode=mode,
                # head=head,
                # hidden_units=hidden_units,
                # feature_columns=tuple(feature_columns or []),
                # optimizer=optimizer,
                # activation_fn=activation_fn,
                # dropout=dropout,
                # input_layer_partitioner=input_layer_partitioner,
                # config=config
            )

        super(UnSupervisedGraknEmbedder, self).__init__(model_fn=_model_fn, model_dir=model_dir, config=config)


def _unsupervised_grakn_embedder_model_fn(
        features,  # This is batch_features from input_fn
        labels,  # This is batch_labels from input_fn
        mode,  # An instance of tf.estimator.ModeKeys
        params):  # Additional configuration

    if mode == tf.estimator.ModeKeys.TRAIN:
        pass
    if mode == tf.estimator.ModeKeys.EVAL:
        pass
    if mode == tf.estimator.ModeKeys.PREDICT:
        pass


class GraknConceptPicker:
    def pick_concepts(self, match_query, n_concepts=None, proportion_of_concepts=None):
        """
        Randomly picks one of the matching concepts from Grakn
        :return:
        """
        return []


########################################################################################################################
# USAGE
########################################################################################################################

"""
It's very likely that the user will want to pick a set of positive examples, for which they have labels, and a set of 
test data.
"""

training_query = (
    "match $x isa person; $c isa company, has name 'Netflix'; (customer: $x, vendor: $c) isa subscription; offset {{ "
    "offset }}; limit 1; get $x;")

testing_query = (
    "match $x isa person; $c isa company, has name 'Netflix'; (customer: $x, vendor: $c) isa subscription, "
    "has is-premium true; offset {{ offset }}; limit 1; get $x;")

concept_picker = GraknConceptPicker()

training_concepts = concept_picker.pick_concepts(training_query, proportion_of_concepts=0.4)
testing_concepts = concept_picker.pick_concepts(testing_query, proportion_of_concepts=0.2)

x = tf.placeholder(tf.resource)
# tf.variant
val = tf.placeholder(tf.float32)
y_true = tf.placeholder(tf.float32)

linear_model = tf.layers.Dense(units=1)

y_pred = linear_model(x)
loss = tf.losses.mean_squared_error(labels=y_true, predictions=y_pred)

optimizer = tf.train.GradientDescentOptimizer(0.01)
train = optimizer.minimize(loss)

init = tf.global_variables_initializer()

sess = tf.Session()
sess.run(init)
for i in range(100):
  _, loss_value = sess.run((train, loss))
  print(loss_value)

print(sess.run(y_pred))