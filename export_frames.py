# Lint as: python3
# MIT License
#
# Copyright (c) 2021 RafaelMiquelino
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

r"""Export frames from video files using opencv library.
For extracting run:
python export_frames.py -- \
  --input_path=/tmp/videos \
  --output_path=/tmp/frames \
"""

import os
import sys

import cv2
from absl import flags, app

flags.DEFINE_string('input_path', None, 'Path to video source files.')
flags.DEFINE_string('output_path', None, 'Path to extracted frames.')
flags.DEFINE_integer('fps', 30, 'Frame per seconds to extract from the video')
flags.DEFINE_integer('image_max_dimension', 1024, 'Value of the maximum image dimension')
flags.DEFINE_integer('image_jpeg_quality', 80, 'Quality of the extracted image (0-100)')

FLAGS = flags.FLAGS


def get_frame(video_capture, time, frame_output_path, max_size, jpeg_quality):
    video_capture.set(cv2.CAP_PROP_POS_MSEC, time * 1000)
    has_frames, image = video_capture.read()
    if has_frames:
        img_w = image.shape[0]
        img_h = image.shape[1]
        if max(img_w, img_h) > max_size:
            if img_w < img_h:
                img_w = max_size * img_w // img_h
                img_h = max_size
            else:
                img_h = max_size * img_h // img_w
                img_w = max_size
        dist_size = (img_h, img_w)
        image = cv2.resize(image, dist_size, interpolation=cv2.INTER_AREA)
        cv2.imwrite(frame_output_path, image, params=[cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])  # save frame as JPG file
    return has_frames


def export_frames(video_path, frame_output_path, interval=1/30, max_dimension=1024, jpeg_quality=80):
    vidcap = cv2.VideoCapture(video_path)
    time = 0
    count = 1
    file_name = "".join((frame_output_path, str(count), ".jpg"))
    success = get_frame(vidcap, time, file_name, max_dimension, jpeg_quality)
    while success:
        count += 1
        time = time + interval
        time = round(time, 2)
        file_name = "".join((frame_output_path, str(count), ".jpg"))
        success = get_frame(vidcap, time, file_name, max_dimension, jpeg_quality)


def main(unused_argv):
    flags.mark_flag_as_required('input_path')
    flags.mark_flag_as_required('output_path')

    input_path = FLAGS.input_path
    output_path = FLAGS.output_path

    if os.path.isdir(input_path):
        file_list = os.listdir(input_path)
        file_list = [os.path.join(input_path, file) for file in file_list if file not in ['.DS_Store']]
    else:
        file_list = [input_path]

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for file in file_list:
        print("Extracting frames from", file)
        frame_prefix = os.path.join(
            output_path,
            "".join((
                os.path.splitext(os.path.basename(file))[0],
                "_img_"))
        )
        try:
            export_frames(file,
                          frame_prefix,
                          interval=1 / FLAGS.fps,
                          max_dimension=FLAGS.image_max_dimension,
                          jpeg_quality=FLAGS.image_jpeg_quality
                          )
        except Exception as err:
            print(err)
            sys.exit(1)
    print("Done")


if __name__ == '__main__':
    app.run(main)
