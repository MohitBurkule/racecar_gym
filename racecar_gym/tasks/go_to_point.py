from typing import Dict, Tuple, List, Any
import numpy as np

from .task import Task


class GoToPointTask(Task):
    def __init__(self,
                 target_position: Tuple[float, float],
                 time_limit: float = 30.0,
                 success_threshold: float = 0.05,
                 collision_penalty: float = -100.0,
                 success_reward: float = 100.0,
                 time_penalty: float = -0.1):
        self._target = np.array(target_position)
        self._time_limit = time_limit
        self._threshold = success_threshold
        self._collision_penalty = collision_penalty
        self._success_reward = success_reward
        self._time_penalty = time_penalty
        self._initial_distance = None

    def reward(self, agent_id: str, state: Dict[str, Any], action: Dict[str, np.ndarray]) -> float:
        agent_state = state[agent_id]
        position = agent_state['pose'][:2]

        # Calculate distance to target
        distance = np.linalg.norm(position - self._target)

        # Initialize on first call
        if self._initial_distance is None:
            self._initial_distance = distance

        # Check collision
        if agent_state.get('wall_collision', False):
            return self._collision_penalty

        # Check if reached
        if distance < self._threshold:
            return self._success_reward

        # Progress reward: reward getting closer
        if self._initial_distance > 0:
            progress = (self._initial_distance - distance) / self._initial_distance
            return progress * 10 + self._time_penalty
        return self._time_penalty

    def done(self, agent_id: str, state: Dict[str, Any]) -> bool:
        agent_state = state[agent_id]
        position = agent_state['pose'][:2]
        distance = np.linalg.norm(position - self._target)

        # Success condition
        if distance < self._threshold:
            return True

        # Failure conditions
        if agent_state.get('wall_collision', False):
            return True

        # Timeout
        if agent_state['time'] > self._time_limit:
            return True

        return False

    def reset(self):
        self._initial_distance = None
