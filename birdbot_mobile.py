from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import subprocess
import sys
import picamera
import time
import tensorflow as tf
import threading
import numpy as np
import motor_control
from PIL import Image

model_file = "trained_128_mobile_butt_graph.pb"
label_file = "mobile_butt_labels.txt"
input_height = 128
input_width = 128
input_mean = 128
input_std = 128
input_layer = "input"
output_layer = "final_result"

def get_time():
  now = time.strftime("%Y-%m-%d %H:%M.%S")
  return now

def load_labels(filename):
  """Read in labels, one label per line."""
  return [line.rstrip() for line in tf.gfile.GFile(filename)]

def read_tensor_from_image_file(file_name, input_height=128, input_width=128,
				input_mean=0, input_std=255):
  print('Reading image tensor \t\t %s' %(get_time()))
  input_name = "file_reader"
  output_name = "normalized"
  file_reader = tf.read_file(file_name, input_name)
  image_reader = tf.image.decode_jpeg(file_reader, channels = 3, name='jpeg_reader')
  float_caster = tf.cast(image_reader, tf.float32)
  dims_expander = tf.expand_dims(float_caster, 0);
  resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
  normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
  sess = tf.Session()
  result = sess.run(normalized)
  print('Finished reading \t\t %s' %(get_time()))

  return result

def create_and_persist_graph(filename):
    print('Loading the graph \t\t %s' %(get_time()))
    with tf.Session() as persisted_sess:
        # Load Graph
        with tf.gfile.FastGFile(filename,'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            persisted_sess.graph.as_default()
            tf.import_graph_def(graph_def, name='')
            print('Graph loaded \t\t\t %s' %(get_time()))
        return persisted_sess.graph


def something(file_name, graph):  
  t = read_tensor_from_image_file(file_name,
                                  input_height=input_height,
                                  input_width=input_width,
                                  input_mean=input_mean,
                                  input_std=input_std)
  print('Doing something \t\t %s' %(get_time()))
  input_name = input_layer
  output_name = output_layer
  input_operation = graph.get_operation_by_name(input_name);
  output_operation = graph.get_operation_by_name(output_name);

  with tf.Session(graph=graph) as sess:
    results = sess.run(output_operation.outputs[0],
                      {input_operation.outputs[0]: t})
  results = np.squeeze(results)

  top_k = results.argsort()[-5:][::-1]
  labels = load_labels(label_file)
  butt_prob = results[0] *100
  print('Finished doing something \t %s' %(get_time()))

  return butt_prob
    

def image_capture_analysis(graph):
  print('Starting camera \t\t %s' %(get_time()))
  camera = picamera.PiCamera()
  camera.resolution = (128, 128)
  camera.start_preview()
  time.sleep(2)
  fail_count = 0
  for filename in camera.capture_continuous('image.jpg'):
    img_time = time.strftime("%Y-%m-%d %H:%M.%S")
    print('Taking image \t\t\t %s' %(get_time()))
    butt_prob = something(filename, graph)
    if butt_prob >= 70:
      print('BUTT!!!!!  %.2f%% \t\t %s' % (butt_prob, img_time))
      motor_control.main(180, 1, 2),
      motor_control.main(180, -1, 0)
      fail_count = 0
      Image.open('image.jpg').save('posbutt_images/%s.jpg' %(img_time))
      time.sleep(1)
    else:
      print('No butt %.2f%% \t\t\t %s'  % (butt_prob, img_time))
      Image.open('image.jpg').save('negbutt_images/%s.jpg' %(img_time))
      fail_count += 1
      if fail_count == 5:
        print('Clearing pedestal \t\t %s'  % (img_time))
        motor_control.main(360, -1, 0)
        fail_count = 0
        time.sleep(1)
  


def main():
  print('Starting program')
  graph = create_and_persist_graph(model_file)
  image_capture_analysis(graph)
    
    

main()



