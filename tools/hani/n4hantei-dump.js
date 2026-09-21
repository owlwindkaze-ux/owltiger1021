/* 点検用に、問題データを JSON で 出す */
const D = require(__dirname + '/n4hantei-data.js');
process.stdout.write(JSON.stringify(D, null, 1));
