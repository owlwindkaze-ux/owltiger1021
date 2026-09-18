const fs = require('fs');
const R = '/home/user/owltiger1021/';
const P = JSON.parse(fs.readFileSync('/tmp/hani/plan.json','utf8'));
const gN4 = JSON.parse(fs.readFileSync(R+'bunpo/grammar-n4.json','utf8')).grammar;
const gN3 = JSON.parse(fs.readFileSync(R+'bunpo/grammar-n3.json','utf8')).grammar;
const rN4 = JSON.parse(fs.readFileSync(R+'dokkai/reading-n4.json','utf8')).passages;
const rN3 = JSON.parse(fs.readFileSync(R+'dokkai/reading-n3.json','utf8')).passages;
/* ふりがなの《》は、テストでは残す（アプリと同じ書き方） */
function readPassage(p){
  return { title:p.title, intro:p.intro, text:p.text,
    items:(p.questions||[]).map(q => ({ q:q.q, s:'', opts:q.choices.slice(),
      ans:q.answer+1, why:q.explain })) };
}

/* 種を固定した乱数（毎回同じ問題になる） */
let seed = 20261207;
const rnd = () => (seed = (seed*1664525 + 1013904223) >>> 0) / 4294967296;
const pick = (arr, n) => { const a = arr.slice(); const o = [];
  while (o.length < n && a.length) o.push(a.splice(Math.floor(rnd()*a.length), 1)[0]);
  return o; };
const shuffle = a => { const b = a.slice();
  for (let i=b.length-1;i>0;i--){ const j=Math.floor(rnd()*(i+1)); [b[i],b[j]]=[b[j],b[i]]; }
  return b; };

const weeks = (a,b) => { const o=[]; for(let w=a;w<=b;w++) o.push(w); return o; };
const kanjiIn = (a,b) => weeks(a,b).flatMap(w => P.kanjiPlan[w]||[]);
const vocabIn = (a,b) => weeks(a,b).flatMap(w => P.vocabPlan[w]||[]);
const gramIn  = (a,b) => weeks(a,b).flatMap(w => P.gramPlan[w]||[]);

/* ---- 語彙：読みを4択で ---- */
function readingQs(pool, n){
  const src = pool.filter(v => /[一-鿿]/.test(v.word) && v.reading && v.reading.length >= 2
    && !/[;；,、]/.test(v.reading) && !/[;；]/.test(v.word));
  return pick(src, n).map(v => {
    /* 誤答は、正解と長さが近い読みから選ぶ。長さでバレると問題にならない */
    const cand = src.filter(x => x.word !== v.word && x.reading !== v.reading)
      .sort((a,b) => Math.abs(a.reading.length - v.reading.length)
                   - Math.abs(b.reading.length - v.reading.length));
    const others = pick(cand.slice(0, 40), 3);
    const opts = shuffle([v.reading, ...others.map(x => x.reading)]);
    return { q: '', s: v.word,
      opts, ans: opts.indexOf(v.reading)+1, why: v.word + '＝' + v.reading };
  });
}
/* ---- 語彙：意味を4択で ---- */
function meaningQs(pool, n, exclude){
  const used = new Set(exclude.map(x => x.s));
  /* 意味はインドネシア語で出す。読むのは実習生なので、英語では確かめられない */
  const mn = v => v.meaning_id || v.meaning;
  const src = pool.filter(v => mn(v) && mn(v).length >= 2 && !used.has(v.word)
    && !/[;；]/.test(v.word) && !/[;；]/.test(mn(v)));   /* 意味がひとつに決まる語だけ */
  return pick(src, n).map(v => {
    const cand = src.filter(x => x.word !== v.word && mn(x) !== mn(v))
      .sort((a,b) => Math.abs(mn(a).length - mn(v).length) - Math.abs(mn(b).length - mn(v).length));
    const others = pick(cand.slice(0, 40), 3);
    const opts = shuffle([mn(v), ...others.map(mn)]);
    return { q: '', s: v.word,
      opts, ans: opts.indexOf(mn(v))+1, why: v.word + '（' + v.reading + '）＝' + mn(v) };
  });
}
/* ---- 文型：既存の練習問題から ---- */
function gramQs(pool, n){
  const src = [];
  pool.forEach(g => (g.quiz||[]).forEach(q => {
    if (q.type === 'choice' && q.choices && q.choices.length === 4) src.push({ g, q });
  }));
  return pick(src, n).map(x => {
    const right = x.q.choices[x.q.answer];
    const opts = shuffle(x.q.choices.slice());
    return { q: '', s: x.q.q.replace(/＿+/g, '（　　）'),
      opts, ans: opts.indexOf(right)+1, why: x.g.pattern + '　' + (x.q.explain_id||'') };
  });
}

/* ---- 聴解（新規に書き下ろし・7問） ---- */
const L = (sp,v) => ({k:'line',sp,v}), N = v => ({k:'q',v}), PA = (s,a)=> a?{k:'pause',s,a:true}:{k:'pause',s};
const LISTEN = {
  1: [
    { no:'問19', ans:2, opts:['9時','9時半','10時','10時半'],
      answer:'2　9時半', why:'「30分前に」と言われている。',
      steps:[N('女の人は、何時に 来ますか。'),PA(2),
        L('男','あしたの 会議は 10時からです。'),
        L('女','はい。'),
        L('男','準備が あるので、30分前に 来て ください。'),
        L('女','わかりました。'),PA(6,true)]},
    { no:'問20', ans:3, opts:['水を持って行く','窓を閉める','タオルを持って行く','電気を消す'],
      answer:'3　タオルを持って行く', why:'水は「もうある」と言われている。',
      steps:[N('男の人は、何を 持って 行きますか。'),PA(2),
        L('女','お風呂の 用意、お願いします。水と タオルを。'),
        L('男','水は もう 置いて ありますよ。'),
        L('女','あ、そうでしたね。じゃあ タオルだけ。'),
        L('男','はい。'),PA(6,true)]}
  ],
  4: [
    { no:'問16', ans:1, opts:['書類をコピーする','会議室へ行く','部長に電話する','記録を書く'],
      answer:'1　書類をコピーする', why:'「先にコピーを」と決まる。',
      steps:[N('女の人は、このあと まず 何を しますか。'),PA(2),
        L('男','会議室に 行く 前に、この 書類を 人数分 お願いします。'),
        L('女','コピーですね。何部でしょうか。'),
        L('男','8部です。そのあとで 会議室へ。'),
        L('女','はい。'),PA(6,true)]},
    { no:'問17', ans:4, opts:['あしたの朝','あしたの昼','あさっての朝','あさっての昼'],
      answer:'4　あさっての昼', why:'「あしたは無理」→「あさっての午後」。',
      steps:[N('面会は いつに なりましたか。'),PA(2),
        L('女','ご家族の 面会、あしたの 朝は いかがですか。'),
        L('男','あしたは 検査が あって 無理なんです。'),
        L('女','では、あさっては。'),
        L('男','あさっての 午後なら 大丈夫です。'),PA(6,true)]},
    { no:'問18', ans:2, opts:['熱があるから','足が痛いから','ねむいから','おなかがすいたから'],
      answer:'2　足が痛いから', why:'「熱はない」と否定される。',
      steps:[N('この人が 歩かない 理由は 何ですか。'),PA(3),
        L('男','今日は 歩きたくないと おっしゃって います。熱でしょうか。'),
        L('女','熱は ありません。36度2分です。'),
        L('男','では どうして。'),
        L('女','右の 足が 痛いそうです。'),PA(6,true)]},
    { no:'問19', ans:1, opts:['はい、承知しました','はい、お願いしました','いいえ、今日です','いいえ、まだです'],
      answer:'1　はい、承知しました', why:'指示を受けたときの返事。',
      steps:[L('男','この 記録、今日中に お願いします。'),
        L('女','1、はい、承知しました。'),
        L('女','2、はい、お願いしました。'),
        L('女','3、いいえ、今日です。'),PA(6,true)]},
    { no:'問20', ans:3, opts:['はい、書きました','いいえ、書きます','いいえ、まだです','はい、これからです'],
      answer:'3　いいえ、まだです', why:'「もう〜ましたか」に、していないと答える。',
      steps:[L('女','報告書は もう 出しましたか。'),
        L('男','1、はい、書きました。'),
        L('男','2、いいえ、書きます。'),
        L('男','3、いいえ、まだです。'),PA(6,true)]}
  ]
};

/* ---- 4回分を組み立てる ---- */
const TESTS = [
  { no:1, week:4,  range:'第1〜4週（N5の漢字102字・語彙200語）',
    build(){
      const v = vocabIn(1,4);
      const a = readingQs(v, 8), b = meaningQs(v, 10, a);
      return { parts:[
        { head:'A　つぎの ことばは ひらがなで どう 書きますか。（8問）', items:a },
        { head:'B　つぎの ことばの 意味は どれですか。（10問）', items:b },
        { head:'C　聴解（2問）　音を 聞いて 答えます', listen:true, items:LISTEN[1].map(x=>({
            q:'', s:'', opts:x.opts, ans:x.ans, why:x.why })) }
      ], listen: LISTEN[1] };
    }},
  { no:2, week:8,  range:'第5〜8週（N4の漢字72字・語彙332語・文型60項目）',
    build(){
      const v = vocabIn(5,8), g = gramIn(5,8);
      const a = readingQs(v,5), b = meaningQs(v,7,a), c = gramQs(g,6);
      return { parts:[
        { head:'A　つぎの ことばは ひらがなで どう 書きますか。（5問）', items:a },
        { head:'B　つぎの ことばの 意味は どれですか。（7問）', items:b },
        { head:'C　（　　）に 何を 入れますか。（6問）', items:c },
        Object.assign({ head:'D　読解（2問）' }, { reading: readPassage(rN4[16]) })
      ] };
    }},
  { no:3, week:12, range:'第9〜12週（N4の漢字72字・語彙330語・文型57項目）',
    build(){
      const v = vocabIn(9,12), g = gramIn(9,12);
      const a = readingQs(v,5), b = meaningQs(v,7,a), c = gramQs(g,6);
      return { parts:[
        { head:'A　つぎの ことばは ひらがなで どう 書きますか。（5問）', items:a },
        { head:'B　つぎの ことばの 意味は どれですか。（7問）', items:b },
        { head:'C　（　　）に 何を 入れますか。（6問）', items:c },
        Object.assign({ head:'D　読解（2問）' }, { reading: readPassage(rN4[17]) })
      ] };
    }},
  { no:4, week:20, range:null,
    build(){
      const v = vocabIn(13,20), g = gramIn(13,20), k = kanjiIn(13,20);
      this.range = '第13〜20週（N3の漢字'+k.length+'字・語彙'+v.length+'語・文型'+g.length+
        '項目／100日コース第1〜4週）';
      const a = readingQs(v,4), b = meaningQs(v,3,a), c = gramQs(g,4);
      return { parts:[
        { head:'A　つぎの ことばは ひらがなで どう 書きますか。（4問）', items:a },
        { head:'B　つぎの ことばの 意味は どれですか。（3問）', items:b },
        { head:'C　（　　）に 何を 入れますか。（4問）', items:c },
        { head:'D　聴解（5問）　音を 聞いて 答えます', listen:true, items:LISTEN[4].map(x=>({
            q:'', s:'', opts:x.opts, ans:x.ans, why:x.why })) },
        Object.assign({ head:'E　読解（4問）' }, { reading: readPassage(rN3[10]) })
      ], listen: LISTEN[4] };
    }}
];

const out = TESTS.map(t => { const built = t.build(); return { no:t.no, week:t.week, range:t.range, ...built }; });

/* 正解の位置をならす（①に偏らないように、種を固定して並べ替える） */
out.forEach(t => {
  t.parts.forEach(p => { if (p.reading) p.items = p.reading.items; });
  const all = [];
  t.parts.forEach(p => (p.items||[]).forEach(q => all.push(q)));
  all.forEach((q, i) => {
    const want = (i + t.no) % q.opts.length;      /* 順ぐりに散らす */
    const right = q.opts[q.ans-1];
    const rest = q.opts.filter((_,j) => j !== q.ans-1);
    const opts = [];
    let r = 0;
    for (let k = 0; k < q.opts.length; k++) opts.push(k === want ? right : rest[r++]);
    q.opts = opts; q.ans = want + 1;
  });
});

/* ---- 点検 ---- */
let bad = [];
out.forEach(t => {
  let n = 0;
  t.parts.forEach(p => { if (p.reading) p.items = p.reading.items; });
  t.parts.forEach(p => (p.items||[]).forEach(q => {
    n++;
    if (!(q.ans >= 1 && q.ans <= q.opts.length)) bad.push('第'+t.no+'回 正解が範囲外');
    const s = q.opts.map(x => String(x).trim());
    if (new Set(s).size !== s.length) bad.push('第'+t.no+'回 '+(q.s||'')+' 選択肢が重複：'+s.join('/'));
  }));
  const dist = {};
  t.parts.forEach(p => (p.items||[]).forEach(q => dist[q.ans] = (dist[q.ans]||0)+1));
  console.log('第'+t.no+'回　'+n+'問　正解の散らばり', JSON.stringify(dist), '　範囲:', t.range);
});
console.log('不備:', bad.length ? bad : 'なし');
fs.writeFileSync('/tmp/hani/tests.json', JSON.stringify(out));
