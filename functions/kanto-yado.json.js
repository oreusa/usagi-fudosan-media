import { asset } from "../lib/life.js";
// /otoku の宿の一覧（燈の物）
export async function onRequestGet({ request }) { return asset(request, "/kanto-yado.json"); }
