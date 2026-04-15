"""Run a random-agent demo on Austria track and save as video."""
import os
import gymnasium
import racecar_gym.envs.gym_api
import numpy as np

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "demo_output.mp4")
NUM_STEPS = 500
FPS = 60
TRACK = "SingleAgentAustria-v0"


def run():
    env = gymnasium.make(TRACK, render_mode="rgb_array_birds_eye")
    obs, info = env.reset(options=dict(mode="grid"))
    print(f"Observation keys: {list(obs.keys())}")
    print(f"Action space: {env.action_space}")
    print(f"Running {NUM_STEPS} steps...")

    frames = []
    for t in range(NUM_STEPS):
        action = env.action_space.sample()
        obs, rewards, terminated, truncated, states = env.step(action)
        frame = env.render()
        if frame is not None:
            frames.append(frame.astype(np.uint8))
        if terminated or truncated:
            print(f"Episode ended at step {t}")
            break
        if (t + 1) % 100 == 0:
            pose = states["pose"][:3].round(3)
            print(f"  Step {t+1}/{NUM_STEPS} — car at {pose}")

    env.close()

    if not frames:
        print("No frames captured.")
        return

    try:
        import imageio.v2 as imageio

        imageio.mimwrite(OUTPUT_PATH, frames, fps=FPS, codec="libx264", quality=8)
        print(f"Saved video: {OUTPUT_PATH} ({len(frames)} frames, {FPS} fps)")
    except ImportError:
        # Fallback: save frames as images
        from PIL import Image

        img_dir = os.path.join(os.path.dirname(__file__), "demo_frames")
        os.makedirs(img_dir, exist_ok=True)
        for i, f in enumerate(frames):
            Image.fromarray(f).save(os.path.join(img_dir, f"frame_{i:04d}.png"))
        print(f"imageio not installed. Saved {len(frames)} frames to {img_dir}/")
        print("Install imageio for video: pip install imageio[ffmpeg]")


if __name__ == "__main__":
    run()
