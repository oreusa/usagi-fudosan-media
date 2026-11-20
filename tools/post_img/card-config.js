// 関西 TOWN NOTE の表紙の絵の設定（card.js が読む）
const path=require('path');const R=path.join(__dirname,'..','..');
// night：夜9時の枠（n7 ひと駅しらべ・x21）は星空の形（11/20 オーナーOKの見本どおり）
module.exports={name:'KANSAI TOWN NOTE',night:/-(n7|x21)$/,logo:path.join(R,'tools','brand','logo.png'),brand:'TOWN NOTE',out:path.join(R,'media','post'),base:'https://oreusa.github.io/usagi-fudosan-media/media/post/'};
