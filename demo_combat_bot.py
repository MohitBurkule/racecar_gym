"""Run combat bot demo with visual inspection and frame saving."""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

import gymnasium
import racecar_gym.envs.gym_api
import numpy as np
import time
import pybullet as p
from PIL import Image

def main():
    print("=== Combat Bot Demo ===")
    print("Robot starts at bottom-left (-1.5, -1.5)")
    print("Target is at top-right (1.5, 1.5)")
    print("Frames will be saved to combat_frames/")
    print("Close the window to exit.\n")

    # Create output directory
    os.makedirs("combat_frames", exist_ok=True)

    env = gymnasium.make('SingleAgentCombat_bot-v0', render_mode='human')

    obs, info = env.reset(options={'mode': 'fixed'})
    print(f"Start: pos={obs['external_camera'][:2].round(2)}, heading={obs['external_camera'][2]:.2f}")

    step = 0
    frame_count = 0
    save_every = 5  # Save every N frames to reduce disk usage

    while step < 5000:
        pos = obs['external_camera'][:2]
        heading = obs['external_camera'][2]
        target = np.array([1.5, 1.5])
        error = target - pos
        dist = np.linalg.norm(error)

        # Simple P-controller
        target_heading = np.arctan2(error[1], error[0])
        heading_error = (target_heading - heading + np.pi) % (2 * np.pi) - np.pi

        speed = min(0.7, dist * 2.0)
        motor_left = np.clip(speed - heading_error * 2.0, -1, 1)
        motor_right = np.clip(speed + heading_error * 2.0, -1, 1)

        action = {'motor_left': np.array([motor_left]), 'motor_right': np.array([motor_right])}
        obs, reward, done, truncated, info = env.step(action)

        # Capture frame using PyBullet camera (bird's eye view)
        if step % save_every == 0:
            # Camera params for bird's eye view
            width, height = 640, 480
            view_matrix = p.computeViewMatrix(
                cameraEyePosition=[0, 0, 3],
                cameraTargetPosition=[0, 0, 0],
                cameraUpVector=[0, 1, 0]
            )
            proj_matrix = p.computeProjectionMatrixFOV(
                fov=60, aspect=float(width)/height, nearVal=0.1, farVal=10.0
            )
            w, h, rgb, depth, seg = p.getCameraImage(
                width, height, view_matrix, proj_matrix,
                renderer=p.ER_BULLET_HARDWARE_OPENGL
            )
            frame = np.reshape(np.array(rgb, dtype=np.uint8), (h, w, 4))[:, :, :3]
            Image.fromarray(frame).save(f"combat_frames/frame_{frame_count:04d}.png")
            frame_count += 1

        step += 1
        if step % 100 == 0:
            print(f"Step {step}: pos={pos.round(2)}, dist={dist:.2f}, motors=({motor_left:.2f}, {motor_right:.2f})")

        if done or truncated:
            print(f"Done! Final dist={dist:.2f}")
            # Save final frame
            width, height = 640, 480
            view_matrix = p.computeViewMatrix(
                cameraEyePosition=[0, 0, 3],
                cameraTargetPosition=[0, 0, 0],
                cameraUpVector=[0, 1, 0]
            )
            proj_matrix = p.computeProjectionMatrixFOV(
                fov=60, aspect=float(width)/height, nearVal=0.1, farVal=10.0
            )
            w, h, rgb, depth, seg = p.getCameraImage(
                width, height, view_matrix, proj_matrix,
                renderer=p.ER_BULLET_HARDWARE_OPENGL
            )
            final_frame = np.reshape(np.array(rgb, dtype=np.uint8), (h, w, 4))[:, :, :3]
            Image.fromarray(final_frame).save(f"combat_frames/frame_{frame_count:04d}.png")
            break

    env.close()
    print(f"\nSaved {frame_count + 1} frames to combat_frames/")
    print("Create video with: ffmpeg -framerate 30 -i combat_frames/frame_%04d.png -c:v libx264 -pix_fmt yuv420p output.mp4")

if __name__ == "__main__":
    main()
