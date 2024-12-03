import numpy as np
from astropy.constants import G
from pysics.core.base import KeepRefs


class Particle(KeepRefs):

    def __init__(self, mass: float | int, velocity: np.ndarray, position: np.ndarray) -> None:
        super(Particle, self).__init__()

        self.m = mass
        self.v = velocity
        self.p = position

    def interact(self, t_res: float | int):

        force_vector = np.array([0., 0., 0.])

        for obj in self.instances():
            if obj._id == self._id:
                continue

            d = np.subtract(self.p, obj.p)

            if np.linalg.norm(d) != 0:
                f = -G.value * ((obj.m * self.m) / (np.linalg.norm(d) ** 3)) * d
            else:
                f = 0

            force_vector = np.add(force_vector, f)

        p_prime = np.add(self.m * self.v, force_vector * t_res)
        self.p = self.p + (p_prime / self.m) * t_res
        self.v = p_prime / self.m
