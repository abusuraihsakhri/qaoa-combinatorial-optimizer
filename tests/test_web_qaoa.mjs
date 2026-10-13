import test from 'node:test';
import assert from 'node:assert/strict';
import {parseEdges, costsFor, probabilities, optimize} from '../web/qaoa.mjs';
const triangle = [[0,1,1],[1,2,1],[0,2,1]];
test('edge parsing validates duplicate, nonfinite, and invalid endpoints', () => {
  assert.deepEqual(parseEdges('0,1,1\n1,2,1\n0,2,1',3),triangle);
  for (const text of ['0,0,1','0,1,0','0,3,1','0,1,NaN','0,1,1\n1,0,1']) {
    assert.throws(() => parseEdges(text,3));
  }
});
test('triangle costs, norm and expectation', () => {
  const costs = costsFor(3, triangle);
  assert.deepEqual(costs,[0,2,2,2,2,2,2,0]);
  const p = probabilities(costs,[0],[0]);
  assert.ok(p.every(v => Math.abs(v-1/8)<1e-12));
  const result = optimize(3,triangle,1,8);
  assert.equal(result.exact_optimum, 2);
  assert.ok(Math.abs(result.distribution.reduce((a,b)=>a+b.probability,0)-1)<1e-10);
  assert.ok(result.expected_cut <= 2+1e-9);
  assert.ok(result.expected_cut >= 1);
});
test('two layers with weighted square', () => {
  const edges = [[0,1,1],[1,2,2],[2,3,1],[3,0,2]];
  const one = optimize(4,edges,1,8), two = optimize(4,edges,2,8);
  assert.equal(two.exact_optimum,6);
  assert.ok(two.expected_cut >= one.expected_cut - 1e-9);
});
