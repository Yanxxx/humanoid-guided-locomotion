# Copyright (c) 2022-2025, The Isaac Lab Project Developers. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Configuration for the Unitree G1 guided locomotion task, based on the official G1 rough terrain config."""

from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.utils import configclass

# Import the official G1 rough terrain configuration as our base
from isaaclab_tasks.manager_based.locomotion.velocity.config.g1.rough_env_cfg import G1Rewards, G1RoughEnvCfg

# Import our custom reward functions
from .mdp import rewards


# --- 1. Define a new set of rewards that inherits from the base G1 rewards ---
@configclass
class GuidedG1Rewards(G1Rewards):
    """Custom reward terms for the guided locomotion task."""

    # We are REPLACING the original tracking rewards with our own.
    # The new rewards will track x, y, and z-rotation commands.
    track_lin_vel_xy_exp = RewTerm(func=rewards.reward_lin_vel_xy_exp, weight=1.5, params={"std": 0.25})
    track_ang_vel_z_exp = RewTerm(func=rewards.reward_ang_vel_z_exp, weight=0.75, params={"std": 0.25})

    # The other rewards (termination_penalty, feet_air_time, etc.) are inherited from G1Rewards automatically.


# --- 2. Define the main environment configuration ---
@configclass
class GuidedG1RoughEnvCfg(G1RoughEnvCfg):
    """Configuration for the G1 guided locomotion environment."""

    # Point to our new custom rewards class
    rewards: GuidedG1Rewards = GuidedG1Rewards()

    def __post_init__(self):
        """Post-initialization to modify the inherited settings."""
        # Run the parent class's __post_init__ first
        super().__post_init__()

        # --- Modify Commands ---
        # Update the command ranges to allow for x, y, and yaw velocity commands.
        self.commands.base_velocity.ranges.lin_vel_x = (-1.0, 1.5)
        self.commands.base_velocity.ranges.lin_vel_y = (-0.8, 0.8) # Allow sideways motion
        self.commands.base_velocity.ranges.ang_vel_z = (-1.0, 1.0)

        # --- Modify Observations ---
        # The base G1 config already includes commands in the observations, so we don't need to change anything here.
        # The policy will see the commands by default.

        # --- Modify Rewards ---
        # The G1 base config sets the vertical velocity penalty to 0. We want to re-enable it.
        self.rewards.lin_vel_z_l2.weight = -2.0
