/* 診断テストの共通ヘルパー */
const Q = (id, text, opts, ans, why) => ({ id, text, opts, ans, why });
const SORT = (id, parts, order, star, why) =>
  ({ id, kind: 'sort', parts, order, star, ans: order[star - 1], why });
const L = (sp, v) => ({ k: 'line', sp, v });
const N = v => ({ k: 'q', v });
const P = (s, a) => (a ? { k: 'pause', s, a: true } : { k: 'pause', s });
module.exports = { Q, SORT, L, N, P };
