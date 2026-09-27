# -*- coding: utf-8 -*-
"""介護の各場面での声かけを足す。

出どころ：Google ドライブ ＞ 日本語の勉強 ＞ 05_介護の日本語・現場教材 ＞
「介護の各場面での声掛け例　日本語（よみ）英語　インドネシア語　読み（カタカナ）」
（このシステムの持ち主が作ったもの。2026-09-27 に取り込み）

日本語は「体（からだ）」の形で書いてあるので、**語と読みに分ける**。
インドネシア語のカタカナ読みは取り込まない（読むのは実習生なので要らない）。
"""
import json, io, re

# (日本語ふりがな付き, インドネシア語, 英語)
S = {
"食事のとき": [
("ごはんの時間（じかん）です。","Sekarang waktu makan.","It's meal time."),
("朝（あさ）ごはんですよ。","Sekarang waktu sarapan.","It's breakfast time."),
("お昼（ひる）ごはんですよ。","Sekarang waktu makan siang.","It's lunch time."),
("夕（ゆう）ごはんですよ。","Sekarang waktu makan malam.","It's dinner time."),
("いすに座（すわ）りましょう。","Mari duduk di kursi.","Let's sit on the chair."),
("テーブルに近（ちか）づきましょう。","Mari mendekat ke meja.","Let's move closer to the table."),
("体（からだ）を少（すこ）し前（まえ）に倒（たお）してください。","Tolong agak membungkuk ke depan.","Please lean your body a little forward."),
("顎（あご）を上（あ）げないでください。","Tolong jangan angkat dagu.","Please don't lift your chin."),
("一口（ひとくち）ずつ、ゆっくり食（た）べましょう。","Mari makan pelan-pelan, sedikit demi sedikit.","Let's eat slowly, one bite at a time."),
("よくかんでください。","Tolong kunyah dengan baik.","Please chew well."),
("のどは苦（くる）しくないですか。","Apakah tenggorokan Anda tidak sesak?","Does your throat feel okay?"),
("小（ちい）さく切（き）りますね。","Saya potong kecil-kecil, ya.","I'll cut it into small pieces."),
("飲（の）み物（もの）にとろみをつけますね。","Saya beri pengental pada minumannya, ya.","I'll thicken your drink."),
("次（つぎ）の一口（ひとくち）、いきますね。","Suapan berikutnya, ya.","Here comes the next bite."),
("休（やす）みながら食（た）べましょう。","Mari makan sambil istirahat.","Let's eat while taking breaks."),
("もう少（すこ）し食（た）べられますか。","Bisakah makan sedikit lagi?","Can you eat a little more?"),
("お水（みず）を少（すこ）し飲（の）みましょう。","Mari minum sedikit air.","Let's drink a little water."),
("むせたときは手（て）を上（あ）げてください。","Kalau tersedak, tolong angkat tangan.","If you choke, please raise your hand."),
("おいしいですか。","Enak, ya?","Does it taste good?"),
("熱（あつ）くないですか。","Tidak terlalu panas, kan?","Is it not too hot?"),
("スプーンで食（た）べましょう。","Mari makan dengan sendok.","Let's eat with a spoon."),
("自分（じぶん）で食（た）べられるところは、お願（ねが）いします。","Bagian yang bisa Bapak/Ibu makan sendiri, silakan.","Please eat what you can by yourself."),
("こぼれても大丈夫（だいじょうぶ）ですよ。","Tidak apa-apa kalau sedikit tumpah.","It's okay if you spill a little."),
],
"排泄のとき": [
("トイレに行（い）きましょう。","Mari ke toilet.","Let's go to the toilet."),
("オムツを替（か）えましょう。","Saya ganti popok, ya.","Let's change your diaper."),
("立（た）ち上（あ）がれますか。","Bisakah berdiri?","Can you stand up?"),
("ゆっくり立（た）ちましょう。","Mari berdiri pelan-pelan.","Let's stand up slowly."),
("手（て）すりにつかまってください。","Tolong pegang pegangan tangan.","Please hold the handrail."),
("ズボンを少（すこ）し下（さ）げますね。","Saya turunkan celana sedikit, ya.","I'll pull your pants down a little."),
("深（ふか）く腰（こし）をかけてください。","Tolong duduk sampai ke belakang.","Please sit back deeply."),
("いきまないでください。","Tolong jangan mengejan terlalu kuat.","Please don't strain."),
("終（お）わったら呼（よ）んでください。","Kalau sudah selesai, panggil saya, ya.","Please call me when you are finished."),
("きれいに拭（ふ）きますね。","Saya bersihkan dulu, ya.","I'll wipe you clean."),
("お尻（しり）を少（すこ）し上（あ）げてください。","Tolong angkat pantat sedikit.","Please lift your hips a little."),
("お腹（なか）は痛（いた）くないですか。","Apakah perut Anda sakit?","Does your stomach hurt?"),
("便（べん）は出（で）ましたか。","Apakah sudah buang air besar?","Did you have a bowel movement?"),
("おしっこは出（で）ましたか。","Apakah sudah buang air kecil?","Did you urinate?"),
("パッドを替（か）えますね。","Saya ganti pad, ya.","I'll change your pad."),
("においが強（つよ）いですね。気分（きぶん）はどうですか。","Baunya agak kuat. Bagaimana perasaan Anda?","The smell is strong. How do you feel?"),
("今日（きょう）は便（べん）が固（かた）いですね。","Hari ini fesesnya agak keras.","Your stool is hard today."),
("今日（きょう）は便（べん）がやわらかいですね。","Hari ini fesesnya agak lunak.","Your stool is soft today."),
("すぐに片（かた）づけますね。","Saya akan bereskan sekarang.","I'll clean it up right away."),
("お疲（つか）れさまでした。","Terima kasih, sudah selesai.","Thank you, good job."),
],
"移動のとき": [
("ベッドからいすに移（うつ）ります。","Kita pindah dari tempat tidur ke kursi.","We're moving from the bed to the chair."),
("ブレーキをかけますね。","Saya pasang rem dulu, ya.","I'll put the brakes on."),
("足（あし）をそろえてください。","Tolong rapatkan kaki.","Please put your feet together."),
("三（さん）つ数（かぞ）えて立（た）ちましょう。","Kita berdiri hitungan tiga, ya.","Let's stand up on the count of three."),
("「一、二、三（いち、に、さん）」で立（た）ちますよ。","Kita berdiri saat saya bilang “satu, dua, tiga”.","We'll stand on “one, two, three”."),
("私（わたし）が腰（こし）を支（ささ）えます。","Saya akan menyangga pinggang Anda.","I will support your waist."),
("いすの前（まえ）まで一緒（いっしょ）に歩（ある）きましょう。","Mari berjalan bersama ke kursi.","Let's walk together to the chair."),
("いすの前（まえ）で止（と）まりましょう。","Berhenti di depan kursi.","Let's stop in front of the chair."),
("ゆっくり座（すわ）りましょう。","Mari duduk pelan-pelan.","Let's sit down slowly."),
("いすの背（せ）にもたれてください。","Tolong bersandar di sandaran kursi.","Please lean back on the chair."),
("痛（いた）いところはありませんか。","Apakah ada bagian yang sakit?","Do you feel any pain?"),
("一人（ひとり）では動（うご）かないでください。","Tolong jangan bergerak sendiri.","Please don't move by yourself."),
("無理（むり）しないでください。","Tolong jangan memaksakan diri.","Please don't overdo it."),
("立（た）つときは、必（かなら）ず呼（よ）んでください。","Saat mau berdiri, tolong panggil saya.","Please always call me when you stand up."),
("足（あし）がふらつきますか。","Apakah kaki terasa goyah?","Do your legs feel unsteady?"),
("すべらないように気（き）をつけましょう。","Hati-hati agar tidak terpeleset.","Let's be careful not to slip."),
("もう少（すこ）し休（やす）みましょう。","Mari istirahat sedikit lagi.","Let's rest a little more."),
],
"口腔ケア": [
("歯（は）をみがきましょう。","Mari sikat gigi.","Let's brush your teeth."),
("入（い）れ歯（ば）を外（はず）しますね。","Saya lepaskan gigi palsu, ya.","I'll remove your dentures."),
("お口（くち）を少（すこ）し閉（と）じてください。","Tolong tutup mulut sedikit.","Please close your mouth a little."),
("痛（いた）いところはありますか。","Apakah ada bagian yang sakit?","Do you have any painful areas?"),
("ここは少（すこ）ししみます。","Di sini mungkin agak perih.","It may sting a little here."),
("上（うえ）の歯（は）をみがきます。","Saya sikat gigi bagian atas.","I'll brush your upper teeth."),
("下（した）の歯（は）をみがきます。","Saya sikat gigi bagian bawah.","I'll brush your lower teeth."),
("舌（した）を少（すこ）し出（だ）してください。","Tolong keluarkan lidah sedikit.","Please stick your tongue out a little."),
("舌（した）をやさしくみがきます。","Saya sikat lidah pelan-pelan.","I'll gently brush your tongue."),
("うがいをしましょう。","Mari kumur-kumur.","Let's rinse your mouth."),
("飲（の）み込（こ）まずに吐（は）き出（だ）してください。","Tolong keluarkan, jangan ditelan.","Please spit it out, don't swallow."),
("お水（みず）で口（くち）をゆすぎますね。","Saya bilas mulut dengan air, ya.","I'll rinse your mouth with water."),
("唇（くちびる）をふきますね。","Saya lap bibir, ya.","I'll wipe your lips."),
("きれいになりました。","Sekarang sudah bersih.","It's clean now."),
("すっきりしましたか。","Rasanya lebih segar?","Do you feel refreshed?"),
("入（い）れ歯（ば）を戻（もど）しますね。","Saya pasang kembali gigi palsu, ya.","I'll put your dentures back in."),
("毎日（まいにち）続（つづ）けましょう。","Mari kita lakukan setiap hari.","Let's continue this every day."),
("のどに違和感（いわかん）はありませんか。","Apakah ada rasa tidak enak di tenggorokan?","Do you feel anything strange in your throat?"),
],
"入浴のとき": [
("入浴（にゅうよく）の時間（じかん）です。","Sekarang waktu mandi.","It's bath time."),
("すべらないように気（き）をつけてください。","Hati-hati agar tidak terpeleset.","Please be careful not to slip."),
("いすに座（すわ）って服（ふく）を脱（ぬ）ぎましょう。","Mari duduk dan melepas baju.","Let's sit on the chair and take off your clothes."),
("お湯（ゆ）の温度（おんど）を確（たし）かめます。","Saya cek dulu suhu airnya.","I'll check the water temperature."),
("お湯（ゆ）は熱（あつ）くないです。","Airnya tidak terlalu panas.","The water is not too hot."),
("ゆっくり浴槽（よくそう）に入（はい）りましょう。","Mari masuk ke bak mandi pelan-pelan.","Let's slowly get into the tub."),
("体（からだ）を洗（あら）いますね。","Saya akan mencuci badan Anda.","I'll wash your body."),
("ご自分（じぶん）で洗（あら）えるところはお願（ねが）いします。","Bagian yang bisa, silakan cuci sendiri.","Please wash the parts you can by yourself."),
("背中（せなか）を洗（あら）いますね。","Saya cuci punggung Anda, ya.","I'll wash your back."),
("髪（かみ）を洗（あら）います。目（め）を閉（と）じてください。","Saya cuci rambut. Tolong tutup mata.","I'll wash your hair. Please close your eyes."),
("お湯（ゆ）をかけます。少（すこ）し冷（つめ）たいですよ。","Saya siram air. Agak sedikit dingin, ya.","I'll pour water on you. It's a little cool."),
("気分（きぶん）は悪（わる）くないですか。","Apakah Anda merasa baik-baik saja?","Do you feel okay?"),
("のぼせていませんか。","Apakah Anda merasa pusing karena panas?","Are you feeling faint from the heat?"),
("そろそろお湯（ゆ）から上（あ）がりましょう。","Mari kita keluar dari bak mandi.","Let's get out of the bath soon."),
("体（からだ）をタオルでふきますね。","Saya keringkan badan dengan handuk.","I'll dry your body with a towel."),
("さっぱりしましたね。","Sekarang rasanya segar, ya.","You must feel refreshed."),
],
"着替えのとき": [
("着替（きが）えの時間（じかん）です。","Sekarang saatnya ganti baju.","It's time to change clothes."),
("上（うえ）の服（ふく）を脱（ぬ）ぎましょう。","Mari lepas baju bagian atas.","Let's take off your top."),
("ボタンを外（はず）しますね。","Saya buka kancingnya, ya.","I'll unbutton your shirt."),
("腕（うで）を上（あ）げてください。","Tolong angkat lengan.","Please raise your arms."),
("片方（かたほう）ずつ袖（そで）を通（とお）しますね。","Saya masukkan lengan satu per satu.","I'll put your arms through the sleeves one by one."),
("次（つぎ）はズボンを脱（ぬ）ぎますね。","Berikutnya kita lepas celana, ya.","Next, we'll take off your pants."),
("少（すこ）しお尻（しり）を上（あ）げてください。","Tolong angkat pantat sedikit.","Please lift your hips a little."),
("靴下（くつした）を脱（ぬ）ぎますね。","Saya lepas kaus kaki, ya.","I'll take off your socks."),
("新（あたら）しい服（ふく）を着（き）ましょう。","Mari pakai baju yang bersih.","Let's put on clean clothes."),
("頭（あたま）から服（ふく）をかぶります。","Baju akan saya lewatkan dari atas kepala.","I'll put the shirt over your head."),
("腕（うで）を前（まえ）に出（だ）してください。","Tolong julurkan lengan ke depan.","Please put your arms forward."),
("ボタンを留（と）めますね。","Saya pasang kancingnya, ya.","I'll button it up."),
("ズボンを上（あ）げますね。","Saya naikkan celananya, ya.","I'll pull up your pants."),
("ウエストのゴムを整（ととの）えます。","Saya rapikan karet pinggangnya.","I'll adjust the waistband."),
("靴下（くつした）をはきましょう。","Mari pakai kaus kaki.","Let's put on your socks."),
("衣服（いふく）はきつくないですか。","Apakah bajunya tidak terlalu sempit?","Are the clothes too tight?"),
("寒（さむ）くないですか。","Apakah Anda tidak kedinginan?","Are you warm enough?"),
("これで着替（きが）えは終（お）わりです。","Selesai ganti baju.","We're done changing clothes."),
("とてもお似合（にあ）いですよ。","Sangat cocok untuk Anda.","It looks very good on you."),
],
"バイタル測定": [
("これからバイタルを測（はか）ります。","Sekarang saya periksa tanda vital, ya.","I'm going to check your vital signs."),
("体温（たいおん）を測（はか）ります。","Saya ukur suhu tubuh.","I'll take your temperature."),
("体温計（たいおんけい）をわきにはさみます。","Saya taruh termometer di ketiak.","I'll put the thermometer under your arm."),
("「ピッ」と鳴（な）るまで、そのままでいてください。","Tolong diam sampai berbunyi “piip”.","Please stay still until it beeps."),
("血圧（けつあつ）を測（はか）ります。","Saya ukur tekanan darah.","I'll measure your blood pressure."),
("腕（うで）にカフを巻（ま）きますね。","Saya pasang manset di lengan, ya.","I'll wrap the cuff around your arm."),
("少（すこ）し締（し）めつけられますが、すぐ終（お）わります。","Akan terasa sedikit kencang, tapi sebentar saja.","It will feel tight for a moment, but it will be quick."),
("動（うご）かないでいてください。","Tolong jangan bergerak.","Please don't move."),
("脈拍（みゃくはく）を測（はか）ります。","Saya periksa denyut nadi.","I'll check your pulse."),
("手首（てくび）をかりますね。","Saya pegang pergelangan tangan Anda.","I'll hold your wrist."),
("血中（けっちゅう）酸素（さんそ）の量（りょう）を測（はか）ります。","Saya ukur kadar oksigen dalam darah.","I'll measure your blood oxygen level."),
("指（ゆび）に機械（きかい）をつけますね。","Saya pasang alat ini di jari, ya.","I'll put this device on your finger."),
("少（すこ）し冷（つめ）たく感（かん）じるかもしれません。","Mungkin terasa sedikit dingin.","It may feel a little cold."),
("体調（たいちょう）はどうですか。","Bagaimana kondisi tubuh Anda?","How are you feeling?"),
("息（いき）は苦（くる）しくないですか。","Apakah Anda sesak napas?","Do you have any trouble breathing?"),
("頭（あたま）は痛（いた）くないですか。","Apakah kepala Anda sakit?","Do you have a headache?"),
("今日（きょう）の血圧（けつあつ）は少（すこ）し高（たか）めです。","Tekanan darah hari ini agak tinggi.","Your blood pressure is a bit high today."),
("看護師（かんごし）に報告（ほうこく）しますね。","Saya laporkan ke perawat, ya.","I'll report this to the nurse."),
("少（すこ）し休（やす）みましょう。","Mari istirahat sebentar.","Let's rest a little."),
("測定（そくてい）は終（お）わりです。","Pemeriksaan selesai.","We're done with the measurements."),
],
}

KANA = re.compile(r'[぀-ゟ゠-ヿ]')
def split_ruby(t):
    """「体（からだ）を…」→（語, 読み）。かっこの前の漢字の並びが、その読み。"""
    word, read, i = '', '', 0
    while i < len(t):
        m = re.match(r'([一-鿿々]+)（([぀-ゟ]+)）', t[i:])
        if m:
            word += m.group(1); read += m.group(2); i += m.end()
        else:
            word += t[i]; read += t[i]; i += 1
    return word, read

P='vocab-data.json'; d=json.load(io.open(P,encoding='utf-8')); vw=d['words']
have={w['word'] for w in vw}
kd={x['character'] for x in json.load(io.open('kanji-data.json',encoding='utf-8'))['kanji']}
isK=lambda c:'一'<=c<='鿿'

add=[]; dup=[]; nok={}
for sub, items in S.items():
    for ja, idn, en in items:
        w, r = split_ruby(ja)
        w = w.rstrip('。'); r = r.rstrip('。')
        if w in have: dup.append(w); continue
        ks=[c for c in w if isK(c)]
        miss=[c for c in ks if c not in kd]
        if miss: nok[w]=miss; continue
        add.append({"word":w,"reading":r,"meaning":en,"level":"介護","category":"声かけ",
                    "kanji":ks,"meaning_id":idn,"sub":sub,"care":True})
        have.add(w)

print('足す %d件 ／ すでにある %d件' % (len(add), len(dup)))
if dup: print('  すでにある:', '　'.join(dup))
if nok: print('  漢字が足りない:', nok)
print('\n読みの取り出しの確かめ（10件）:')
for e in add[:10]: print('   %-34s %s' % (e['word'], e['reading']))
vw.extend(add); d['count']=len(vw)
json.dump(d,io.open(P,'w',encoding='utf-8'),ensure_ascii=False)
print('\n語彙 %d語' % len(vw))
