import { asset } from "../../lib/life.js";
// 燈の部品（/assets/…）を TOWN NOTE から読む（lib/life.js）
export async function onRequestGet({ request }) {
  const u = new URL(request.url);
  return asset(request, u.pathname.replace(/^\/life-assets\//, "/assets/") + u.search);
}
