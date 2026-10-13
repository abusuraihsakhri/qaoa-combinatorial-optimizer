/** Deterministic, dependency-free state-vector QAOA for positive-weight Max-Cut. */
export const MAX_VERTICES = 9;

export function parseEdges(text, vertices) {
  if (!Number.isInteger(vertices) || vertices < 2 || vertices > MAX_VERTICES) {
    throw new Error('Vertex count must be 2–' + MAX_VERTICES + '.');
  }
  const lines = text.trim().split(/\r?\n/).map(s => s.trim()).filter(s => s && !s.startsWith('#'));
  if (!lines.length || lines.length > MAX_VERTICES * (MAX_VERTICES - 1) / 2) {
    throw new Error('Provide 1 or more edges, one per line.');
  }
  const seen = new Set();
  return lines.map((line, index) => {
    const tokens = line.split(/[\s,]+/);
    if (tokens.length !== 3 || tokens.some(s => s === '' || !Number.isFinite(Number(s)))) {
      throw new Error('Line ' + (index + 1) + ': expected u, v, weight.');
    }
    const [u, v, weight] = tokens.map(Number);
    if (![u, v].every(Number.isInteger) || u < 0 || v < 0 || u >= vertices || v >= vertices || u === v) {
      throw new Error('Line ' + (index + 1) + ': invalid vertex indices.');
    }
    if (weight <= 0) throw new Error('Line ' + (index + 1) + ': weight must be positive.');
    const key = Math.min(u,v) + ',' + Math.max(u,v);
    if (seen.has(key)) throw new Error('Line ' + (index + 1) + ': duplicate edge.');
    seen.add(key);
    return [Math.min(u,v), Math.max(u,v), weight];
  });
}

export function costsFor(vertices, edges) {
  return Array.from({length: 1 << vertices}, (_, mask) =>
    edges.reduce((sum, [u,v,w]) => sum + ((((mask >> u) ^ (mask >> v)) & 1) ? w : 0), 0));
}

export function probabilities(costs, gammas, betas) {
  const count = costs.length;
  if (count < 4 || (count & (count - 1)) || gammas.length !== betas.length ||
      gammas.length < 1 || gammas.length > 3 ||
      ![...gammas, ...betas].every(Number.isFinite)) {
    throw new Error('Invalid QAOA state or angles.');
  }
  let re = new Float64Array(count).fill(1 / Math.sqrt(count));
  let im = new Float64Array(count);
  for (let layer = 0; layer < gammas.length; layer++) {
    for (let i = 0; i < count; i++) {
      const a = gammas[layer] * costs[i], c = Math.cos(a), s = Math.sin(a);
      const r = re[i], j = im[i];
      re[i] = c * r + s * j;
      im[i] = c * j - s * r;
    }
    const c = Math.cos(betas[layer]), s = Math.sin(betas[layer]);
    for (let bit = 1; bit < count; bit <<= 1) {
      for (let base = 0; base < count; base += 2 * bit) {
        for (let a = base; a < base + bit; a++) {
          const b = a + bit;
          const r0 = re[a], j0 = im[a], r1 = re[b], j1 = im[b];
          re[a] = c * r0 + s * j1;
          im[a] = c * j0 - s * r1;
          re[b] = c * r1 + s * j0;
          im[b] = c * j1 - s * r0;
        }
      }
    }
  }
  return Array.from(re, (r,i) => r*r + im[i]*im[i]);
}

export function optimize(vertices, edges, layers=1, grid=10) {
  if (!Number.isInteger(layers) || layers < 1 || layers > 3 ||
      !Number.isInteger(grid) || grid < 4 || grid > 24) throw new Error('Invalid layers or grid.');
  const parsed = parseEdges(edges.map(e => e.join(',')).join('\n'), vertices);
  const costs = costsFor(vertices, parsed);
  const expectation = (gs, bs) => probabilities(costs, gs, bs).reduce((sum,p,i) => sum + p*costs[i],0);
  let score = -Infinity, gammas = [0], betas = [0];
  for (let gi=0; gi<grid; gi++) for (let bi=0; bi<grid; bi++) {
    const g = 2*Math.PI*gi/grid, b = Math.PI*bi/(2*grid);
    const value = expectation([g], [b]);
    if (value > score) { score = value; gammas = [g]; betas = [b]; }
  }
  gammas.push(...Array(layers-1).fill(0));
  betas.push(...Array(layers-1).fill(0));
  let dg = 2*Math.PI/grid, db = Math.PI/(2*grid);
  for (let k=0; k<10; k++) {
    for (const [params, delta, period] of [[gammas,dg,2*Math.PI], [betas,db,Math.PI]]) {
      for (let layer=0; layer<layers; layer++) {
        let original = params[layer];
        for (const step of [-delta, delta]) {
          params[layer] = (original + step + period) % period;
          const candidate = expectation(gammas, betas);
          if (candidate > score + 1e-12) { score = candidate; original = params[layer]; }
        }
        params[layer] = original;
      }
    }
    dg /= 2; db /= 2;
  }
  const probs = probabilities(costs, gammas, betas);
  const likely = probs.indexOf(Math.max(...probs));
  const exactOptimum = Math.max(...costs);
  const bits = i => Array.from({length:vertices}, (_,j) => (i >> j) & 1).join('');
  return {
    vertices, edges: parsed, layers, gammas, betas,
    expected_cut: score, exact_optimum: exactOptimum,
    approximation_ratio: exactOptimum ? score / exactOptimum : 1,
    most_likely_bitstring: bits(likely), most_likely_cut: costs[likely],
    most_likely_probability: probs[likely],
    optimal_bitstrings: costs.flatMap((v,i) => Math.abs(v-exactOptimum)<1e-9 ? [bits(i)] : []),
    distribution: probs.map((p,i) => ({bitstring:bits(i), probability:p, cut:costs[i]})),
    simulator: 'classical state-vector QAOA'
  };
}
