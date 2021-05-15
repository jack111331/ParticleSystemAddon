import numpy as np
class Solver:
    #         particle_system.time_step += step ?
    def solve_step(self, particle_system, step):
        pass

class ForwardEulerSolver(Solver):
    def solve_step(self, particle_system, step):
        current_state = particle_system.get_state()
        derivative_state = particle_system.derivative_eval()
        particle_system.set_state(current_state + step * derivative_state)

class SecondOrderRKSolver(Solver):
    def solve_step(self, particle_system, step):
        origin_state = particle_system.get_state()
        derivative_state = particle_system.derivative_eval()
        particle_system.set_state(origin_state + step/2.0 * derivative_state)

        derivative_state = particle_system.derivative_eval()
        particle_system.set_state(origin_state + step * derivative_state)

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

class BackwardEulerSolver(Solver):
    def __init__(self):
        self.stiffness = 3.0

    def solve_step(self, particle_system, step):
        current_state = particle_system.get_state()

        # Velocity is unknown
        particle_system.set_state(1/(1 + step * self.stiffness) * current_state)
