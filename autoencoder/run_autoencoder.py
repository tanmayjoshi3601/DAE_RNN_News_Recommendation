import tensorflow as tf

import autoencoder
import datasets

# #################### #
#   Flags definition   #
# #################### #
flags = tf.app.flags
FLAGS = flags.FLAGS

# Global configuration
flags.DEFINE_string('model_name', '', 'Model name.')
flags.DEFINE_string('dataset', 'mnist', 'Which dataset to use. ["mnist", "cifar10"]')
flags.DEFINE_string('cifar_dir', '', 'Path to the cifar 10 dataset directory.')
flags.DEFINE_integer('seed', -1, 'Seed for the random generators (>= 0). Useful for testing hyperparameters.')
flags.DEFINE_boolean('restore_previous_model', False, 'If true, restore previous model corresponding to model name.')
flags.DEFINE_boolean('encode_train', False, 'Whether to encode and store the training set.')
flags.DEFINE_boolean('encode_valid', False, 'Whether to encode and store the validation set.')
flags.DEFINE_boolean('encode_test', False, 'Whether to encode and store the test set.')


# Stacked Denoising Autoencoder specific parameters
flags.DEFINE_integer('n_components', 256, 'Number of hidden units in the dae.')
flags.DEFINE_string('corr_type', 'none', 'Type of input corruption. ["none", "masking", "salt_and_pepper"]')
flags.DEFINE_float('corr_frac', 0., 'Fraction of the input to corrupt.')
flags.DEFINE_integer('xavier_init', 1, 'Value for the constant in xavier weights initialization.')
flags.DEFINE_string('enc_act_func', 'tanh', 'Activation function for the encoder. ["sigmoid", "tanh"]')
flags.DEFINE_string('dec_act_func', 'none', 'Activation function for the decoder. ["sigmoid", "tanh", "none"]')
flags.DEFINE_string('main_dir', 'dae/', 'Directory to store data relative to the algorithm.')
flags.DEFINE_string('loss_func', 'mean_squared', 'Loss function. ["mean_squared" or "cross_entropy"]')
flags.DEFINE_integer('verbose', 0, 'Level of verbosity. 0 - silent, 1 - print accuracy.')
flags.DEFINE_integer('weight_images', 0, 'Number of weight images to generate.')
flags.DEFINE_string('opt', 'gradient_descent', '["gradient_descent", "ada_grad", "momentum"]')
flags.DEFINE_float('learning_rate', 0.01, 'Initial learning rate.')
flags.DEFINE_float('momentum', 0.5, 'Momentum parameter.')
flags.DEFINE_integer('num_epochs', 10, 'Number of epochs.')
flags.DEFINE_integer('batch_size', 10, 'Size of each mini-batch.')

assert FLAGS.dataset in ['mnist', 'cifar10']
assert FLAGS.enc_act_func in ['sigmoid', 'tanh']
assert FLAGS.dec_act_func in ['sigmoid', 'tanh', 'none']
assert FLAGS.corr_type in ['masking', 'salt_and_pepper', 'decay', 'none']
assert 0. <= FLAGS.corr_frac <= 1.
assert FLAGS.loss_func in ['cross_entropy', 'mean_squared']
assert FLAGS.opt in ['gradient_descent', 'ada_grad', 'momentum']

if __name__ == '__main__':

    if FLAGS.dataset == 'mnist':

        # ################# #
        #   MNIST Dataset   #
        # ################# #

        trX, vlX, teX = datasets.load_mnist_dataset(mode='unsupervised')

    elif FLAGS.dataset == 'cifar10':

        # ################### #
        #   Cifar10 Dataset   #
        # ################### #

        trX, teX = datasets.load_cifar10_dataset(FLAGS.cifar_dir, mode='unsupervised')
        vlX = teX[:5000]  # Validation set is the first half of the test set

    else:  # cannot be reached, just for completeness
        trX = None
        vlX = None
        teX = None

    # Create the object
    dae = autoencoder.DenoisingAutoencoder(
        seed=FLAGS.seed, model_name=FLAGS.model_name, n_components=FLAGS.n_components,
        enc_act_func=FLAGS.enc_act_func, dec_act_func=FLAGS.dec_act_func, xavier_init=FLAGS.xavier_init,
        corr_type=FLAGS.corr_type, corr_frac=FLAGS.corr_frac, dataset=FLAGS.dataset,
        loss_func=FLAGS.loss_func, main_dir=FLAGS.main_dir, opt=FLAGS.opt,
        learning_rate=FLAGS.learning_rate, momentum=FLAGS.momentum,
        verbose=FLAGS.verbose, num_epochs=FLAGS.num_epochs, batch_size=FLAGS.batch_size)

    # Fit the model
    dae.fit(trX, teX, restore_previous_model=FLAGS.restore_previous_model)

    # Encode the training data and store it
    dae.transform(trX, name='train', save=FLAGS.encode_train)
    dae.transform(vlX, name='validation', save=FLAGS.encode_valid)
    dae.transform(teX, name='test', save=FLAGS.encode_test)

    # save images
    dae.get_weights_as_images(28, 28, max_images=FLAGS.weight_images)

