import { page } from "../lib/life.js";
// 11/23 ふだんは新しい土台の関西のページ（links/shin/kaimawari.html・tools/shin/build.py）を _middleware.js が先に出す。
// それが無い時だけ、燈の前のページ（/kyu/kaimawari.html）を TOWN の名前にして映す（燈の新しいページは関東用なので映さない）。
export async function onRequestGet({ request }) { return page(request, "/kyu/kaimawari.html"); }
