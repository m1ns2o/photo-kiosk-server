import subprocess

input_file = "input.mp4"
output_file = "output.mp4"
target_bitrate = "5000k"  # Set your desired bitrate

command = [
    "ffmpeg",
    "-i", input_file,
    "-b:v", target_bitrate,
    "-c:a", "copy",  # Copy audio codec without re-encoding
    output_file
]

subprocess.run(command)
