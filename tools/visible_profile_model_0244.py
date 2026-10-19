"""Piecewise-exact native identity/pose visible-envelope derivative,no file IO."""
import cv2
import numpy as np
from headfoundry.raster import occluding_edges
from headfoundry.profile_fit import envelope_edges_with_jacobian, project_with_basis_jacobian


def pose(state, initial):
    r, dr = cv2.Rodrigues(initial[:3]+.03*state[:3])
    t = initial[3:].copy()
    t[:2] += .005*state[3:5]
    t[2] *= np.exp(.03*state[5])
    return r, t, dr.reshape(3, 3, 3)


def envelope(state, template, directions, faces, skin_vertices, initial, intrinsic, rows, direction, view):
    dimensions = directions.shape[-1]
    vertices = template+np.einsum('vck,k->vc', directions, state[:dimensions])
    start = dimensions+6*view
    r, t, dr = pose(state[start:start+6], initial)
    cam = vertices@r.T+t
    if (cam[:, 2] <= 1e-6).any():
        raise ValueError('Entire mesh must have positive depth')
    edges = occluding_edges(vertices, faces, np.c_[r, t])
    edges = edges[np.isin(edges, skin_vertices).all(axis=1)]
    basis = np.zeros((*cam.shape, len(state)))
    basis[:, :, :dimensions] = np.einsum('ij,vjk->vik', r, directions)
    basis[:, :, start:start+3] = .03*np.einsum('kij,vj->vik', dr, vertices)
    basis[:, 0, start+3] = basis[:, 1, start+4] = .005
    basis[:, 2, start+5] = .03*t[2]
    supports, jacobian = envelope_edges_with_jacobian(cam, edges, intrinsic@np.c_[np.eye(3), np.zeros(3)],
        rows, direction, basis)
    return np.array([s[2][0] for s in supports]), jacobian, supports, np.c_[r, t]


def frontal_constraints(beta, base, directions, projection, target):
    current, jacobian = project_with_basis_jacobian(base+np.einsum('nck,k->nc', directions, beta), directions, projection)
    delta = current-target
    return 4.-np.einsum('ni,ni->n', delta, delta), -2*np.einsum('ni,nik->nk', delta, jacobian)


def near_constraint_faces(vertices, template, faces):
    old = np.cross(template[faces[:, 1]]-template[faces[:, 0]], template[faces[:, 2]]-template[faces[:, 0]])
    new = np.cross(vertices[faces[:, 1]]-vertices[faces[:, 0]], vertices[faces[:, 2]]-vertices[faces[:, 0]])
    denominator = np.einsum('ni,ni->n', old, old)
    signed = np.einsum('ni,ni->n', old, new)/denominator
    squared = np.einsum('ni,ni->n', new, new)/denominator
    return np.flatnonzero((signed <= 1e-6+1e-4) | (squared <= .20001**2+1e-4) | (squared >= 4.99999**2-1e-4))
