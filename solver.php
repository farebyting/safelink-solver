<?php
$j = tempnam(sys_get_temp_dir(), "ck");
$h = curl_init();
curl_setopt_array($h, [CURLOPT_RETURNTRANSFER => 1, CURLOPT_COOKIEJAR => $j, CURLOPT_COOKIEFILE => $j,
  CURLOPT_FOLLOWLOCATION => 1, CURLOPT_IPRESOLVE => CURL_IPRESOLVE_V4, CURLOPT_ENCODING => "", CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_2_0, CURLOPT_USERAGENT => "Mozilla/5.0", CURLOPT_HTTPHEADER => ["content-type: application/json"]]);
function g($h, $u, $b = null) { curl_setopt($h, CURLOPT_URL, $u); if ($b === null) curl_setopt($h, CURLOPT_HTTPGET, 1); else curl_setopt($h, CURLOPT_POSTFIELDS, $b); return curl_exec($h); }
$p = g($h, $argv[1]);
preg_match('/ray_id" value="([^"]+)/', $p, $r); preg_match('/alias" value="([^"]+)/', $p, $a);
g($h, "https://app.khaddavi.net/redirect.php?ray_id={$r[1]}&alias={$a[1]}");
g($h, "https://app.khaddavi.net/api/verify", '{"_a":0}');
$go = json_decode(g($h, "https://app.khaddavi.net/api/go", '{"key":1,"size":"3840.2160"}'), true);
preg_match('/href = "(.+?)"/', g($h, $go["url"]), $m);
echo stripslashes($m[1]), "\n";
