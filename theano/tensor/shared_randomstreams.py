"""Define RandomStreams, providing random number variables for Theano graphs."""
__docformat__ = "restructuredtext en"

import sys
import numpy

from theano.gof import Container
from theano.compile.sharedvalue import SharedVariable, shared_constructor, shared
import raw_random

class RandomStateSharedVariable(SharedVariable):
    pass

@shared_constructor
def randomstate_constructor(value, name=None, strict=False):
    """SharedVariable Constructor for RandomState"""
    if not isinstance(value, numpy.random.RandomState):
        raise TypeError
    return RandomStateSharedVariable(
            type=raw_random.random_state_type,
            value=value, 
            name=name,
            strict=strict)

class RandomStreams(object):
    """Module component with similar interface to numpy.random (numpy.random.RandomState)"""

    random_state_variables = []
    """A list of pairs of the form (input_r, output_r).  This will be over-ridden by the module
    instance to contain stream generators.
    """

    default_instance_seed = None
    """Instance variable should take None or integer value.  Used to seed the random number
    generator that provides seeds for member streams"""

    gen_seedgen = None
    """numpy.RandomState instance that gen() uses to seed new streams.
    """

    def updates(self):
        return list(self.random_state_variables)

    def __init__(self, seed=None):
        """
        :type seed: None or int

        :param seed: a default seed to initialize the RandomState instances after build.  See
        `RandomStreamsInstance.__init__` for more details.
        """
        super(RandomStreams, self).__init__()
        self.random_state_variables = []
        self.default_instance_seed = seed
        self.gen_seedgen = numpy.random.RandomState(seed)

    def seed(self, seed=None):
        """Re-initialize each random stream
        
        :param seed: each random stream will be assigned a unique state that depends
        deterministically on this value.

        :type seed: None or integer in range 0 to 2**30

        :rtype: None
        """
        if seed is None:
            seed = self.default_instance_seed

        seedgen = numpy.random.RandomState(seed)
        for old_r, new_r in self.random_state_variables:
            old_r_seed = seedgen.randint(2**30)
            old_r.value = numpy.random.RandomState(int(old_r_seed))

    def __getitem__(self, item):
        """Retrieve the numpy RandomState instance associated with a particular stream

        :param item: a variable of type RandomStateType, associated with this RandomStream

        :rtype: numpy RandomState (or None, before initialize)

        :note: This is kept for compatibility with `tensor.randomstreams.RandomStreams`.  The
        simpler syntax ``item.rng.value`` is also valid.

        """
        return item.value

    def __setitem__(self, item, val):
        """Set the numpy RandomState instance associated with a particular stream

        :param item: a variable of type RandomStateType, associated with this RandomStream

        :param val: the new value
        :type val: numpy RandomState

        :rtype:  None

        :note: This is kept for compatibility with `tensor.randomstreams.RandomStreams`.  The
        simpler syntax ``item.rng.value = val`` is also valid.

        """
        item.value = val


    def gen(self, op, *args, **kwargs):
        """Create a new random stream in this container.

        :param op: a RandomFunction instance to 

        :param args: interpreted by `op`

        :param kwargs: interpreted by `op`

        :returns: The symbolic random draw part of op()'s return value.  This function stores
        the updated RandomStateType Variable for use at `build` time.

        :rtype: TensorVariable
        """
        seed = int(self.gen_seedgen.randint(2**30))
        random_state_variable = shared(numpy.random.RandomState(seed))
        new_r, out = op(random_state_variable, *args, **kwargs)
        out.rng = random_state_variable
        self.random_state_variables.append((random_state_variable, new_r))
        return out

    def binomial(self, *args, **kwargs):
        """Return a symbolic binomial sample

        This is a shortcut for a call to `self.gen`
        """
        return self.gen(raw_random.binomial, *args, **kwargs)

    def uniform(self, *args, **kwargs):
        """Return a symbolic uniform sample

        This is a shortcut for a call to `self.gen`
        """
        return self.gen(raw_random.uniform, *args, **kwargs)

    def normal(self, *args, **kwargs):
        """Return a symbolic normal sample

        This is a shortcut for a call to `self.gen`
        """
        return self.gen(raw_random.normal, *args, **kwargs)

    def random_integers(self, *args, **kwargs):
        """Return a symbolic random integer sample

        This is a shortcut for a call to `self.gen`
        """
        return self.gen(raw_random.random_integers, *args, **kwargs)
