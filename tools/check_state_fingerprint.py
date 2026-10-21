"""Bounded-memory exact array-state fingerprint; no neural runtime required."""
import hashlib
import json

import numpy as np


def state_fingerprint(named_arrays):
    digest = hashlib.sha256()
    for name in sorted(named_arrays):
        array = np.asarray(named_arrays[name])
        if array.dtype.hasobject or not array.dtype.itemsize:
            raise ValueError('object arrays do not have deterministic value bytes')
        header = json.dumps([name, array.dtype.str, list(array.shape)],
                            separators=(',', ':')).encode('utf8')
        digest.update(len(header).to_bytes(8, 'little'))
        digest.update(header)
        # flat slicing copies only this bounded chunk, even for strided views.
        step = max(1, (1024*1024)//array.dtype.itemsize)
        for start in range(0, array.size, step):
            digest.update(array.flat[start:start+step].tobytes())
    return digest.hexdigest()


def check():
    a = np.arange(24, dtype=np.float32).reshape(4, 6)
    base = {'weight': a, 'count': np.array(2, dtype=np.int64)}
    expected = state_fingerprint(base)
    alternate = {'count': base['count'], 'weight': np.asfortranarray(a)}
    assert state_fingerprint(alternate) == expected
    changed = a.copy()
    changed[0, 0] = np.nextafter(changed[0, 0], np.float32(1))
    assert state_fingerprint({**base, 'weight': changed}) != expected
    assert state_fingerprint({**base, 'weight': a.view(np.int32)}) != expected
    assert state_fingerprint({**base, 'weight': a.reshape(2, 12)}) != expected
    assert state_fingerprint({'s': np.array(1)}) != state_fingerprint({'s': np.array([1])})
    try:
        state_fingerprint({'bad': np.array([object()], dtype=object)})
    except ValueError:
        pass
    else:
        raise AssertionError('object state accepted')


if __name__ == '__main__':
    check()
    print('TECHNICAL_CHECK_PASSED: exact bounded-memory fingerprint arithmetic only')
