"""Independent edge/center dense-grid arithmetic; no model dependency."""
import numpy as np


def bilinear(field, native_xy, native_size):
    field, points = np.asarray(field, float), np.asarray(native_xy, float)
    size = np.asarray(native_size, float)
    if (field.ndim not in (2, 3) or min(field.shape[:2]) < 2
            or points.ndim != 2 or points.shape[1] != 2 or not len(points)
            or size.shape != (2,) or (size <= 0).any()
            or not all(np.isfinite(x).all() for x in (field, points, size))):
        raise ValueError('finite grid, paired points and positive native dimensions required')
    h, w = field.shape[:2]
    xy = (points+.5)/size*[w, h]-.5
    if (xy < 0).any() or (xy > [w-1, h-1]).any():
        raise ValueError('query outside complete bilinear interpolation domain')
    low = np.floor(xy).astype(int)
    high = np.minimum(low+1, [w-1, h-1])
    fraction = xy-low
    if field.ndim == 3:
        fraction = fraction[:, None, :]
    fx, fy = fraction[..., 0], fraction[..., 1]
    return ((1-fx)*(1-fy)*field[low[:, 1], low[:, 0]]+
            fx*(1-fy)*field[low[:, 1], high[:, 0]]+
            (1-fx)*fy*field[high[:, 1], low[:, 0]]+
            fx*fy*field[high[:, 1], high[:, 0]])


def check():
    h, w = 24, 16
    y, x = np.meshgrid((np.arange(h)+.5)*2/h-1,
                       (np.arange(w)+.5)*2/w-1, indexing='ij')
    field = np.stack((x, y), -1)
    q = np.array([[100.3, 300.7], [359.5, 639.5], [600.2, 900.4]])
    expected = 2*(q+.5)/[720, 1280]-1
    np.testing.assert_allclose(bilinear(field, q, [720, 1280]), expected, atol=1e-12)
    np.testing.assert_allclose(bilinear(x, q, [720, 1280]), expected[:, 0], atol=1e-12)
    for bad in [np.array([[np.nan, 300.]]), np.array([[-1., -1.]])]:
        try:
            bilinear(field, bad, [720, 1280])
        except ValueError:
            continue
        raise AssertionError('invalid query was accepted')


if __name__ == '__main__':
    check()
    print('TECHNICAL_CHECK_PASSED: independent grid arithmetic only')
