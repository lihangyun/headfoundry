"""Sparse graphical target data parser, independent of MakeHuman application code."""
import numpy as np


def parse_target(text, vertex_count):
    """Return displacements in source coordinates; unspecified vertices stay zero.

    Caller must verify asset rights, digest and matching base topology first.
    """
    if not isinstance(vertex_count,int) or isinstance(vertex_count,bool) or vertex_count<=0:
        raise ValueError('positive base vertex count required')
    delta=np.zeros((vertex_count,3));seen=set()
    for line in text.splitlines():
        fields=line.split('#',1)[0].split()
        if not fields:continue
        if len(fields)!=4:raise ValueError('target row must contain index and three offsets')
        index=int(fields[0]);offset=np.array(fields[1:],float)
        if index<0 or index>=vertex_count or index in seen or not np.isfinite(offset).all():
            raise ValueError('invalid or duplicate target vertex')
        delta[index]=offset;seen.add(index)
    if not seen:raise ValueError('empty target')
    return delta
