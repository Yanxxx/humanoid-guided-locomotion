import torch
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv

# -- Tracking Rewards (Positive Reinforcement) --

def reward_lin_vel_xy_exp(env: "ManagerBasedRLEnv", std: float) -> torch.Tensor:
    """Reward the robot for matching the commanded linear velocity in the x-y plane."""
    # Get the robot asset from the scene
    robot = env.scene["robot"]
    # Get the target velocity command
    target_vel = env.command_manager.get_command("base_velocity")[:, :2]
    # Get the robot's actual velocity
    robot_vel = robot.data.root_lin_vel_b[:, :2]
    # Calculate an exponential reward based on the error
    error = torch.sum(torch.square(target_vel - robot_vel), dim=1)
    return torch.exp(-error / std**2)

def reward_ang_vel_z_exp(env: "ManagerBasedRLEnv", std: float) -> torch.Tensor:
    """Reward the robot for matching the commanded angular velocity around the z-axis."""
    # Get the robot asset from the scene
    robot = env.scene["robot"]
    # Get the target turning command
    target_vel = env.command_manager.get_command("base_velocity")[:, 2]
    # Get the robot's actual turning velocity
    robot_vel = robot.data.root_ang_vel_b[:, 2]
    # Calculate an exponential reward based on the error
    error = torch.square(target_vel - robot_vel)
    return torch.exp(-error / std**2)

# -- Penalties (Negative Reinforcement) --

def penalize_lin_vel_z_l2(env: "ManagerBasedRLEnv") -> torch.Tensor:
    """Penalize vertical velocity to prevent jumping or falling through the floor."""
    robot = env.scene["robot"]
    return torch.square(robot.data.root_lin_vel_b[:, 2])

def penalize_ang_vel_xy_l2(env: "ManagerBasedRLEnv") -> torch.Tensor:
    """Penalize rolling and pitching to encourage stability."""
    robot = env.scene["robot"]
    return torch.sum(torch.square(robot.data.root_ang_vel_b[:, :2]), dim=1)

def penalize_dof_acc_l2(env: "ManagerBasedRLEnv") -> torch.Tensor:
    """Penalize high joint accelerations to encourage smooth actions."""
    robot = env.scene["robot"]
    return torch.sum(torch.square(robot.data.dof_acc), dim=1)

def penalize_action_rate_l2(env: "ManagerBasedRLEnv") -> torch.Tensor:
    """Penalize large changes in actions between steps to encourage smoothness."""
    return torch.sum(torch.square(env.action_manager.action - env.action_manager.prev_action), dim=1)

def penalize_joint_pos_limits(env: "ManagerBasedRLEnv") -> torch.Tensor:
    """Penalize the robot for exceeding its joint limits."""
    robot = env.scene["robot"]
    out_of_bounds = -(robot.data.dof_pos - robot.data.soft_dof_pos_limits[..., 0]).clamp(max=0.0)
    out_of_bounds += (robot.data.dof_pos - robot.data.soft_dof_pos_limits[..., 1]).clamp(min=0.0)
    return torch.sum(out_of_bounds, dim=1)
