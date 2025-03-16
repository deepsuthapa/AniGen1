from flask import Flask, request, jsonify, send_file
import torch
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
import os
import time

def load_model():
    pipe = DiffusionPipeline.from_pretrained("cerspense/zeroscope_v2_576w", torch_dtype=torch.float16)
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    pipe.to("cuda")
    return pipe

app = Flask(__name__)
model = load_model()

@app.route("/generate", methods=["POST"])
def generate_video():
    try:
        data = request.json
        prompt = data.get("prompt", "")
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        output_dir = "generated_videos"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"output_{int(time.time())}.mp4")
        
        video_frames = model(prompt, num_inference_steps=50).frames
        video_frames[0].save(output_path, format="MP4")
        
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
