#!/usr/bin/env python3
"""日本公式YouTubeの新着を取得。主対象が明確なタイトルだけ自動登録する。"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, re, time, urllib.request, xml.etree.ElementTree as ET

CHANNEL = "UCvoQlzEzqa6vQA8hq9GNNug"
CHANNEL_URL = "https://www.youtube.com/@ArknightsStaff_JP"
FEED = "https://www.youtube.com/feeds/videos.xml?channel_id=" + CHANNEL
NAMES_URL = "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData_YoStar/main/ja_JP/gamedata/excel/character_table.json"
SEED_NAMES = {'Lancet-2': 'char_285_medic2', 'Castle-3': 'char_286_cast3', 'THRM-EX': 'char_376_therex', 'ジャスティスナイト': 'char_4000_jnight', 'テラ大陸調査団': 'char_4077_palico', 'U-Official': 'char_4091_ulika', 'Friston-3': 'char_4093_frston', 'PhonoR-0': 'char_4136_phonor', 'CONFESS-47': 'char_4188_confes', 'ヤトウ': 'char_502_nblade', 'ノイルホーン': 'char_500_noirc', 'レンジャー': 'char_503_rang', 'ドゥリン': 'char_501_durin', '12F': 'char_009_12fce', 'フェン': 'char_123_fang', 'バニラ': 'char_240_wyvern', '予備隊員-近距離': 'char_504_rguard', 'プリュム': 'char_192_falco', 'メランサ': 'char_208_melan', 'ポプカル': 'char_281_popka', 'カーディ': 'char_209_ardign', 'ビーグル': 'char_122_beagle', '予備隊員-重装': 'char_602_cdfend', 'スポット': 'char_284_spot', 'クルース': 'char_124_kroos', 'アドナキエル': 'char_211_adnach', '予備隊員-狙撃': 'char_603_csnipe', 'ラヴァ': 'char_121_lava', 'ハイビスカス': 'char_120_hibisc', 'アンセル': 'char_212_ansel', '予備隊員-支援': 'char_506_rmedic', 'スチュワード': 'char_210_stward', '予備隊員-術師': 'char_604_ccast', 'オーキッド': 'char_278_orchid', 'ヘイズ': 'char_141_nights', 'ギターノ': 'char_109_fmout', 'グレイ': 'char_253_greyy', 'アコルト': 'char_4051_akkord', 'カシャ': 'char_328_cammou', 'インディゴ': 'char_469_indigo', 'プリン': 'char_4004_pudd', 'ジェシカ': 'char_235_jesica', 'メテオ': 'char_126_shotst', 'ヴァーミル': 'char_190_clour', 'メイ': 'char_133_mm', 'シラユキ': 'char_118_yuki', 'パインコーン': 'char_440_pinecn', 'アンブリエル': 'char_302_glaze', 'アシッドドロップ': 'char_366_acdrop', 'トター': 'char_4062_totter', 'ケイパー': 'char_4100_caper', 'クーリエ': 'char_198_blackd', 'スカベンジャー': 'char_149_scave', '予備隊員-先鋒': 'char_600_cpione', 'ヴィグナ': 'char_290_vigna', 'テンニンカ': 'char_151_myrtle', 'ビーンストーク': 'char_452_bstalk', 'スネグーラチカ': 'char_4208_wintim', 'ドーベルマン': 'char_130_doberm', 'マトイマル': 'char_289_gyuki', 'コンビクション': 'char_159_peacok', '予備隊員-前衛': 'char_601_cguard', 'フロストリーフ': 'char_193_frostl', 'エステル': 'char_127_estell', 'ムース': 'char_185_frncat', 'カッター': 'char_301_cutter', 'ウタゲ': 'char_337_utage', 'アレーン': 'char_271_spikes', '羅小黒': 'char_4067_lolxh', 'クォーツ': 'char_4063_quartz', 'ヒューマス': 'char_491_humus', 'ウィンドスクート': 'char_445_wscoot', 'グラベル': 'char_237_gravel', '予備隊員-特殊': 'char_607_cspec', 'ジェイ': 'char_272_strong', 'ロープ': 'char_236_rope', 'ミルラ': 'char_117_myrrh', 'ガヴィル': 'char_187_ccheal', 'ススーロ': 'char_298_susuro', '予備隊員-医療': 'char_605_cmedic', 'パフューマー': 'char_181_flower', 'セイリュウ': 'char_385_finlpp', 'チェストナット': 'char_4041_chnut', 'マッターホルン': 'char_199_yak', 'クオーラ': 'char_150_snakek', 'バブル': 'char_381_bubble', 'ルトナダ': 'char_4130_luton', 'グム': 'char_196_sunbr', 'ジュナー': 'char_260_durnar', 'ディピカ': 'char_110_deepcl', 'アーススピリット': 'char_183_skgoat', 'ポデンコ': 'char_258_podego', '予備隊員-補助': 'char_606_csuppo', 'ロベルタ': 'char_484_robrta', '盟約・補助オペレーター': 'char_616_pithst', 'イーサン': 'char_355_ethan', 'ショウ': 'char_277_sqrrel', 'ヴァーダント': 'char_4107_vrdant', 'コントレイル': 'char_4165_ctrail', 'フィリオプシス': 'char_128_plosis', 'ブリーズ': 'char_275_breeze', 'ローズソルト': 'char_4163_rosesa', 'ズィマー': 'char_115_headbr', 'テキサス': 'char_102_texas', 'キアーベ': 'char_349_chiave', 'ポンシラス': 'char_488_buildr', 'チューリップ': 'char_608_acpion', 'ケストレル': 'char_4023_rfalcn', 'マツキリ': 'char_4199_makiri', 'リード': 'char_261_sddrag', 'ワイルドメイン': 'char_496_wildmn', '歴陣鋭槍フェン': 'char_1036_fang2', 'エリジウム': 'char_401_elysm', 'ワンチィン': 'char_4119_wanqin', 'ブラックナイト': 'char_476_blkngt', 'ミトム': 'char_4147_mitm', 'カンタービレ': 'char_497_ctable', 'パズル': 'char_4017_puzzle', 'チルチャック': 'char_4144_chilc', 'サーファー': 'char_4052_surfer', 'スワイヤー': 'char_308_swire', 'ウィスラッシュ': 'char_265_sophia', 'ブライオファイタ': 'char_4106_bryota', 'Doc': 'char_4125_rdoc', 'フランカ': 'char_106_franka', 'エンカク': 'char_131_flameb', 'モーガン': 'char_154_morgan', 'Sharp': 'char_609_acguad', 'ライオス': 'char_4142_laios', 'インドラ': 'char_155_tiger', 'フリント': 'char_415_flint', 'ダグザ': 'char_157_dagda', 'ラップランド': 'char_140_whitew', 'エアースカーペ': 'char_294_ayer', 'リェータ': 'char_194_leto', 'ウィンドチャイム': 'char_4083_chimes', 'バイビーク': 'char_252_bibeak', 'Tachanka': 'char_459_tachak', 'スペクター': 'char_143_ghost', 'ブローカ': 'char_356_broca', 'Fuze': 'char_4126_fuze', 'ヴァルカリス': 'char_4166_varkis', 'アステシア': 'char_274_astesi', 'シデロカ': 'char_333_sidero', 'アカフユ': 'char_475_akafyu', 'レウスSノイルホーン': 'char_1030_noirc2', 'ラ・プルマ': 'char_421_crow', 'ハイモア': 'char_4066_highmo', 'テキーラ': 'char_486_takila', 'オッダ': 'char_4131_odda', 'グレースベアラー': 'char_4187_graceb', '祐天寺にゃむ': 'char_4185_amoris', 'ハディヤ': 'char_394_hadiya', 'アズリウス': 'char_129_bluep', 'プラチナ': 'char_204_platnm', 'グレースロート': 'char_367_swllow', 'Stormeye': 'char_611_acnipe', 'エイプリル': 'char_365_aprl', '寒芒クルース': 'char_1021_kroos2', 'インサイダー': 'char_498_inside', 'メテオリーテ': 'char_219_meteo', 'シェーシャ': 'char_379_sesa', 'ジエユン': 'char_4078_bdhkgt', 'イグゼキュター': 'char_279_excu', 'アオスタ': 'char_346_aosta', 'キチセイ': 'char_4203_kichi', 'スカイボックス': 'char_4213_skybx', 'アーミヤ': 'char_002_amiya', 'アブサント': 'char_405_absin', 'トミミ': 'char_411_tomimi', 'カニパラート': 'char_466_qanik', 'スカイフレア': 'char_166_skfire', 'Pith': 'char_612_accast', 'レイズ': 'char_306_leizi', 'アステジーニ': 'char_135_halo', 'ビーズワクス': 'char_344_beewax', 'レオンハルト': 'char_373_lionhd', 'サンタラ': 'char_341_sntlla', 'リプレーザ': 'char_4031_liesel', 'ミント': 'char_388_mint', 'アイリス': 'char_338_iris', 'ハーモニー': 'char_297_hamoni', 'デルフィーン': 'char_4110_delphn', '炎獄ラヴァ': 'char_1011_lava2', 'コロセラム': 'char_489_serum', 'アロマ': 'char_446_aroma', 'イェラ': 'char_4013_kjera', 'ロックロック': 'char_4040_rockr', 'ミニマリスト': 'char_4054_malist', 'ディアマンテ': 'char_499_kaitou', 'ウォーミー': 'char_4081_warmy', 'ミス・クリスティーン': 'char_4198_christ', 'テクノ': 'char_4164_tecno', 'メイヤー': 'char_242_otter', 'シーン': 'char_336_folivo', 'サンドレコナー': 'char_4140_lasher', 'サイレンス': 'char_108_silent', 'ワルファリン': 'char_171_bldsk', 'フォリニック': 'char_345_folnic', 'Touch': 'char_613_acmedc', 'レコードキーパー': 'char_4196_reckpr', 'セイロン': 'char_348_ceylon', 'ウィスパーレイン': 'char_436_whispr', 'ノウエル': 'char_4173_nowell', 'トゥイエ': 'char_402_tuye', 'マルベリー': 'char_473_mberry', 'ハニーベリー': 'char_449_glider', 'ハロルド': 'char_4114_harold', '濯塵ハイビスカス': 'char_1024_hbisc2', 'ヴァンデラ': 'char_494_vendla', 'パプリカ': 'char_4071_peper', 'パピルス': 'char_4139_papyrs', 'ウクシク': 'char_4224_turdus', 'タラクサカム': 'char_4222_taraxa', 'ニアール': 'char_148_nearl', 'ウン': 'char_226_hmau', 'ベースライン': 'char_4109_baslin', 'センシ': 'char_4143_sensi', 'レッド': 'char_144_red', 'ワイフー': 'char_243_waaifu', 'カフカ': 'char_214_kafka', 'ウユウ': 'char_455_nothin', 'フィグリーノ': 'char_4155_talr', 'リスカム': 'char_107_liskam', 'アンダーフロー': 'char_4137_udflow', 'クロワッサン': 'char_201_moeshd', 'バイソン': 'char_325_bison', 'ヴァルカン': 'char_163_hpsts', 'ヴェトチキ': 'char_4207_branch', 'アスベストス': 'char_378_asbest', 'シャレム': 'char_4025_aprot2', 'ツェルニー': 'char_4047_pianst', 'Blitz': 'char_457_blitz', 'ヘビーレイン': 'char_304_zebra', 'アッシュロック': 'char_431_ashlok', 'ファイヤーホイッスル': 'char_493_firwhl', 'オーロラ': 'char_422_aurora', 'セメント': 'char_464_cement', 'フィラエ': 'char_4148_philae', 'プロヴァンス': 'char_145_prove', 'メラナイト': 'char_4006_melnte', 'ファイヤーウォッチ': 'char_158_milu', 'アンドレアナ': 'char_218_cuttle', 'ルナカブ': 'char_4014_lunacu', 'トギフォンス': 'char_363_toddi', 'エラト': 'char_4043_erato', 'ジュー': 'char_4221_ju', '承曦グレイ': 'char_1027_greyy2', 'コールドショット': 'char_4104_coldst', 'スノーハンター': 'char_4211_snhunt', 'ブリギッド': 'char_4177_brigid', 'スプリア': 'char_4015_spuria', 'クリフハート': 'char_173_slchan', 'スノーズント': 'char_383_snsant', 'アーモンド': 'char_4105_almond', 'プラマニクス': 'char_174_slbell', 'シャマレ': 'char_254_vodfox', 'ルシーラ': 'char_4079_haini', 'イースチナ': 'char_195_glassb', 'グラウコス': 'char_326_glacus', 'プロヴァイゾ': 'char_4032_provs', 'グレインバッズ': 'char_4122_grabds', 'ウインドフリット': 'char_433_windft', 'キャサリン': 'char_4162_cathy', 'アランナ': 'char_4178_alanna', 'ソラ': 'char_101_sora', 'ハイディ': 'char_4045_heidi', '三角初華': 'char_4184_dolris', 'ツキノギ': 'char_343_tknogi', '九色鹿': 'char_4019_ncdeer', 'クエルクス': 'char_492_quercu', 'シィンズゥ': 'char_4172_xingzh', '萃香パフューマー': 'char_1022_flwr2', 'ヴァラルクビン': 'char_4102_threye', 'ボビング': 'char_487_bobb', 'ボタニ': 'char_4223_botany', 'マンティコア': 'char_215_mantic', 'キララ': 'char_478_kirara', '八幡海鈴': 'char_4186_tmoris', 'エフイーター': 'char_241_panda', 'エンフォーサー': 'char_4036_forcer', 'ロビン': 'char_451_robin', 'Frost': 'char_458_rfrost', 'ウルフェナイト': 'char_4171_wulfen', 'ベナ': 'char_369_bena', 'カゼマル': 'char_4016_kazema', 'Iana': 'char_4124_iana', '若葉睦': 'char_4183_mortis', 'ブリキ': 'char_4151_tinman', 'ティッピ': 'char_4191_tippi', 'エクシア': 'char_103_angel', 'アルケット': 'char_332_archet', 'Ash': 'char_456_ash', 'シュヴァルツ': 'char_340_shwaz', 'パゼオンカ': 'char_4055_bgsnow', 'ファートゥース': 'char_430_fartth', 'レミュアン': 'char_4193_lemuen', 'W': 'char_113_cqbw', 'フィアメッタ': 'char_300_phenxi', 'ロサ': 'char_197_poca', 'ティフォン': 'char_2012_typhon', 'ロスモンティス': 'char_391_rosmon', 'ウィシャデル': 'char_1035_wisdel', '遊龍チェン': 'char_1013_chen2', 'レイ': 'char_4117_ray', 'ナラントゥヤ': 'char_4138_narant', 'シージ': 'char_112_siege', 'バグパイプ': 'char_222_bpipe', 'サガ': 'char_362_saga', 'ウルピスフォリア': 'char_4026_vulpis', 'サイラッハ': 'char_479_sleach', 'フレイムテイル': 'char_420_flamtl', 'ヴィジェル': 'char_427_vigil', 'ミュルジス': 'char_249_mlyss', '凛御シルバーアッシュ': 'char_1045_svash2', 'イネス': 'char_4087_ines', 'イフリータ': 'char_134_ifrit', 'モスティマ': 'char_213_mostma', 'エイヤフィヤトラ': 'char_180_amgoat', 'ケオベ': 'char_2013_cerber', 'ホルハイヤ': 'char_4027_heyak', 'ロゴス': 'char_4133_logos', 'シー': 'char_2015_dusk', 'マルシル': 'char_4141_marcil', 'パッセンジャー': 'char_472_pasngr', 'カーネリアン': 'char_426_billro', 'リン': 'char_4080_lin', '聖聆プラマニクス': 'char_1046_sbell2', 'ゴールデングロー': 'char_377_gdglow', '荒蕪ラップランド': 'char_1038_whitw2', 'エーベンホルツ': 'char_4046_ebnhlz', 'ニンフ': 'char_4146_nymph', '熾炎ブレイズ': 'char_1040_blaze2', 'マントラ': 'char_4204_mantra', 'ネクラス': 'char_450_necras', 'ノーシス': 'char_206_gnosis', 'アンジェリーナ': 'char_291_aglina', 'スズラン': 'char_358_lisa', 'Raidian': 'char_614_acsupo', '溯光アステジーニ': 'char_1047_halo2', 'マゼラン': 'char_248_mgllan', 'レイディアン': 'char_4195_radian', '濁心スカジ': 'char_1012_skadi2', 'シヴィライト・エテルナ': 'char_4134_cetsyr', '淬羽サイレンス': 'char_1031_slent2', 'ハルカ': 'char_4202_haruka', 'リィン': 'char_2023_ling', 'ステインレス': 'char_4072_ironmn', 'ナスティ': 'char_4212_nasti', 'ヴィルトゥオーサ': 'char_245_cello', 'トラゴーディア': 'char_1042_phatm2', 'ファントム': 'char_250_phatom', '血掟テキサス': 'char_1028_texas2', 'キリンRヤトウ': 'char_1029_yato2', 'クラウンスレイヤー': 'char_1502_crosly', 'Misery': 'char_615_acspec', 'リー': 'char_322_lmlee', '琳琅スワイヤー': 'char_1033_swire2', 'ウィーディ': 'char_400_weedy', 'ア': 'char_225_haak', '新約エクシア': 'char_1041_angel2', 'グレイディーア': 'char_474_glady', 'ミヅキ': 'char_437_mizuki', 'アスカロン': 'char_4132_ascln', '帰溟スペクター': 'char_1023_ghost2', 'ドロシー': 'char_4048_doroth', 'Ela': 'char_4123_ela', 'ウァン': 'char_2027_wang', '引星ソーンズ': 'char_1039_thorn2', 'シャイニング': 'char_147_shining', 'ナイチンゲール': 'char_179_cgbird', 'ケルシー': 'char_003_kalts', 'ルーメン': 'char_4042_lumen', '純燼エイヤフィヤトラ': 'char_1016_agoat2', '焔影リード': 'char_1020_reed2', 'ティティ': 'char_4056_titi', 'Mon3tr': 'char_4179_monstr', 'ホシグマ': 'char_136_hsguma', 'Mechanist': 'char_610_acfend', 'サリア': 'char_202_demkni', 'ブレミシャイン': 'char_423_blemsh', 'シュウ': 'char_2025_shu', 'ニェン': 'char_2014_nian', 'マドロック': 'char_311_mudrok', 'ペナンス': 'char_4065_judge', 'ユーネクテス': 'char_416_zumama', 'ホルン': 'char_4039_horn', '滌火ジェシカ': 'char_1034_jesca2', 'サンクタ・ミキサー': 'char_4194_rmixer', 'ユー': 'char_2026_yu', '斬業ホシグマ': 'char_1044_hsgma2', 'マウンテン': 'char_264_f12yin', 'チョンユエ': 'char_2024_chyue', 'ベッローネ': 'char_4037_demetr', 'シルバーアッシュ': 'char_172_svrash', 'ソーンズ': 'char_293_thorns', 'チューバイ': 'char_4082_qiubai', '豊川祥子': 'char_4182_oblvns', '領主・Sharp': 'char_617_sharp2', 'ヘドリー': 'char_4088_hodrer', 'ウルピアヌス': 'char_4145_ulpia', 'ペペ': 'char_4058_pepe', '怒潮ズィマー': 'char_1051_headb2', 'チェン': 'char_010_chen', 'アイリーニ': 'char_4009_irene', 'デーゲンブレヒャー': 'char_4116_blkkgt', 'ブレイズ': 'char_017_huang', '百錬ガヴィル': 'char_1026_gvial2', 'スルト': 'char_350_surtr', 'ヴィヴィアナ': 'char_4098_vvana', 'ヴィーナ・ヴィクトリア': 'char_1019_siege2', '赤刃明霄チェン': 'char_1050_chen3', 'ヘラグ': 'char_188_helage', 'ズオ・ラウ': 'char_4121_zuole', 'パラス': 'char_485_pallas', '耀騎士ニアール': 'char_1014_nearl2', 'レッシング': 'char_4011_lessng', '聖約イグゼキュター': 'char_1032_excu2', 'エンテレケイア': 'char_4010_etlchi', 'ムリナール': 'char_4064_mlynar', '司霆レイズ': 'char_1043_leizi2', 'ケルン': 'char_4214_cairn', 'サベージ': 'char_230_savage', 'カタパルト': 'char_282_catap', 'ミッドナイト': 'char_283_midn', 'ビーハンター': 'char_137_brownb', 'ジャッキー': 'char_347_jaksel', 'ナイトメア': 'char_164_nightm', 'グラニ': 'char_220_grani', 'スカジ': 'char_263_skadi', '猟潮の騎士': 'trap_079_allydonq'}
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
ROOT = Path(__file__).resolve().parent

def get(url):
    error = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "OriginiumAtlasVideoUpdater/1.0"})
            with urllib.request.urlopen(req, timeout=35) as response:
                data = response.read(15_000_001)
                if len(data) > 15_000_000:
                    raise ValueError("応答サイズが上限を超えました")
                return data
        except Exception as exc:
            error = exc
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise RuntimeError("取得できませんでした: " + url) from error

def load(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default

def save(path, value):
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        temp = path.with_suffix(path.suffix + ".tmp")
        temp.write_text(text, encoding="utf-8")
        temp.replace(path)

def parse_feed(data):
    root = ET.fromstring(data)
    if root.tag != "{" + NS["a"] + "}feed":
        raise ValueError("YouTubeのAtomフィードではありません")
    if root.findtext("yt:channelId", namespaces=NS) not in (CHANNEL, CHANNEL[2:]):
        raise ValueError("日本公式以外のチャンネルです")
    out = []
    for e in root.findall("a:entry", NS):
        if e.findtext("yt:channelId", namespaces=NS) != CHANNEL:
            raise ValueError("日本公式以外の投稿が含まれています")
        vid = e.findtext("yt:videoId", default="", namespaces=NS)
        title = e.findtext("a:title", default="", namespaces=NS).strip()
        if not re.fullmatch(r"[\w-]{11}", vid, re.ASCII) or not title:
            raise ValueError("動画IDまたはタイトルが不正です")
        out.append({"id": vid, "title": title, "publishedAt": e.findtext("a:published", default="", namespaces=NS)})
    if not out:
        raise ValueError("フィードが空です。既存一覧は変更しません")
    return out

def classify(title, names):
    # 全文中の名前の出現ではなく、主役を明記する限定的な形式だけを認める。
    patterns = [
        (r"^アークナイツ\s*「([^」]+)」(?:ティザー|スペシャル)PV(?:\s.*)?$", "キャラクターPV"),
        (r"^アークナイツ\s+([^「『]+)[「『].*(?:MV|ライブ映像|周年記念PV).*$", "キャラクター映像"),
        (r"^「[^」]+」\s+(.+)$", "公式楽曲（EP）"),
        (r"^サガの炎国行脚録.*$", "キャラクターアニメ"),
        (r"^アークナイツ.*ラップランドの限定上映会.*$", "キャラクターPV"),
    ]
    for pattern, kind in patterns:
        m = re.fullmatch(pattern, title)
        if not m:
            continue
        subject = m.group(1).strip() if m.lastindex else ("サガ" if "サガの" in title else "ラップランド")
        # 異格は別名・別IDとして扱い、基底キャラへ推測で転記しない。
        if subject in names:
            return {"operatorKeys": [names[subject]], "operatorNames": [subject], "kind": kind}
    return None

def update(catalog, pending, entries, names, now):
    if catalog.get("channelId") != CHANNEL:
        raise ValueError("既存一覧のチャンネルが一致しません")
    by_id = {v["id"]: v for v in catalog["videos"]}
    if len(by_id) != len(catalog["videos"]):
        raise ValueError("既存一覧に動画IDの重複があります")
    waiting = {v["id"]: v for v in pending.get("videos", []) if v["id"] not in by_id}
    added = 0
    for entry in entries:
        vid = entry["id"]
        if vid in by_id:
            waiting.pop(vid, None)
            continue
        subject = classify(entry["title"], names)
        if subject:
            by_id[vid] = dict(entry, channelId=CHANNEL, **subject, evidence=[{
                "url": "https://www.youtube.com/watch?v=" + vid,
                "basis": "日本公式AtomフィードのチャンネルIDと、主役を明記する動画タイトルの完全一致を照合"
            }])
            waiting.pop(vid, None)
            added += 1
        else:
            waiting[vid] = dict(entry, channelId=CHANNEL, reason="主役・紹介対象をタイトルから確定できないため未登録")
    catalog = dict(catalog, schemaVersion=1, channelUrl=CHANNEL_URL,
                   publicationScope="日本公式YouTubeのみ", lastCheckedAt=now, videos=list(by_id.values()))
    if added:
        catalog["updatedAt"] = now
    pending = {"channelId": CHANNEL, "lastCheckedAt": now, "videos": list(waiting.values())}
    return catalog, pending, added

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--feed-file", type=Path, help="テスト用のAtomフィード。通常は指定不要")
    ap.add_argument("--offline-names", action="store_true", help="内蔵オペレーター名だけで判定")
    args = ap.parse_args()
    # 公式フィード取得が失敗した場合は、既存ファイルに一切書き込まない。
    entries = parse_feed(args.feed_file.read_bytes() if args.feed_file else get(FEED))
    names = dict(SEED_NAMES)
    if not args.offline_names:
        try:
            data = json.loads(get(NAMES_URL))
            names.update({v["name"]: k for k, v in data.items() if k.startswith("char_") and isinstance(v, dict) and v.get("name")})
        except Exception:
            print("注意: 最新のオペレーター名は取得できませんでした。内蔵名で継続します。")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    catalog = load(ROOT / "operator-videos.json", {})
    pending = load(ROOT / "pending-videos.json", {"videos": []})
    catalog, pending, added = update(catalog, pending, entries, names, now)
    save(ROOT / "operator-videos.json", catalog)
    save(ROOT / "pending-videos.json", pending)
    print(f"日本公式の新着{len(entries)}件を確認。自動登録{added}件、確認待ち計{len(pending['videos'])}件。")

if __name__ == "__main__":
    main()
