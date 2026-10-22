"""Coordinate-free cycle consensus,not physical identity/visibility certification."""
import time

# ponytail: exact cliques for small graphs;stop at fixed caps instead of approximate identities.

def select_tracks(edges):
    """Unique-largest maximal-clique membership;no coordinate/error input."""
    start = time.monotonic()
    adjacency = {}
    for a, b in edges:
        if a[0] == b[0] or a == b:
            raise ValueError('same-frame observation edge')
        adjacency.setdefault(a, set()).add(b)
        adjacency.setdefault(b, set()).add(a)
    cliques, leaves = [], [0]

    def visit(chosen, possible, excluded):
        if time.monotonic()-start > 60 or leaves[0] >= 100000:
            raise RuntimeError('fixed maximal-clique capacity exceeded')
        if not possible and not excluded:
            leaves[0] += 1
            if len(chosen) >= 3:
                cliques.append(tuple(sorted(chosen)))
            return
        pivot = max(sorted(possible|excluded), key=lambda v:len(possible & adjacency[v]))
        for vertex in sorted(possible-adjacency[pivot]):
            visit(chosen+(vertex,), possible & adjacency[vertex], excluded & adjacency[vertex])
            possible.remove(vertex)
            excluded.add(vertex)

    visit((), set(adjacency), set())
    cliques.sort(key=lambda clique:(-len(clique), clique))
    best = {}
    for index, clique in enumerate(cliques):
        for vertex in clique:
            size, candidates = best.get(vertex, (0, set()))
            if len(clique) > size:
                best[vertex] = (len(clique), {index})
            elif len(clique) == size:
                candidates.add(index)
    selected, rows = [], []
    for index, clique in enumerate(cliques):
        accepted = all(best[v] == (len(clique), {index}) for v in clique)
        rows.append({'vertices':clique, 'selected':accepted})
        if accepted:
            selected.append(clique)
    flat = [v for clique in selected for v in clique]
    if len(flat) != len(set(flat)):
        raise AssertionError('selected track membership conflicts')
    return selected, {'raw_vertices':len(adjacency), 'raw_edges':len(edges), 'maximal_cliques':leaves[0],
                      'candidate_tracks':len(cliques), 'selected_tracks':len(selected),
                      'selected_observations':len(flat), 'candidates':rows, 'seconds':time.monotonic()-start}

