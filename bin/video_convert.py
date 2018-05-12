import os
import json
import argparse
import subprocess
import datetime


parser = argparse.ArgumentParser(description="Auto Convert Videos")
parser.add_argument("input", type=str, help="input file or dir")
parser.add_argument("-r", "--recursively", action="store_true", help="Convert Recursively")


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


def convert_video(file_path, remove_origin=True):
    elements = file_path.split(".")
    ext = elements[-1]
    filename = ".".join(elements[0: -1])
    if ext not in ["m4a", "mkv", "ts", "mp4"]:
        print("Unsupported format, skipping %s" % file_path)
        return
    if not need_convert(file_path):
        print("Skipping will-formated file %s" % file_path)
        return
    print("Converting video file %s" % file_path)
    start_at = datetime.datetime.now()
    res = subprocess.call('ffmpeg -i "{input_file}" -vcodec h264 -strict -2 "{output_file}" > /dev/null'.format(
        input_file=file_path,
        output_file=filename + ".mp4"), shell=True)
    run_time = datetime.datetime.now() - start_at
    print("Time takes: %s" % run_time)
    if res == 0:
        print("Success!")
        if remove_origin:
            print("Removing Origin Files")
    if res == 0 and remove_origin:
        os.remove(file_path)
        

def convert_video_dir(video_dir, recursively=False):
    tasks = [video_dir]
    while len(tasks) != 0:
        working_dir = tasks.pop(0)
        print("Entering %s" % working_dir)
        for f in os.listdir(working_dir):
            f = os.path.join(working_dir, f)
            if os.path.isfile(f):
                convert_video(f)
            elif recursively:
                tasks.append(f)


if __name__ == "__main__":
    args = parser.parse_args()
    input_filename = args.input
    recursively = args.recursively
    start_at = datetime.datetime.now()
    print("start at %s" % start_at)
    if os.path.isfile(input_filename):
        convert_video(input_filename)
    else:
        convert_video_dir(input_filename, recursively)

    end_at = datetime.datetime.now()
    print("end at %s" % end_at)
    print("total time: %s" % end_at - start_at)
    
    