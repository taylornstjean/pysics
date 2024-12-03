from pysics.render.render import run_render
from pysics.core.models import Particle
import numpy as np

if __name__ == "__main__":

    p1 = Particle(1e12, np.array([2., 2., 0.]), np.array([10., 0., 0.]))
    p2 = Particle(1e12, np.array([1.1, 0., 2.]), np.array([20., 0., 0.]))
    p3 = Particle(1e12, np.array([1., 2.1, 0.]), np.array([10., 21., 0.]))
    p4 = Particle(1e12, np.array([0.5, 2., 0.]), np.array([10., 0., 20.]))
    run_render(p1, p2, p3, p4)
