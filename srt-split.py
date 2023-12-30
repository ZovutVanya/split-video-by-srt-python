import os
import re
import sys
import subprocess
from datetime import datetime


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Script to split video files into chunks based on .srt timecodes\n")
        print(
            "usage: srt-split.py [video file] [subtitle file] (optional)[output format]"
        )
        print(
            "If no output format is supplied, "
            + "cut files will be saved in the same format as the original file."
        )
        sys.exit(0)

    file_to_cut = sys.argv[1]
    subtitle_file = sys.argv[2] if len(sys.argv) > 2 else None
    output_format = (
        sys.argv[3] if len(sys.argv) > 3 else ".".join(file_to_cut.split(".")[1:])
    )

    file_name = os.path.splitext(os.path.basename(file_to_cut))[0]

    if not os.path.isfile(file_to_cut):
        print(f"ERR: no file found at {file_to_cut}")
        print(
            "usage: srt-split.py [video file] [subtitle file] (optional)[output format]"
        )
        sys.exit(1)

    if subtitle_file and not os.path.isfile(subtitle_file):
        print(f"ERR: no file found at {subtitle_file}")
        print(
            "usage: srt-split.py [video file] [subtitle file] (optional)[output format]"
        )
        sys.exit(1)

    start_times_for_ffmpeg = []
    time_diff = []
    texts = []

    if subtitle_file:
        print("Extracting timecodes from subtitle file...")
        with open(subtitle_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            start_time_match = re.search(r"^[0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3}", line)
            end_time_match = re.search(r" [0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3}", line)

            if start_time_match and end_time_match:
                start_time = start_time_match.group()
                end_time = end_time_match.group()[1:]
                start_times_for_ffmpeg.append(start_time.replace(",", "."))

                start_date = datetime.strptime(start_time, "%H:%M:%S,%f")
                end_date = datetime.strptime(end_time, "%H:%M:%S,%f")
                diff = end_date - start_date
                time_diff.append(str(diff))

                text = lines[i + 1].strip()
                texts.append(text)

    print("Ready to start cutting.\n")

    # Make directory to store output clips
    output_directory = f"{file_name}-clips"
    os.makedirs(output_directory, exist_ok=True)

    num_of_clips = len(start_times_for_ffmpeg)
    export_error_occurred = False

    numerate = input("Should the files be numerated or named by srt line? [1/2] ")

    for k in range(1, num_of_clips + 1):
        j = k - 1
        print(f"Cutting segment no. {k} of {num_of_clips}")
        if numerate == "1":
            filename = f"{k}-{file_name}"
            output_file = os.path.join(output_directory, f"{filename}.{output_format}")
        else:
            filename = (
                re.sub(r'[/\\<>:|*"?]', "", texts[j])
                if len(texts[j].split(" ")) < 5
                else re.sub(r'[/\\<>:|*"?]', "", " ".join(texts[j].split(" ")[:4]))
            )
            output_file = os.path.join(output_directory, f"{filename}.{output_format}")

        command = [
            "ffmpeg",
            "-v",
            "warning",
            "-i",
            file_to_cut,
            "-strict",
            "-2",
            "-ss",
            start_times_for_ffmpeg[j],
            "-t",
            time_diff[j],
            output_file,
        ]

        process = subprocess.run(command)
        if process.returncode == 0:
            print("OK")
            srtfile = os.path.join(output_directory, f"{filename}.srt")
            with open(srtfile, "w", encoding="utf-8") as sub:
                sub.write("1\n")
                sub.write(f"00:00:00,000 --> {time_diff[j].replace('.', ',')}\n")
                sub.write(texts[j])
                sub.write("\n")
        else:
            print("ERR")
            export_error_occurred = True

    if not export_error_occurred:
        print(f"Finished. Files are available in {os.path.abspath(output_directory)}")
    else:
        print("There were errors with the ffmpeg processing. Please see log above.")
