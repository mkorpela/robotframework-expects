from typing import List, Pattern
import re
from difflib import SequenceMatcher

def longest_substring(str1:str, str2:str) -> str:
    match = SequenceMatcher(None, str1, str2).find_longest_match(0, len(str1), 0, len(str2))
    return str1[match.a: match.a + match.size]

def iter(s1:str, s2:str) -> List[str]:
    if s1 == "" or s2 == "":
        return [] if s1 == s2 else [""]
    splitter = longest_substring(s1, s2)
    if splitter == "":
        return [""]
    s1a, s1b = s1.split(splitter, 1)
    s2a, s2b = s2.split(splitter, 1)
    return iter(s1a, s2a) + [splitter] + iter(s1b, s2b)

def regexpify(lst:List[str]) -> Pattern[str]:
    return re.compile('^'+''.join(re.escape(s) if s != "" else '.*' for s in lst)+'$')

if __name__ == '__main__':
    X = '''<!doctype html><html itemscope=\"\" itemtype=\"http://schema.org/WebPage\" lang=\"fi\"><head><meta content=\"text/html; charset=UTF-8\" http-equiv=\"Content-Type\"><meta content=\"/images/branding/googleg/1x/googleg_standard_color_128dp.png\" itemprop=\"image\"><title>Google</title><script nonce=\"hHbCzs7P/CvO3aWi12ShXw==\">(function(){window.google={kEI:'F8YPXpgIoqGbBYiGmpgF',kEXPI:'0,1353747,5662,730,224,755,3972,378,206,2955,249,10,168,121,424,338,175,364,671,483,3,278,4,60,315,175,251,209,10,410444,719024,143,1197791,358,38,329080,1294,12383,4855,32691,15248,861,19404,9286,363,3320,5505,8384,4858,1362,4325,4965,774,2255,2816,1923,3118,4524,1672,1719,1808,1976,10953,5297,2054,622,298,873,1217,9405,11306,2884,20,317,4148,1,368,2778,520,399,992,1285,8,3609,154,612,14,1279,2212,202,328,149,1103,842,515,1474,48,158,662,3438,260,52,1137,2,2063,606,1839,184,595,1138,43,521,1947,747,219,210,44,1009,93,328,1284,16,84,417,2426,23,2223,474,1339,748,209,830,3094,135,771,1216,332,524,7,728,592,1574,1879,1515,1345,4,6509,2832,258,214,367,1040,1042,2459,219,2465,4,842,3093,1274,108,976,270,4,22,486,2,513,654,480,809,99,2,433,930,548,118,643,517,366,732,4,17,1121,258,265,359,1035,2,119,10,335,93,505,78,457,25,206,1787,51,357,63,1029,94,35,967,656,46,66,1,109,10,2,17,38,107,138,442,373,959,426,61,10,26,230,781,189,6,15,169,107,32,536,265,87,116,72,174,700,760,22,81,194,112,1178,157,5859137,1874,1804020,4194851,2799848,1323,549,333,444,1,2,80,1,900,896,1,8,1,2,2551,1,748,141,795,10,553,1,4265,1,1,1,1,137,1,802,77,9,169,3,2,2,2,9,4,2,2,4,222,23964287',authuser:0,kscs:'c9c918f0_F8YPXpgIoqGbBYiGmpgF',kGL:'FI',kBL:'v77x'};google.sn='webhp';google.kHL='fi';google.jsfs='Ffpdje';})();(function(){google.lc=[];google.li=0;google.getEI=function(a){for(var b;a&&(!a.getAttribute||!(b=a.getAttribute(\"eid\")));)a=a.parentNode;return b||google.kEI};google.getLEI=function(a){for(var b=null;a&&(!a.getAttribute||!(b=a.getAttribute(\"leid\")));)a=a.parentNode;return b};google.https=function(){return\"https:\"==window.location.protocol};google.ml=function(){return null};google.time=function(){return(new Date).getTime()};google.log=function(a,b,e,c,g){if(a=google.logUrl(a,b,e,c,g)){b=new Image;var d=google.lc,f=google.li;d[f]=b;b.onerror=b.onload=b.onabort=function(){delete d[f]};google.vel&&google.vel.lu&&google.vel.lu(a);b.src=a;google.li=f+1}};google.logUrl=function(a,b,e,c,g){var d=\"\",f=google.ls||\"\";e||-1!=b.search(\"&ei=\")||(d=\"&ei=\"+google.getEI(c),-1==b.search(\"&lei=\")&&(c=google.getLEI(c))&&(d+=\"&lei=\"+c));c=\"\";!e&&google.cshid&&-1==b.search(\"&cshid=\")&&\"slh\"!=a&&(c=\"&cshid=\"+google.cshid);a=e||\"/\"+(g||\"gen_204\")+\"?atyp=i&ct=\"+a+\"&cad=\"+b+d+f+\"&zx=\"+google.time()+c;/^http:/i.test(a)&&google.https()&&(google.ml(Error(\"a\"),!1,{src:a,glmm:1}),a=\"\");return a};}).call(this);(function(){google.y={};google.x=function(a,b){if(a)var c=a.id;else{do c=Math.random();while(google.y[c])}google.y[c]=[a,b];return!1};google.lm=[];google.plm=function(a){google.lm.push.apply(google.lm,a)};google.lq=[];google.load=function(a,b,c){google.lq.push([[a],b,c])};google.loadAll=function(a,b){google.lq.push([a,b])};}).call(this);google.f={};(function(){document.documentElement.addEventListener(\"submit\",function(b){var a;if(a=b.target){var c=a.getAttribute(\"data-submitfalse\");a=\"1\"==c||\"q\"==c&&!a.elements.q.value?!0:!1}else a=!1;a&&(b.preventDefault(),b.stopPropagation())},!0);}).call(this);var a=window.location,b=a.href.indexOf(\"#\");if(0<=b){var c=a.href.substring(b+1);/(^|&)q=/.test(c)&&-1==c.indexOf(\"#\")&&a.replace(\"/search?\"+c.replace(/(^|&)fp=[^&]*/g,\"\")+\"&cad=h\")};</script><style>#gbar,#guser{font-size:13px;padding-top:1px !important;}#gbar{height:22px}#guser{padding-bottom:7px !important;text-align:right}.gbh,.gbd{border-top:1px solid #c9d7f1;font-size:1px}.gbh{height:0;position:absolute;top:24px;width:100%}@media all{.gb1{height:22px;margin-right:.5em;vertical-align:top}#gbar{float:left}}a.gb1,a.gb4{text-decoration:underline !important}a.gb1,a.gb4{color:#00c !important}.gbi .gb4{color:#dd8e27 !important}.gbf .gb4{color:#900 !important}\n</style><style>body,td,a,p,.h{font-family:arial,sans-serif}body{margin:0;overflow-y:scroll}#gog{padding:3px 8px 0}td{line-height:.8em}.gac_m td{line-height:17px}form{margin-bottom:20px}.h{color:#36c}.q{color:#00c}.ts td{padding:0}.ts{border-collapse:collapse}em{font-weight:bold;font-style:normal}.lst{height:25px;width:496px}.gsfi,.lst{font:18px arial,sans-serif}.gsfs{font:17px arial,sans-serif}.ds{display:inline-box;display:inline-block;margin:3px 0 4px;margin-left:4px}input{font-family:inherit}a.gb1,a.gb2,a.gb3,a.gb4{color:#11c !important}body{background:#fff;color:black}a{color:#11c;text-decoration:none}a:hover,a:active{text-decoration:underline}.fl a{color:#36c}a:visited{color:#551a8b}a.gb1,a.gb4{text-decoration:underline}a.gb3:hover{text-decoration:none}#ghead a.gb2:hover{color:#fff !important}.sblc{padding-top:5px}.sblc a{display:block;margin:2px 0;margin-left:13px;font-size:11px}.lsbb{background:#eee;border:solid 1px;border-color:#ccc #999 #999 #ccc;height:30px}.lsbb{display:block}.ftl,#fll a{display:inline-block;margin:0 12px}.lsb{background:url(/images/nav_logo229.png) 0 -261px repeat-x;border:none;color:#000;cursor:pointer;height:30px;margin:0;outline:0;font:15px arial,sans-serif;vertical-align:top}.lsb:active{background:#ccc}.lst:focus{outline:none}.tiah{width:458px}</style><script nonce=\"hHbCzs7P/CvO3aWi12ShXw==\"></script></head><body bgcolor=\"#fff\"><script nonce=\"hHbCzs7P/CvO3aWi12ShXw==\">(function(){var src='/images/nav_logo229.png';var iesg=false;document.body.onload = function(){window.n && window.n();if (document.images){new Image().src=src;}\nif (!iesg){document.f&&document.f.q.focus();document.gbqf&&document.gbqf.q.focus();}\n}\n})();</script><div id=\"mngb\"> <div id=gbar><nobr><b class=gb1>Haku</b> <a class=gb1 href=\"http://www.google.fi/imghp?hl=fi&tab=wi\">Kuvahaku</a> <a class=gb1 href=\"http://maps.google.fi/maps?hl=fi&tab=wl\">Maps</a> <a class=gb1 href=\"https://play.google.com/?hl=fi&tab=w8\">Play</a> <a class=gb1 href=\"http://www.youtube.com/?gl=FI&tab=w1\">YouTube</a> <a class=gb1 href=\"https://mail.google.com/mail/?tab=wm\">Gmail</a> <a class=gb1 href=\"https://drive.google.com/?tab=wo\">Drive</a> <a class=gb1 href=\"https://www.google.com/calendar?tab=wc\">Kalenteri</a> <a class=gb1 style=\"text-decoration:none\" href=\"https://www.google.fi/intl/fi/about/products?tab=wh\"><u>Lis\u00e4\u00e4</u> &raquo;</a></nobr></div><div id=guser width=100%><nobr><span id=gbn class=gbi></span><span id=gbf class=gbf></span><span id=gbe></span><a href=\"http://www.google.fi/history/optout?hl=fi\" class=gb4>Verkkohistoria</a> | <a  href=\"/preferences?hl=fi\" class=gb4>Asetukset</a> | <a target=_top id=gb_70 href=\"https://accounts.google.com/ServiceLogin?hl=fi&passive=true&continue=http://www.google.com/\" class=gb4>Kirjaudu sis\u00e4\u00e4n</a></nobr></div><div class=gbh style=left:0></div><div class=gbh style=right:0></div> </div><center><br clear=\"all\" id=\"lgpd\"><div id=\"lga\"><img alt=\"Google\" height=\"92\" src=\"/images/branding/googlelogo/1x/googlelogo_white_background_color_272x92dp.png\" style=\"padding:28px 0 14px\" width=\"272\" id=\"hplogo\"><br><br></div><form action=\"/search\" name=\"f\"><table cellpadding=\"0\" cellspacing=\"0\"><tr valign=\"top\"><td width=\"25%\">&nbsp;</td><td align=\"center\" nowrap=\"\"><input name=\"ie\" value=\"ISO-8859-1\" type=\"hidden\"><input value=\"fi\" name=\"hl\" type=\"hidden\"><input name=\"source\" type=\"hidden\" value=\"hp\"><input name=\"biw\" type=\"hidden\"><input name=\"bih\" type=\"hidden\"><div class=\"ds\" style=\"height:32px;margin:4px 0\"><div style=\"position:relative;zoom:1\"><input class=\"lst tiah\" style=\"color:#000;margin:0;padding:5px 8px 0 6px;vertical-align:top;padding-right:38px\" autocomplete=\"off\" value=\"\" title=\"Google-haku\" maxlength=\"2048\" name=\"q\" size=\"57\"><img src=\"/textinputassistant/tia.png\" style=\"position:absolute;cursor:pointer;right:5px;top:4px;z-index:300\" data-script-url=\"/textinputassistant/11/fi_tia.js\" id=\"tsuid1\" alt=\"\" height=\"23\" width=\"27\"><script nonce=\"hHbCzs7P/CvO3aWi12ShXw==\">(function(){var id='tsuid1';document.getElementById(id).onclick = function(){var s = document.createElement('script');s.src = this.getAttribute('data-script-url');(document.getElementById('xjsc')||document.body).appendChild(s);};})();</script></div></div><br style=\"line-height:0\"><span class=\"ds\"><span class=\"lsbb\"><input class=\"lsb\" value=\"Google-haku\" name=\"btnG\" type=\"submit\"></span></span><span class=\"ds\"><span class=\"lsbb\"><input class=\"lsb\" id=\"tsuid2\" value=\"Kokeilen onneani\" name=\"btnI\" type=\"submit\"><script nonce=\"hHbCzs7P/CvO3aWi12ShXw==\">(function(){var id='tsuid2';document.getElementById(id).onclick = function(){if (this.form.q.value){this.checked = 1;if (this.form.iflsig)this.form.iflsig.disabled = false;}\nelse top.location='/doodles/';};})();</script><input value=\"AAP1E1EAAAAAXg_UJ4SI6d3tIoruD1RZmNNqI_VTjYxd\" name=\"iflsig\" type=\"hidden\"></span></span></td><td class=\"fl sblc\" align=\"left\" nowrap=\"\" width=\"25%\"><a href=\"/advanced_search?hl=fi&amp;authuser=0\">Tarkennettu haku</a><a href=\"/language_tools?hl=fi&amp;authuser=0\">Kielity\u00f6kalut</a></td></tr></table><input id=\"gbv\" name=\"gbv\" type=\"hidden\" value=\"1\"><script nonce=\"hHbCzs7P/CvO3aWi12ShXw==\">(function(){var a,b=\"1\";if(document&&document.getElementById)if(\"undefined\"!=typeof XMLHttpRequest)b=\"2\";else if(\"undefined\"!=typeof ActiveXObject){var c,d,e=[\"MSXML2.XMLHTTP.6.0\",\"MSXML2.XMLHTTP.3.0\",\"MSXML2.XMLHTTP\",\"Microsoft.XMLHTTP\"];for(c=0;d=e[c++];)try{new ActiveXObject(d),b=\"2\"}catch(h){}}a=b;if(\"2\"==a&&-1==location.search.indexOf(\"&gbv=2\")){var f=google.gbvu,g=document.getElementById(\"gbv\");g&&(g.value=a);f&&window.setTimeout(function(){location.href=f},0)};}).call(this);</script></form><div id=\"gac_scont\"></div><div style=\"font-size:83%;min-height:3.5em\"><br><div id=\"gws-output-pages-elements-homepage_additional_languages__als\"><style>#gws-output-pages-elements-homepage_additional_languages__als{font-size:small;margin-bottom:24px}#SIvCob{display:inline-block;line-height:28px;}#SIvCob a{padding:0 3px;}.H6sW5{display:inline-block;margin:0 2px;white-space:nowrap}.z4hgWe{display:inline-block;margin:0 2px}</style><div id=\"SIvCob\">Googlen versiot:  <a href=\"http://www.google.com/setprefs?sig=0_c0VjhULyvVcnPjyQN5lkh_wUQlQ%3D&amp;hl=sv&amp;source=homepage&amp;sa=X&amp;ved=0ahUKEwjY7_GCw-jmAhWi0KYKHQiDBlMQ2ZgBCAU\">svenska</a>  </div></div></div><span id=\"footer\"><div style=\"font-size:10pt\"><div style=\"margin:19px auto;text-align:center\" id=\"fll\"><a href=\"/intl/fi/ads/\">Googlen mainontaratkaisut</a><a href=\"http://www.google.fi/intl/fi/services/\">Yritysratkaisut</a><a href=\"/intl/fi/about.html\">Tietoja Googlesta</a><a href=\"http://www.google.com/setprefdomain?prefdom=FI&amp;prev=http://www.google.fi/&amp;sig=K_Y42aBv_dWMSncnrKW2i-TOFu1DY%3D\">Google.fi</a></div></div><p style=\"color:#767676;font-size:8pt\">&copy; 2020 - <a href=\"/intl/fi/policies/privacy/\">Tietosuoja</a> - <a href=\"/intl/fi/policies/terms/\">K\u00e4ytt\u00f6ehdot</a></p></span></center><script nonce=\"hHbCzs7P/CvO3aWi12ShXw==\">(function(){window.google.cdo={height:0,width:0};(function(){var a=window.innerWidth,b=window.innerHeight;if(!a||!b){var c=window.document,d=\"CSS1Compat\"==c.compatMode?c.documentElement:c.body;a=d.clientWidth;b=d.clientHeight}a&&b&&(a!=google.cdo.width||b!=google.cdo.height)&&google.log(\"\",\"\",\"/client_204?&atyp=i&biw=\"+a+\"&bih=\"+b+\"&ei=\"+google.kEI);}).call(this);})();(function(){var u='/xjs/_/js/k\\x3dxjs.hp.en.3mkxARIkkN0.O/m\\x3dsb_he,d/am\\x3dAAMCbAQ/d\\x3d1/rs\\x3dACT90oH0ZgFCL-q_Qh6y8ytgGBhQJ9zvUw';\nsetTimeout(function(){var b=document;var a=\"SCRIPT\";\"application/xhtml+xml\"===b.contentType&&(a=a.toLowerCase());a=b.createElement(a);a.src=u;google.timers&&google.timers.load&&google.tick&&google.tick(\"load\",\"xjsls\");document.body.appendChild(a)},0);})();(function(){window.google.xjsu='/xjs/_/js/k\\x3dxjs.hp.en.3mkxARIkkN0.O/m\\x3dsb_he,d/am\\x3dAAMCbAQ/d\\x3d1/rs\\x3dACT90oH0ZgFCL-q_Qh6y8ytgGBhQJ9zvUw';})();function _DumpException(e){throw e;}\nfunction _F_installCss(c){}\n(function(){google.spjs=false;google.snet=true;google.em=[];google.emw=false;})();(function(){var pmc='{\\x22d\\x22:{},\\x22sb_he\\x22:{\\x22agen\\x22:true,\\x22cgen\\x22:true,\\x22client\\x22:\\x22heirloom-hp\\x22,\\x22dh\\x22:true,\\x22dhqt\\x22:true,\\x22ds\\x22:\\x22\\x22,\\x22ffql\\x22:\\x22en\\x22,\\x22fl\\x22:true,\\x22host\\x22:\\x22google.com\\x22,\\x22isbh\\x22:28,\\x22jsonp\\x22:true,\\x22msgs\\x22:{\\x22cibl\\x22:\\x22Tyhjenn\u00e4 haku\\x22,\\x22dym\\x22:\\x22Tarkoititko:\\x22,\\x22lcky\\x22:\\x22Kokeilen onneani\\x22,\\x22lml\\x22:\\x22Lis\u00e4tietoja\\x22,\\x22oskt\\x22:\\x22Sy\u00f6tt\u00f6ty\u00f6kalut\\x22,\\x22psrc\\x22:\\x22T\u00e4m\u00e4 haku on poistettu \\\\u003Ca href\\x3d\\\\\\x22/history\\\\\\x22\\\\u003EVerkkohistoriastasi\\\\u003C/a\\\\u003E\\x22,\\x22psrl\\x22:\\x22Poista\\x22,\\x22sbit\\x22:\\x22Hae kuvan perusteella\\x22,\\x22srch\\x22:\\x22Google-haku\\x22},\\x22ovr\\x22:{},\\x22pq\\x22:\\x22\\x22,\\x22refpd\\x22:true,\\x22rfs\\x22:[],\\x22sbpl\\x22:24,\\x22sbpr\\x22:24,\\x22scd\\x22:10,\\x22sce\\x22:5,\\x22stok\\x22:\\x22Bi6XYXM0mi1VKOrGZ257sXeY0HM\\x22,\\x22uhde\\x22:false}}';google.pmc=JSON.parse(pmc);})();</script>        </body></html>'''
    Y = '''<!doctype html><html itemscope=\"\" itemtype=\"http://schema.org/WebPage\" lang=\"fi\"><head><meta content=\"text/html; charset=UTF-8\" http-equiv=\"Content-Type\"><meta content=\"/images/branding/googleg/1x/googleg_standard_color_128dp.png\" itemprop=\"image\"><title>Google</title><script nonce=\"RO9WwpHi+AxZN2NGce4C3A==\">(function(){window.google={kEI:'XMYPXpzjO7qLk74Pj_O1kAs',kEXPI:'0,1353747,5662,730,224,3656,1070,378,207,1244,1710,250,10,713,338,175,352,12,672,482,3,278,4,60,315,635,10,1129468,143,1197755,394,38,329080,1294,12383,4855,32692,15247,867,17444,11240,369,8819,8384,1699,3160,1361,4324,4967,773,2256,4738,3118,6196,1719,1808,1976,10953,5297,2054,920,873,1214,2978,2785,3645,11306,2883,21,318,1980,2167,1,368,2779,519,399,992,1285,8,2796,967,612,14,1167,112,2212,202,328,149,1103,842,515,317,825,278,54,48,820,3438,260,52,1137,2,2063,606,789,1050,184,595,1182,520,1947,747,219,210,44,1009,93,328,1284,16,84,417,2426,1639,607,474,1339,748,1039,3094,133,773,1548,524,9,726,592,1574,2705,689,91,1254,6513,2832,258,581,356,684,1042,2459,281,2116,291,700,142,3092,1275,108,976,270,4,21,1002,566,88,480,809,99,2,317,116,508,972,116,12,1148,366,885,989,258,265,358,1158,9,275,2,149,585,458,302,1716,50,357,63,853,305,967,656,47,65,1,109,10,2,17,6,139,138,442,373,959,492,31,230,776,194,6,15,183,93,274,40,254,266,86,362,327,373,760,22,82,38,268,425,909,706,5858431,1805894,4194805,46,2801171,549,333,444,1,2,80,1,900,896,1,8,1,2,2551,1,748,141,59,736,563,1,4265,1,1,1,1,137,1,802,77,9,163,4,3,2,4,11,1,5,2,6,220,23964288',authuser:0,kscs:'c9c918f0_XMYPXpzjO7qLk74Pj_O1kAs',kGL:'FI',kBL:'v77x'};google.sn='webhp';google.kHL='fi';google.jsfs='Ffpdje';})();(function(){google.lc=[];google.li=0;google.getEI=function(a){for(var b;a&&(!a.getAttribute||!(b=a.getAttribute(\"eid\")));)a=a.parentNode;return b||google.kEI};google.getLEI=function(a){for(var b=null;a&&(!a.getAttribute||!(b=a.getAttribute(\"leid\")));)a=a.parentNode;return b};google.https=function(){return\"https:\"==window.location.protocol};google.ml=function(){return null};google.time=function(){return(new Date).getTime()};google.log=function(a,b,e,c,g){if(a=google.logUrl(a,b,e,c,g)){b=new Image;var d=google.lc,f=google.li;d[f]=b;b.onerror=b.onload=b.onabort=function(){delete d[f]};google.vel&&google.vel.lu&&google.vel.lu(a);b.src=a;google.li=f+1}};google.logUrl=function(a,b,e,c,g){var d=\"\",f=google.ls||\"\";e||-1!=b.search(\"&ei=\")||(d=\"&ei=\"+google.getEI(c),-1==b.search(\"&lei=\")&&(c=google.getLEI(c))&&(d+=\"&lei=\"+c));c=\"\";!e&&google.cshid&&-1==b.search(\"&cshid=\")&&\"slh\"!=a&&(c=\"&cshid=\"+google.cshid);a=e||\"/\"+(g||\"gen_204\")+\"?atyp=i&ct=\"+a+\"&cad=\"+b+d+f+\"&zx=\"+google.time()+c;/^http:/i.test(a)&&google.https()&&(google.ml(Error(\"a\"),!1,{src:a,glmm:1}),a=\"\");return a};}).call(this);(function(){google.y={};google.x=function(a,b){if(a)var c=a.id;else{do c=Math.random();while(google.y[c])}google.y[c]=[a,b];return!1};google.lm=[];google.plm=function(a){google.lm.push.apply(google.lm,a)};google.lq=[];google.load=function(a,b,c){google.lq.push([[a],b,c])};google.loadAll=function(a,b){google.lq.push([a,b])};}).call(this);google.f={};(function(){document.documentElement.addEventListener(\"submit\",function(b){var a;if(a=b.target){var c=a.getAttribute(\"data-submitfalse\");a=\"1\"==c||\"q\"==c&&!a.elements.q.value?!0:!1}else a=!1;a&&(b.preventDefault(),b.stopPropagation())},!0);}).call(this);var a=window.location,b=a.href.indexOf(\"#\");if(0<=b){var c=a.href.substring(b+1);/(^|&)q=/.test(c)&&-1==c.indexOf(\"#\")&&a.replace(\"/search?\"+c.replace(/(^|&)fp=[^&]*/g,\"\")+\"&cad=h\")};</script><style>#gbar,#guser{font-size:13px;padding-top:1px !important;}#gbar{height:22px}#guser{padding-bottom:7px !important;text-align:right}.gbh,.gbd{border-top:1px solid #c9d7f1;font-size:1px}.gbh{height:0;position:absolute;top:24px;width:100%}@media all{.gb1{height:22px;margin-right:.5em;vertical-align:top}#gbar{float:left}}a.gb1,a.gb4{text-decoration:underline !important}a.gb1,a.gb4{color:#00c !important}.gbi .gb4{color:#dd8e27 !important}.gbf .gb4{color:#900 !important}\n</style><style>body,td,a,p,.h{font-family:arial,sans-serif}body{margin:0;overflow-y:scroll}#gog{padding:3px 8px 0}td{line-height:.8em}.gac_m td{line-height:17px}form{margin-bottom:20px}.h{color:#36c}.q{color:#00c}.ts td{padding:0}.ts{border-collapse:collapse}em{font-weight:bold;font-style:normal}.lst{height:25px;width:496px}.gsfi,.lst{font:18px arial,sans-serif}.gsfs{font:17px arial,sans-serif}.ds{display:inline-box;display:inline-block;margin:3px 0 4px;margin-left:4px}input{font-family:inherit}a.gb1,a.gb2,a.gb3,a.gb4{color:#11c !important}body{background:#fff;color:black}a{color:#11c;text-decoration:none}a:hover,a:active{text-decoration:underline}.fl a{color:#36c}a:visited{color:#551a8b}a.gb1,a.gb4{text-decoration:underline}a.gb3:hover{text-decoration:none}#ghead a.gb2:hover{color:#fff !important}.sblc{padding-top:5px}.sblc a{display:block;margin:2px 0;margin-left:13px;font-size:11px}.lsbb{background:#eee;border:solid 1px;border-color:#ccc #999 #999 #ccc;height:30px}.lsbb{display:block}.ftl,#fll a{display:inline-block;margin:0 12px}.lsb{background:url(/images/nav_logo229.png) 0 -261px repeat-x;border:none;color:#000;cursor:pointer;height:30px;margin:0;outline:0;font:15px arial,sans-serif;vertical-align:top}.lsb:active{background:#ccc}.lst:focus{outline:none}.tiah{width:458px}</style><script nonce=\"RO9WwpHi+AxZN2NGce4C3A==\"></script></head><body bgcolor=\"#fff\"><script nonce=\"RO9WwpHi+AxZN2NGce4C3A==\">(function(){var src='/images/nav_logo229.png';var iesg=false;document.body.onload = function(){window.n && window.n();if (document.images){new Image().src=src;}\nif (!iesg){document.f&&document.f.q.focus();document.gbqf&&document.gbqf.q.focus();}\n}\n})();</script><div id=\"mngb\"> <div id=gbar><nobr><b class=gb1>Haku</b> <a class=gb1 href=\"http://www.google.fi/imghp?hl=fi&tab=wi\">Kuvahaku</a> <a class=gb1 href=\"http://maps.google.fi/maps?hl=fi&tab=wl\">Maps</a> <a class=gb1 href=\"https://play.google.com/?hl=fi&tab=w8\">Play</a> <a class=gb1 href=\"http://www.youtube.com/?gl=FI&tab=w1\">YouTube</a> <a class=gb1 href=\"https://mail.google.com/mail/?tab=wm\">Gmail</a> <a class=gb1 href=\"https://drive.google.com/?tab=wo\">Drive</a> <a class=gb1 href=\"https://www.google.com/calendar?tab=wc\">Kalenteri</a> <a class=gb1 style=\"text-decoration:none\" href=\"https://www.google.fi/intl/fi/about/products?tab=wh\"><u>Lis\u00e4\u00e4</u> &raquo;</a></nobr></div><div id=guser width=100%><nobr><span id=gbn class=gbi></span><span id=gbf class=gbf></span><span id=gbe></span><a href=\"http://www.google.fi/history/optout?hl=fi\" class=gb4>Verkkohistoria</a> | <a  href=\"/preferences?hl=fi\" class=gb4>Asetukset</a> | <a target=_top id=gb_70 href=\"https://accounts.google.com/ServiceLogin?hl=fi&passive=true&continue=http://www.google.com/\" class=gb4>Kirjaudu sis\u00e4\u00e4n</a></nobr></div><div class=gbh style=left:0></div><div class=gbh style=right:0></div> </div><center><br clear=\"all\" id=\"lgpd\"><div id=\"lga\"><img alt=\"Google\" height=\"92\" src=\"/images/branding/googlelogo/1x/googlelogo_white_background_color_272x92dp.png\" style=\"padding:28px 0 14px\" width=\"272\" id=\"hplogo\"><br><br></div><form action=\"/search\" name=\"f\"><table cellpadding=\"0\" cellspacing=\"0\"><tr valign=\"top\"><td width=\"25%\">&nbsp;</td><td align=\"center\" nowrap=\"\"><input name=\"ie\" value=\"ISO-8859-1\" type=\"hidden\"><input value=\"fi\" name=\"hl\" type=\"hidden\"><input name=\"source\" type=\"hidden\" value=\"hp\"><input name=\"biw\" type=\"hidden\"><input name=\"bih\" type=\"hidden\"><div class=\"ds\" style=\"height:32px;margin:4px 0\"><div style=\"position:relative;zoom:1\"><input class=\"lst tiah\" style=\"color:#000;margin:0;padding:5px 8px 0 6px;vertical-align:top;padding-right:38px\" autocomplete=\"off\" value=\"\" title=\"Google-haku\" maxlength=\"2048\" name=\"q\" size=\"57\"><img src=\"/textinputassistant/tia.png\" style=\"position:absolute;cursor:pointer;right:5px;top:4px;z-index:300\" data-script-url=\"/textinputassistant/11/fi_tia.js\" id=\"tsuid1\" alt=\"\" height=\"23\" width=\"27\"><script nonce=\"RO9WwpHi+AxZN2NGce4C3A==\">(function(){var id='tsuid1';document.getElementById(id).onclick = function(){var s = document.createElement('script');s.src = this.getAttribute('data-script-url');(document.getElementById('xjsc')||document.body).appendChild(s);};})();</script></div></div><br style=\"line-height:0\"><span class=\"ds\"><span class=\"lsbb\"><input class=\"lsb\" value=\"Google-haku\" name=\"btnG\" type=\"submit\"></span></span><span class=\"ds\"><span class=\"lsbb\"><input class=\"lsb\" id=\"tsuid2\" value=\"Kokeilen onneani\" name=\"btnI\" type=\"submit\"><script nonce=\"RO9WwpHi+AxZN2NGce4C3A==\">(function(){var id='tsuid2';document.getElementById(id).onclick = function(){if (this.form.q.value){this.checked = 1;if (this.form.iflsig)this.form.iflsig.disabled = false;}\nelse top.location='/doodles/';};})();</script><input value=\"AAP1E1EAAAAAXg_UbCCkAE5iHakg3Q7_yMmwO-PQDcve\" name=\"iflsig\" type=\"hidden\"></span></span></td><td class=\"fl sblc\" align=\"left\" nowrap=\"\" width=\"25%\"><a href=\"/advanced_search?hl=fi&amp;authuser=0\">Tarkennettu haku</a><a href=\"/language_tools?hl=fi&amp;authuser=0\">Kielity\u00f6kalut</a></td></tr></table><input id=\"gbv\" name=\"gbv\" type=\"hidden\" value=\"1\"><script nonce=\"RO9WwpHi+AxZN2NGce4C3A==\">(function(){var a,b=\"1\";if(document&&document.getElementById)if(\"undefined\"!=typeof XMLHttpRequest)b=\"2\";else if(\"undefined\"!=typeof ActiveXObject){var c,d,e=[\"MSXML2.XMLHTTP.6.0\",\"MSXML2.XMLHTTP.3.0\",\"MSXML2.XMLHTTP\",\"Microsoft.XMLHTTP\"];for(c=0;d=e[c++];)try{new ActiveXObject(d),b=\"2\"}catch(h){}}a=b;if(\"2\"==a&&-1==location.search.indexOf(\"&gbv=2\")){var f=google.gbvu,g=document.getElementById(\"gbv\");g&&(g.value=a);f&&window.setTimeout(function(){location.href=f},0)};}).call(this);</script></form><div id=\"gac_scont\"></div><div style=\"font-size:83%;min-height:3.5em\"><br><div id=\"gws-output-pages-elements-homepage_additional_languages__als\"><style>#gws-output-pages-elements-homepage_additional_languages__als{font-size:small;margin-bottom:24px}#SIvCob{display:inline-block;line-height:28px;}#SIvCob a{padding:0 3px;}.H6sW5{display:inline-block;margin:0 2px;white-space:nowrap}.z4hgWe{display:inline-block;margin:0 2px}</style><div id=\"SIvCob\">Googlen versiot:  <a href=\"http://www.google.com/setprefs?sig=0_NWoyMtCKNGyjURUVmH9rbpURSGs%3D&amp;hl=sv&amp;source=homepage&amp;sa=X&amp;ved=0ahUKEwicgaGkw-jmAhW6xcQBHY95DbIQ2ZgBCAU\">svenska</a>  </div></div></div><span id=\"footer\"><div style=\"font-size:10pt\"><div style=\"margin:19px auto;text-align:center\" id=\"fll\"><a href=\"/intl/fi/ads/\">Googlen mainontaratkaisut</a><a href=\"http://www.google.fi/intl/fi/services/\">Yritysratkaisut</a><a href=\"/intl/fi/about.html\">Tietoja Googlesta</a><a href=\"http://www.google.com/setprefdomain?prefdom=FI&amp;prev=http://www.google.fi/&amp;sig=K_ELV3KaMJz25fNaHuN5uGUMgBREY%3D\">Google.fi</a></div></div><p style=\"color:#767676;font-size:8pt\">&copy; 2020 - <a href=\"/intl/fi/policies/privacy/\">Tietosuoja</a> - <a href=\"/intl/fi/policies/terms/\">K\u00e4ytt\u00f6ehdot</a></p></span></center><script nonce=\"RO9WwpHi+AxZN2NGce4C3A==\">(function(){window.google.cdo={height:0,width:0};(function(){var a=window.innerWidth,b=window.innerHeight;if(!a||!b){var c=window.document,d=\"CSS1Compat\"==c.compatMode?c.documentElement:c.body;a=d.clientWidth;b=d.clientHeight}a&&b&&(a!=google.cdo.width||b!=google.cdo.height)&&google.log(\"\",\"\",\"/client_204?&atyp=i&biw=\"+a+\"&bih=\"+b+\"&ei=\"+google.kEI);}).call(this);})();(function(){var u='/xjs/_/js/k\\x3dxjs.hp.en.3mkxARIkkN0.O/m\\x3dsb_he,d/am\\x3dAAMCbAQ/d\\x3d1/rs\\x3dACT90oH0ZgFCL-q_Qh6y8ytgGBhQJ9zvUw';\nsetTimeout(function(){var b=document;var a=\"SCRIPT\";\"application/xhtml+xml\"===b.contentType&&(a=a.toLowerCase());a=b.createElement(a);a.src=u;google.timers&&google.timers.load&&google.tick&&google.tick(\"load\",\"xjsls\");document.body.appendChild(a)},0);})();(function(){window.google.xjsu='/xjs/_/js/k\\x3dxjs.hp.en.3mkxARIkkN0.O/m\\x3dsb_he,d/am\\x3dAAMCbAQ/d\\x3d1/rs\\x3dACT90oH0ZgFCL-q_Qh6y8ytgGBhQJ9zvUw';})();function _DumpException(e){throw e;}\nfunction _F_installCss(c){}\n(function(){google.spjs=false;google.snet=true;google.em=[];google.emw=false;})();(function(){var pmc='{\\x22d\\x22:{},\\x22sb_he\\x22:{\\x22agen\\x22:true,\\x22cgen\\x22:true,\\x22client\\x22:\\x22heirloom-hp\\x22,\\x22dh\\x22:true,\\x22dhqt\\x22:true,\\x22ds\\x22:\\x22\\x22,\\x22ffql\\x22:\\x22en\\x22,\\x22fl\\x22:true,\\x22host\\x22:\\x22google.com\\x22,\\x22isbh\\x22:28,\\x22jsonp\\x22:true,\\x22msgs\\x22:{\\x22cibl\\x22:\\x22Tyhjenn\u00e4 haku\\x22,\\x22dym\\x22:\\x22Tarkoititko:\\x22,\\x22lcky\\x22:\\x22Kokeilen onneani\\x22,\\x22lml\\x22:\\x22Lis\u00e4tietoja\\x22,\\x22oskt\\x22:\\x22Sy\u00f6tt\u00f6ty\u00f6kalut\\x22,\\x22psrc\\x22:\\x22T\u00e4m\u00e4 haku on poistettu \\\\u003Ca href\\x3d\\\\\\x22/history\\\\\\x22\\\\u003EVerkkohistoriastasi\\\\u003C/a\\\\u003E\\x22,\\x22psrl\\x22:\\x22Poista\\x22,\\x22sbit\\x22:\\x22Hae kuvan perusteella\\x22,\\x22srch\\x22:\\x22Google-haku\\x22},\\x22ovr\\x22:{},\\x22pq\\x22:\\x22\\x22,\\x22refpd\\x22:true,\\x22rfs\\x22:[],\\x22sbpl\\x22:24,\\x22sbpr\\x22:24,\\x22scd\\x22:10,\\x22sce\\x22:5,\\x22stok\\x22:\\x22-8OMP8GW-by5IkB-F3zxHPhBR4Y\\x22,\\x22uhde\\x22:false}}';google.pmc=JSON.parse(pmc);})();</script>        </body></html>'''
    print(['', 'ab', '', 'a'] == iter("abba", "baba"))
    print(['moi'] == iter("moi", "moi"))
    print([''] == (iter("xyz", "abc")))
    print(['x', '', 'i'] == iter("xcci", "xbbi"))
    matcher = regexpify(iter(X, Y))
    print(matcher.match(X))
    print(matcher.match(Y))
    print(matcher.match("MOO"))
    #print(matcher.pattern)
