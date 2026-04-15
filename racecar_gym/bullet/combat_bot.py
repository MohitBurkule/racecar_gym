from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

import pybullet

from racecar_gym.bullet.actuators import BulletActuator
from racecar_gym.bullet.sensors import BulletSensor
from racecar_gym.core.definitions import Pose
from racecar_gym.core.vehicles import Vehicle


class CombatBot(Vehicle):
    @dataclass
    class Config:
        urdf_file: str
        color: Tuple[float, float, float, float]

    def __init__(self, sensors: List[BulletSensor], actuators: List[BulletActuator], config: Config):
        super().__init__()
        self._id = None
        self._config = config

        # Actuator indices for combat_bot differential drive
        self._actuator_indices = {
            'motor_left': [0],   # left_wheel_joint
            'motor_right': [1],  # right_wheel_joint
        }
        self._actuators = dict([(a.name, a) for a in actuators])
        self._sensors = sensors

    @property
    def id(self) -> Any:
        return self._id

    @property
    def sensors(self) -> List[BulletSensor]:
        return self._sensors

    @property
    def actuators(self) -> Dict[str, BulletActuator]:
        return self._actuators

    def reset(self, pose: Pose):
        if not self._id:
            self._id = self._load_model(self._config.urdf_file, initial_pose=pose)
            self._setup_motors()
        else:
            pos, orn = pose
            pybullet.resetBasePositionAndOrientation(self._id, pos, pybullet.getQuaternionFromEuler(orn))

        for sensor in self.sensors:
            sensor.reset(body_id=self._id, joint_index=None)

        for name, actuator in self.actuators.items():
            joint_indices = None
            if name in self._actuator_indices:
                joint_indices = self._actuator_indices[name]
            actuator.reset(body_id=self._id, joint_indices=joint_indices)

    def _load_model(self, model: str, initial_pose: Pose) -> int:
        position, orientation = initial_pose
        orientation = pybullet.getQuaternionFromEuler(orientation)
        id = pybullet.loadURDF(model, position, orientation)
        pybullet.changeVisualShape(id, -1, rgbaColor=self._config.color)
        return id

    def _setup_motors(self):
        # Disable motors for all joints initially
        for wheel in range(pybullet.getNumJoints(self._id)):
            pybullet.setJointMotorControl2(self._id,
                                          wheel,
                                          pybullet.VELOCITY_CONTROL,
                                          targetVelocity=0,
                                          force=0)
