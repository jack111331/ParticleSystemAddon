import numpy as np
class Solver:
    #         particle_system.time_step += step ?
    def solve_step(self, particle_system, step):
        pass

    def reset_solver(self, particle_system):
        pass

    def save_solver(self):
        pass

class ForwardEulerSolver(Solver):
    def solve_step(self, particle_system, step):
        current_state = particle_system.get_state()
        derivative_state = particle_system.derivative_eval()
        particle_system.set_state(current_state + step * derivative_state)

    def save_solver(self):
        return "forward_euler_solver"

class SecondOrderRKSolver(Solver):
    def solve_step(self, particle_system, step):
        origin_state = particle_system.get_state()
        derivative_state = particle_system.derivative_eval()
        particle_system.set_state(origin_state + step/2.0 * derivative_state)

        derivative_state = particle_system.derivative_eval()
        particle_system.set_state(origin_state + step * derivative_state)

    def save_solver(self):
        return "second_order_rk_solver"

class FourthOrderRKSolver(Solver):
    def solve_step(self, particle_system, step):
        origin_state = particle_system.get_state()

        # Phase 1
        derivative_state_1 = particle_system.derivative_eval()
        particle_system.set_state(origin_state + step/2.0 * derivative_state_1)

        # Phase 2
        derivative_state_2 = particle_system.derivative_eval()
        particle_system.set_state(origin_state + step/2.0 * derivative_state_2)

        # Phase 3
        derivative_state_3 = particle_system.derivative_eval()
        particle_system.set_state(origin_state + step * derivative_state_3)

        derivative_state_4 = particle_system.derivative_eval()
        particle_system.set_state(origin_state + step * (derivative_state_1 + 2.0 * derivative_state_2 + 2.0 * derivative_state_3 + derivative_state_4)/6.0)

    def save_solver(self):
        return "fourth_order_rk_solver"

class VerletSolver(Solver):
    def solve_step(self, particle_system, step):
        # FIXME
        # http://physics.drexel.edu/~valliere/PHYS305/Diff_Eq_Integrators/Verlet_Methods/Verlet/
        origin_state = particle_system.get_state()
        derivative_state = particle_system.derivative_eval()
        origin_state[:, 3:6] = origin_state[:, 3:6] + step * derivative_state[:, 3:6]/2.0
        origin_state[:, 0:3] = origin_state[:, 0:3] + step * origin_state[:, 3:6]
        particle_system.set_state(origin_state)
        derivative_state = particle_system.derivative_eval()
        origin_state[:, 3:6] = origin_state[:, 3:6] + step * derivative_state[:, 3:6]/2.0

        particle_system.set_state(origin_state)

    def save_solver(self):
        return "verlet_solver"

class LeapfrogSolver(Solver):
    def __init__(self):
        self.half_velocity = None
        self.first = True

    def reset_solver(self, particle_system):
        self.half_velocity = None
        self.first = True

    def solve_step(self, particle_system, step):
        # https://github.com/runiteking1/sph/blob/master/leapfrog.c
        num_particles = len(particle_system.particle_list)
        if self.first == True:
            origin_state = particle_system.get_state()
            self.half_velocity = origin_state[:, 3:6].copy()
            derivative_state = particle_system.derivative_eval()
            self.half_velocity += step/2.0 * derivative_state[:, 3:6]
            origin_state[:, 3:6] += step * derivative_state[:, 3:6]
            origin_state[:, 0:3] += step * self.half_velocity
            particle_system.set_state(origin_state)
            self.first = False
        else:
            origin_state = particle_system.get_state()
            derivative_state = particle_system.derivative_eval()
            self.half_velocity += step * derivative_state[:, 3:6]
            origin_state[:, 3:6] = self.half_velocity.copy()
            origin_state[:, 3:6] += step / 2.0 * derivative_state[:, 3:6]
            origin_state[:, 0:6] += step * self.half_velocity
            particle_system.set_state(origin_state)

    def save_solver(self):
        return "leap_frog_solver"

class BackwardEulerSolver(Solver):
    def __init__(self):
        self.stiffness = 3.0

    def solve_step(self, particle_system, step):
        current_state = particle_system.get_state()

        # Velocity is unknown
        particle_system.set_state(1/(1 + step * self.stiffness) * current_state)

    def save_solver(self):
        return "backward_euler_solver"
