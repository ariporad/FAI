from tensorflow.keras import layers
from tensorflow import keras


def make_dense_net():
    inputs = layers.Input(shape=(50, 50, 4))
    layer0 = layers.Flatten()(inputs)
    layer1 = layers.Dense(64, activation='relu')(layer0)
    layer2 = layers.Dense(64, activation='relu')(layer1)
    layer3 = layers.Dense(512, activation='relu')(layer2)
    out = layers.Dense(2, activation='linear')(layer3)
    model = keras.Model(inputs=inputs, outputs=out)
    optimizer = keras.optimizers.Adam(learning_rate=0.00001)
    model.compile(loss='mse', optimizer=optimizer, metrics=['mae'])
    return model


def make_conv_net():
    inputs = layers.Input(shape=(50, 50, 4))
    layer1 = layers.Conv2D(32, 8, strides=4, activation="selu")(inputs)
    layer2 = layers.Conv2D(64, 4, strides=2, activation="selu")(layer1)
    layer3 = layers.Conv2D(64, 3, strides=1, activation="selu")(layer2)
    layer4 = layers.Flatten()(layer3)
    layer5 = layers.Dense(512, activation="selu")(layer4)
    out = layers.Dense(2, activation="linear")(layer5)
    model = keras.Model(inputs=inputs, outputs=out)
    return model
