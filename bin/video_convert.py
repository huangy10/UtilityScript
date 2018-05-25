#!/usr/bin/python
from __future__ import print_function
import os
import json
import argparse
import subprocess
import datetime


def _set_cmd_args():
    parser = argparse.ArgumentParser(description="Auto Convert Videos")
    parser.add_argument("input", type=str, help="input file or dir")
    parser.add_argument("-r", "--recursively", action="store_true", help="Convert Recursively")
    parser.add_argument("-f", "--force", action="store_true", help="Force to convert video")
    parser.add_argument("--cuda", action="store_true", help="accelate with gpu")
    parser.add_argument("--gpu", default=0, help="gpu index to use")
    return parser

class VideoConverter(object):
    
    def __init__(self, opts, remove_origin=True):
        self.recursively = opts.recursively
        self.force = opts.force
        self.remove_origin = remove_origin
        self.use_cuda = opts.cuda
        self.gpu = opts.gpu
    
    def need_convert(self, filename):
        if self.force:
            return True
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

    def get_non_duplicate_filename(self, filename):
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
            res = 'ffmpeg -y -hwaccel cuvid -i "{input_file}" -c:v h264_nvenc -gpu {gpu_idx} -pix_fmt yuv420p "{output_file}" > vc.log'.format(
                input_file=input_file, output_file=output_file, gpu_idx=self.gpu)
            print("Running command: " + res)
            return res
        else:
            return 'ffmpeg -i "{input_file}" -vcodec h264 -strict -2 "{output_file}" > vc.log'.format(
                input_file=input_file, output_file=output_file)

    def convert_video(self, file_path):
        elements = file_path.split(".")
        ext = elements[-1]
        if ext not in ["m4a", "mkv", "ts", "mp4", "avi", "iso"]:
            print("Unsupported format, skipping %s" % file_path)
            return
        filename = ".".join(elements[0: -1])
        if ext == "mp4" and not self.need_convert(file_path):
            print("Skipping will-formated file %s" % file_path)
            return
        print("Converting video file %s" % file_path)
        start_at = datetime.datetime.now()
        res = subprocess.call(self.get_ffmpeg_command(file_path, self.get_non_duplicate_filename(filename)), shell=True)
        run_time = datetime.datetime.now() - start_at
        print("Time takes: %s" % run_time)
        if res == 0:
            print("Success!")
            if self.remove_origin:
                print("Removing Origin Files")
        if res == 0 and self.remove_origin:
            os.remove(file_path)
        
    def convert_video_dir(self, video_dir):
        tasks = [video_dir]
        while len(tasks) != 0:
            working_dir = tasks.pop(0)
            if not os.path.exists(working_dir):
                print("Ignoring non-exist directory %s" % working_dir)
                continue
            print("Entering %s" % working_dir)
            for f in os.listdir(working_dir):
                f = os.path.join(working_dir, f)
                if not os.path.exists(f):
                    print("Ignoring non-exist file %s" % f)
                    continue
                if os.path.isfile(f):
                    self.convert_video(f)
                elif self.recursively:
                    tasks.append(f)

    def convert(self, input_path):
        if os.path.isfile(input_path):
            self.convert_video(input_path)
        else:
            self.convert_video_dir(input_path)



def main():
    parser = _set_cmd_args()
    args = parser.parse_args()
    input_filename = args.input
    start_at = datetime.datetime.now()
    print("start at %s" % start_at)
    if args.cuda:
        print("using cuda")

    converter = VideoConverter(args)
    converter.convert(input_filename)

    end_at = datetime.datetime.now()
    print("end at %s" % end_at)
    print("total time: %s" % (end_at - start_at))


if __name__ == "__main__":
    main()
    
    