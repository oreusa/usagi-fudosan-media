import { page } from "../lib/life.js";
// くらべたおかいものリストを TOWN NOTE の中で開く（lib/life.js）
export async function onRequestGet({ request }) { return page(request); }
