# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Racecar Gym — reinforcement learning environment for autonomous racing. Built on PyBullet physics, exposes Gymnasium and PettingZoo APIs. Supports single-agent and multi-agent scenarios on multiple tracks.

## Setup & Commands

```bash
# Install (editable)
pip install -e .

# Download track assets (required before running)
cd models/scenes
VERSION=v1.0.0
wget https://github.com/axelbr/racecar_gym/releases/download/tracks-${VERSION}/all.zip
unzip all.zip

# No test suite exists. tests/ is empty.

# Run examples
python examples/gym_examples/single_agent.py
python examples/pettingzoo_examples/pettingzoo_single_agent.py
```

## Architecture

Three-layer design: **Core** → **Bullet** → **Envs**.

### Core (`racecar_gym/core/`)

Abstract interfaces defining the simulation contract:
- `world.py` — World base class
- `vehicles.py` — Vehicle base class
- `agents.py` — Agent: binds vehicle + sensors + actuators + task
- `sensors.py`, `actuators.py` — Sensor/actuator interfaces
- `definitions.py` — Shared types (Pose, Timestep)
- `specs.py` — Observation/action space specs

### Bullet (`racecar_gym/bullet/`)

PyBullet implementation of core interfaces:
- `world.py` — Physics world, collision detection, track loading
- `vehicle.py` — Vehicle dynamics via PyBullet URDF
- `sensors.py` — LIDAR, camera, pose, velocity, acceleration sensors
- `actuators.py` — Motor, steering, speed actuators

### Envs (`racecar_gym/envs/`)

Gym/PettingZoo wrappers over core+bullet:
- `gym_api/` — `SingleAgentRaceEnv`, `MultiAgentRaceEnv`, vectorized variants, `changing_track.py`
- `gym_api/wrappers/` — Frame stack, time limit, old gym compat
- `pettingzoo_api/` — Parallel and sequential PettingZoo envs
- `scenarios.py` — Loads YAML scenario configs into environment instances

### Tasks (`racecar_gym/tasks/`)

Reward/termination logic:
- `progress_based.py` — `MaximizeProgressTask`, `RankDiscountedMaximizeProgressTask`, action-regularized variant
- `tracking.py` — `WaypointFollow` task

### Config

- `scenarios/*.yml` — Per-track scenario definitions (world name, agent configs, sensor lists, task params)
- `models/vehicles/` — Vehicle URDF configs
- `models/scenes/` — Track meshes (downloaded separately)

## Key Patterns

- **Scenario-driven env creation**: Envs built from YAML scenarios via `scenarios.py`, not hardcoded. New tracks = new YAML file.
- **Agent = Vehicle + Task**: Each agent binds a vehicle config, sensor suite, and task. Scenarios define which agents participate.
- **Observation spaces**: Dict-based. Keys depend on configured sensors (lidar, pose, velocity, acceleration). Space specs in `core/specs.py`.
- **Action space**: Continuous, typically `[steering, acceleration]`. Defined per actuator config.
- **Multi-agent**: Up to 4 agents (IDs: A, B, C, D). Collision detection between agents enabled by default.
- **Render modes**: `human`, `rgb_array_follow`, `rgb_array_birds_eye`, `rgb_array_lidar`.

## Dependencies

pybullet==3.2.5, gymnasium==0.28.1, pettingzoo==1.22.3, numpy, scipy, yamldataclassconfig==1.5.0, nptyping<2.0.
