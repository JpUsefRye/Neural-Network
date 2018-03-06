# -*- coding: utf-8 -*-
try:
    from .matrix import Matrix, Vector
except ImportError as e:
    from matrix import Matrix, Vector

import math
import pickle

def Sigmoid(x):
    return 1 / (1 + math.exp(-x))

def dSigmoid(y):
    return y * (1 - y)

def Tanh(x):
    return math.tanh(x)

def dTanh(y):
    return 1 - (y * y)

class ActivationFunction(object):
    def __init__(self, func, dfunc):
        self.func = func
        self.dfunc = dfunc

tanh = ActivationFunction(
    Tanh,
    dTanh
)


sigmoid = ActivationFunction(
    Sigmoid,
    dSigmoid
)

class NeuralNetwork:
    def __init__(self, input_nodes, hidden_nodes, output_nodes, learning_rate=0.1, activation_function=sigmoid):
        self.input_nodes = input_nodes
        self.hidden_nodes = hidden_nodes
        self.output_nodes = output_nodes
        self.learning_rate = learning_rate
        self.activation_function = activation_function

        self.weights_ih = Matrix(self.hidden_nodes, self.input_nodes)
        self.weights_ho = Matrix(self.output_nodes, self.hidden_nodes)
        self.weights_ih.randomize()
        self.weights_ho.randomize()

        self.bias_h = Vector(self.hidden_nodes)
        self.bias_o = Vector(self.output_nodes)
        self.bias_h.randomize()
        self.bias_o.randomize()

        self.setLearningRate(self.learning_rate)
        self.setActivationFunction(self.activation_function)

    def predict(self, inputs_array):
        # Generate hidden outputs
        inputs = Matrix.fromArray(inputs_array)
        hidden = Matrix.multiplyMatrix(self.weights_ih, inputs)
        hidden.add(self.bias_h)
        # Activation function
        hidden.map(self.activation_function.func)
        # Generating the output's output!
        output = Matrix.multiplyMatrix(self.weights_ho, hidden)
        output.add(self.bias_o)
        output.map(self.activation_function.func)
        # Sending it back to the caller!
        return output.toArray()

    def setLearningRate(self, learning_rate):
        minimum = 0.000001
        maximum = 1.0
        if isinstance(learning_rate, float) and learning_rate >= minimum and learning_rate <= maximum:
            self.learning_rate = learning_rate
        else:
            raise ValueError("Learning rate must be float in range 1.0")

    def setActivationFunction(self, func):
        self.activation_function = func

    def train(self, input_array, target_array):
        # Generate hidden outputs
        inputs = Matrix.fromArray(input_array)
        hidden = Matrix.multiplyMatrix(self.weights_ih, inputs)
        hidden.add(self.bias_h)
        # Activation function
        hidden.map(self.activation_function.func)
        # Generating the output's output!
        outputs = Matrix.multiplyMatrix(self.weights_ho, hidden)
        outputs.add(self.bias_o)
        outputs.map(self.activation_function.func)
        # Convert array to matrix object
        targets = Matrix.fromArray(target_array)

        # Calculate the error
        # ERROR = TARGETS - OUTPUTS
        output_errors = Matrix.subtract(targets, outputs)

        # Calculate gradient
        gradients = Matrix.Smap(outputs, self.activation_function.dfunc)
        gradients.multiply(output_errors)
        gradients.multiply(self.learning_rate)

        # Calculate deltas
        hidden_T = Matrix.transpose(hidden)
        weights_ho_deltas = Matrix.multiplyMatrix(gradients, hidden_T)

        # Adjust the weights by deltas
        self.weights_ho.add(weights_ho_deltas)
        # Adjust the bias by its deltas (gradients)
        self.bias_o.add(gradients)

        # Calculate the hidden layer errors
        who_t = Matrix.transpose(self.weights_ho)
        hidden_errors = Matrix.multiplyMatrix(who_t, outputs)

        # Calculate hidden gradient
        hidden_gradient = Matrix.Smap(hidden, self.activation_function.dfunc)
        hidden_gradient.multiply(hidden_errors)
        hidden_gradient.multiply(self.learning_rate)

        # Calculate input->hidden deltas
        inputs_T = Matrix.transpose(inputs)
        weight_ih_deltas = Matrix.multiplyMatrix(hidden_gradient, inputs_T)
        self.weights_ih.add(weight_ih_deltas)
        # Adjust bias by its deltas
        self.bias_h.add(hidden_gradient)

    def serialize(self, fname):
        pickle.dump(self, open(fname+'.weights', 'wb'))

    @staticmethod
    def deserialize(data):
        data = pickle.load(open(data+'.weights', 'rb'))
        nn = NeuralNetwork(data.input_nodes,
                           data.hidden_nodes,
                           data.output_nodes,
                           learning_rate=data.learning_rate,
                           activation_function=data.activation_function)
        
        nn.weights_ih    = data.weights_ih
        nn.weights_ho    = data.weights_ho
        nn.bias_h        = data.bias_h
        nn.bias_o        = data.bias_o
        
        return nn
