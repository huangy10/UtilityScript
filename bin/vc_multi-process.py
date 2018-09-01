#!/usr/bin/python
from __future__ import print_function
import os
import json
import argparse
import subprocess
import datetime
from concurrent.futures import ThreadPoolExecutor

pool = ThreadPoolExecutor(2)


class ParallelVideoConverter(object):
    
    def __init__(self, target_dir, remove_origin=True):
        self.target_dir = target_dir
        self.remove_origin = remove_origin
        self.use_cuda = True
        self.high_quality = False
    
    @staticmethod
    def need_convert(filename):
        video_info = subprocess.check_output(
            'ffprobe -show_format -loglevel quiet -show_streams -print_format json -i "%s"' % filename, shell=True)
        video_info = json.loads(video_info)
        streams = video_info["streams"]
        video_type_ok = False
        audio_type_ok = False
        for stream in streams:
            if stream["codec_type"] == "video" and stream["codec_name"] == "h264":
                video_type_ok = True
            if stream["codec_type"] == "audio" and stream["codec_name"] == "aac":
                audio_type_ok = True
        return not (video_type_ok and audio_type_ok)
    
    @staticmethod
    def get_no_duplicated_file_name(filename):
        idx = 0
        while True:
            if idx == 0:
                output_file_name = filename + ".mp4"
            else:
                output_file_name = "%s-%s.mp4" % (filename, idx)
            if os.path.exists(output_file_name):
                idx += 1
                continue
            else:
                break
        return output_file_name
    
    def get_ffmpeg_command(self, input_file, output_file):
        if self.use_cuda:
            if self.high_quality:
                high_quality_config = "-preset slow -rc vbr_hq -b:v 8M -maxrate:v 10M"
            else:
                high_quality_config = ""
            res = 'ffmpeg -y -hwaccel cuvid -i "{input_file}" -c:v h264_nvenc -gpu {gpu_idx} -pix_fmt yuv420p {high_quality_config} "{output_file}"'.format(
                input_file=input_file, output_file=output_file, gpu_idx=self.gpu, high_quality_config=high_quality_config)
            print("Running command: " + res)
            return res
        else:
            return 'ffmpeg -i "{input_file}" -vcodec h264 -strict -2 "{output_file}"'.format(
                input_file=input_file, output_file=output_file)
    
    def convert_video(self, file_path):
        elements = file_path.split(".")
        ext = elements[-1]
        if ext not in ["m4a", "mkv", "ts", "mp4", "avi", "iso"]:
            print("Unsupported format, skipping %s" % file_path)
            return
        filename = ".".join(elements[0: -1])
