#!/usr/bin/env perl
use HTTP::Tiny; use HTTP::CookieJar; use JSON::PP;
my $h = HTTP::Tiny->new(cookie_jar => HTTP::CookieJar->new, agent => "Mozilla/5.0");
my $p = $h->get($ARGV[0])->{content}; my ($r, $a) = ($p =~ /ray_id" value="([^"]+)/, $p =~ /alias" value="([^"]+)/);
$h->get("https://app.khaddavi.net/redirect.php?ray_id=$r&alias=$a");
my ($x) = $h->cookie_jar->cookie_header("https://app.khaddavi.net") =~ /XSRF-TOKEN=([^;]+)/;
my $post = sub { $h->post("https://app.khaddavi.net" . shift, { headers => { "content-type" => "application/json", "x-xsrf-token" => $x }, content => shift })->{content} };
$post->("/api/verify", '{"_a":0}');
$h->get(decode_json($post->("/api/go", '{"key":1,"size":"3840.2160"}'))->{url})->{content} =~ /href = "(.+?)"/; print $1 =~ s!\\/!/!gr, "\n";
