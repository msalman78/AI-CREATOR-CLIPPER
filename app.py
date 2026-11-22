import os
import subprocess
import tempfile
from pathlib import Path
from flask import Flask, request, send_file, redirect

app = Flask(__name__)

HTML = """
<h1>AI Creator Clipper</h1>
<p>Upload your video and create a vertical Shorts clip.</p>
<form action="/clip" method="post" enctype="multipart/form-data">
<input type="file" name="video" required>
<br><br>
Start time (seconds):
<input type="number" name="start" value="0">
<br><br>
Duration (seconds):
<input type="number" name="duration" value="30">
<br><br>
<button type="submit">Create Clip</button>
</form>
"""

@app.route("/")
def home():
    return HTML

@app.route("/clip", methods=["POST"])
def clip():
    video = request.files.get("video")
    if not video or not video.filename:
        return "Please select a video."

    ext = Path(video.filename).suffix.lower()
    if ext not in [".mp4", ".mov", ".mkv", ".avi", ".webm"]:
        return "Unsupported video format."

    try:
        start = float(request.form.get("start", 0))
        duration = float(request.form.get("duration", 30))
        if start < 0 or duration < 1 or duration > 600:
            return "Invalid time settings."
    except ValueError:
        return "Enter valid numbers."

    folder = tempfile.mkdtemp()
    input_file = os.path.join(folder, "input" + ext)
    output_file = os.path.join(folder, "shorts_clip.mp4")
    video.save(input_file)

    command = [
        "ffmpeg", "-y", "-ss", str(start),
        "-i", input_file, "-t", str(duration),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v", "libx264", "-preset", "veryfast",
        "-c:a", "aac", "-pix_fmt", "yuv420p",
        output_file
    ]

    result = subprocess.run(command, capture_output=True)
    if result.returncode != 0:
        return "Video processing failed. Please try again."

    return send_file(
        output_file,
        as_attachment=True,
        download_name="shorts_clip.mp4"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
