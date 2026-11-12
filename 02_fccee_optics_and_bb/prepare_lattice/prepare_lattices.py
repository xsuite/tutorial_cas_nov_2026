"""Regenerate the common FCC-ee lattice and its two strength files.

Run with the tutorial's Xsuite environment. The default input is the original
fccee_z.json beside this script; --source can select another input file.
Generated lattice and strength files are written to the parent exercise folder
and copied to its solution subfolder so the solutions can run independently.
The original lattice is read only. The notebooks use the generated files directly
and do not run this script. All exercises use the same simplified magnet models.
"""

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
import xtrack as xt


KNOBS_LEFT = ['kqd16l', 'kqf17l', 'kqd18l', 'kqf19l', 'kqd20l',
              'kqd8m', 'kqf9m', 'kqd10m']
KNOBS_RIGHT = ['kqf17r', 'kqd18r', 'kqf19r', 'kqd20r',
               'kqd8mr', 'kqf9mr', 'kqd10mr']
OPTICS_KNOBS = KNOBS_LEFT + KNOBS_RIGHT + ['kqf2', 'kqd1', 'ksf1', 'ksd1']


def save_strengths(env, path):
    # All other strengths and expressions remain in the common lattice.
    values = {name: float(env[name]) for name in OPTICS_KNOBS}
    path.write_text(json.dumps(values, indent=2, sort_keys=True) + '\n')


def prepare(source, output):
    env = xt.load(source)
    line = env.fccee_p_ring
    line.configure_radiation(model=None)

    # Use the same fast magnet models for optics and tracking in every exercise.
    tt_magnets = line.get_table()
    line.set(
        tt_magnets.rows.match(element_type='Bend|RBend|Quadrupole'),
        model='mat-kick-mat', integrator='uniform', num_multipole_kicks=1,
    )
    line.configure_sextupole_model(
        model='drift-kick-drift-expanded', integrator='teapot',
        num_multipole_kicks=1,
    )
    # Small numerical probes resolve the narrow beams at the interaction points.
    # Leave chromaticity calculation enabled for the optics exercises.
    beta_gamma = line.particle_ref.beta0[0] * line.particle_ref.gamma0[0]
    line.twiss_default.update(
        nemitt_x=0.71e-9 * beta_gamma,
        nemitt_y=2.1e-12 * beta_gamma,
        step_W_sigma=0.001,
        steps_R_matrix=dict(
            dx=1e-8, dpx=1e-9, dy=1e-10, dpy=1e-10,
            dzeta=1e-4, ddelta=1e-5,
        ),
    )
    tw_before_split = line.twiss4d(delta_chrom=1e-6)

    env['kqd8mr'] = env['kqd8m']
    env['kqf9mr'] = env['kqf9m']
    env['kqd10mr'] = env['kqd10m']
    env.set(['qd8m.0', 'qd8m.2', 'qd8m.4', 'qd8m.6'], k1='kqd8mr')
    env.set(['qf9m.0', 'qf9m.2', 'qf9m.4', 'qf9m.6'], k1='kqf9mr')
    env.set(['qd10m.0', 'qd10m.2', 'qd10m.4', 'qd10m.6'], k1='kqd10mr')

    tw0 = line.twiss4d(delta_chrom=1e-6)
    np.testing.assert_allclose([tw0.qx, tw0.qy],
                               [tw_before_split.qx, tw_before_split.qy], atol=1e-9, rtol=0)
    env.to_json(output / 'fccee_z.json')
    save_strengths(env, output / 'optics_nominal.json')

    ip = 'ipd'
    start = 'end_ds_start_straight_ipd'
    end = 'end_straight_start_ds_ipd'
    targets_ip = [
        xt.Target('betx', at=ip, value=8 * tw0['betx', ip], tol=1e-8, weight=10),
        xt.Target('bety', at=ip, value=8 * tw0['bety', ip], tol=1e-10, weight=1000),
        xt.TargetSet(alfx=0, alfy=0, at=ip, tol=1e-7),
    ]
    line.match(
        method='4d', start=start, end=ip, init=tw0.get_twiss_init(start),
        vary=xt.VaryList(KNOBS_LEFT, step=1e-8), targets=targets_ip,
        n_steps_max=80,
    )
    opt_right = line.match(
        method='4d', start=ip, end=end, init=tw0.get_twiss_init(end), init_at=end,
        vary=xt.VaryList(KNOBS_RIGHT, step=1e-8), targets=targets_ip,
        n_steps_max=80,
    )
    # First match the IP, then constrain the horizontal beta peak.
    opt_right = opt_right.clone(add_targets=[
        xt.Target(lambda tw: tw.betx.max(), xt.LessThan(2000),
                  tol=1e-3, weight=1e-3, tag='max_betx'),
    ])
    opt_right.solve()
    line.match(
        method='4d', vary=xt.VaryList(['kqf2', 'kqd1'], step=1e-8),
        targets=xt.TargetSet(qx=tw0.qx, qy=tw0.qy, tol=1e-8),
    )
    line.match(
        method='4d', delta_chrom=1e-6,
        vary=xt.VaryList(['ksf1', 'ksd1'], step=1e-5),
        targets=xt.TargetSet(dqx=tw0.dqx, dqy=tw0.dqy, tol=1e-3),
    )
    tw = line.twiss4d(delta_chrom=1e-6)
    ips = ['ipa', 'ipd', 'ipg', 'ipj']
    np.testing.assert_allclose(tw.rows[ips].betx / tw0.rows[ips].betx, 8, rtol=5e-3)
    np.testing.assert_allclose(tw.rows[ips].bety / tw0.rows[ips].bety, 8, rtol=5e-3)
    np.testing.assert_allclose([tw.qx, tw.qy], [tw0.qx, tw0.qy], atol=1e-8, rtol=0)
    np.testing.assert_allclose([tw.dqx, tw.dqy], [tw0.dqx, tw0.dqy], atol=1e-3, rtol=0)
    assert tw.rows[ip:end].betx.max() < 2000
    print('Maximum horizontal beta in right half [m]:', tw.rows[ip:end].betx.max())
    save_strengths(env, output / 'optics_larger_ip_beta.json')

    # Check switching both ways using exactly the student-facing API.
    for filename, reference in [('optics_nominal.json', tw0),
                                ('optics_larger_ip_beta.json', tw)]:
        env.vars.load(output / filename)
        check = line.twiss4d(delta_chrom=1e-6)
        np.testing.assert_allclose(check.rows[ips].betx, reference.rows[ips].betx,
                                   rtol=1e-7)
        np.testing.assert_allclose(check.rows[ips].bety, reference.rows[ips].bety,
                                   rtol=1e-7)
        np.testing.assert_allclose([check.qx, check.qy, check.dqx, check.dqy],
                                   [reference.qx, reference.qy, reference.dqx, reference.dqy],
                                   atol=1e-6, rtol=0)
        print(filename, 'verified:', check.qx, check.qy, check.dqx, check.dqy)

    solution = output / 'solution'
    solution.mkdir(exist_ok=True)
    for filename in ['fccee_z.json', 'optics_nominal.json', 'optics_larger_ip_beta.json']:
        shutil.copyfile(output / filename, solution / filename)


if __name__ == '__main__':
    folder = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=folder / 'fccee_z.json')
    args = parser.parse_args()
    prepare(args.source, folder.parent)
