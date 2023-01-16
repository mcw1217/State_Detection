from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input,Dense, concatenate, Flatten, Dropout
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.utils import plot_model


def build_cnn():
  cnn_base = ResNet50(include_top=False, weights='imagenet', input_shape=[63,63,3], classes=5)
  cnn_base.trainable =False

  inputA = Input(shape=(63,63,3), name="input_img")
  inputB = Input(shape=(1,), name="input_temper")

  base_layer = cnn_base(inputA)
  flatten = Flatten()(base_layer)

  x = concatenate([flatten, inputB])
  x = Dense(256,activation='relu')(x)
  x = Dropout(0.5)(x)
  outputs = Dense(10, activation='softmax')(x)

  model = Model(inputs=[inputA,inputB], outputs=outputs, name='State_output')
  model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=['accuracy'])
  return model

model = build_cnn()

  # plot_model(model, show_shapes=True, show_layer_names=True, to_file='model.png')
  
  

