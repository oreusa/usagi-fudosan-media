/* TOWN NOTES（仮）: おでかけリストに、リールと同じ関西の地図とピンを組み込む。
   今のページ（タブ・府県ボタン・カード）をそのまま読み、選んでいるタブと府県のピンだけを立てる。
   地図の形は tools/outing_reel/paths.json（mapsvg.com, CC BY 4.0）、場所は /townnotes/geo.json。 */
(function(){
var PATHS={"aichi":"m 260.23993,277.87889 -0.17,-0.35 0.5,-1.77 -0.86,-1.4 0.11,-1.46 0.46,-1.37 -0.25,-0.32 -0.89,0.36 -1.14,-0.35 0,0 -0.97,-1.57 -0.32,-1.21 0,0 0.22,-2.19 1.69,-2.97 1.28,0.15 1.66,-0.5 1.48,-1.13 -0.02,0.57 1.18,0.87 -0.03,0.65 0.5,0.21 -0.09,0.48 0.27,0.32 0.32,0.15 0.3,-0.21 0.94,0.39 0.52,0.71 0.85,-0.17 0.92,-0.73 0.63,-0.01 0.75,0.47 -0.07,0.24 0.84,0.05 -0.02,0.31 0.99,0.5 1.72,-1.4 0.8,-0.08 0,0 -0.32,0.83 0.64,0.81 -0.01,0.51 1.26,-0.26 0.85,-0.55 1.56,0.3 0.22,0.39 0.84,-0.27 0,0 -0.31,0.98 0.52,0.5 -0.58,0.57 0.08,0.47 -0.46,0.24 -1.46,2 -0.03,1.06 -1.28,1.93 -2.75,1.53 -0.43,1.23 0.16,2.32 0,0 -3.41,0.79 -3.43,1.23 -2.03,0.27 -0.26,-0.21 0.8,-1.71 0.49,0.05 0.25,0.57 2.36,-1.02 0.86,-0.53 -0.1,-0.44 0.45,-0.36 0.48,0.15 0.22,-0.19 0.21,-1.14 -0.57,-0.7 -1.69,-0.31 -0.52,0.46 -0.24,0.93 -0.81,-0.57 -2.13,0.25 -1.42,-1.37 0.31,-1.08 -0.44,-0.19 -0.42,0.59 -0.27,2.22 1.02,0.93 0.15,0.88 -1.69,-0.6 -0.77,-0.73 z","fukui":"m 238.25993,258.18889 1.16,0.72 0.07,0.38 0.31,-0.04 0.42,-0.26 -0.65,-0.81 0.2,-0.13 0.54,0.36 0.37,-0.65 -0.58,-0.45 -0.25,-0.84 0.59,0.15 0.43,0.69 0.76,-0.4 0.15,0.35 1.22,-0.36 0.23,-0.43 -0.25,-0.32 0.06,-0.95 -0.43,-0.68 1.24,-0.99 0.39,0.6 -0.23,1.43 0.36,0.54 0.6,-0.11 0.48,-1.52 0.02,-1.28 -0.57,-1.13 -1.52,-1.52 0.08,-1.1 -0.79,-1.19 1.06,-1.27 0.35,-1.49 2.1,-3.09 -0.24,-0.66 0.85,0 1.53,-1.09 0,0 1.68,1.59 0.25,1.25 0.41,0.38 0.9,-0.13 0.65,0.76 0.47,0.05 1.75,-0.42 1.86,1.46 0.24,0.62 1.89,-0.48 0,0 0.21,0.49 -0.49,0.37 -0.25,1.39 0.5,0.37 -0.05,0.53 0.79,0.28 -0.13,0.49 0.64,0.53 0.3,1.22 -0.63,0.46 -0.17,0.78 -1.34,-0.02 -1.13,0.49 -0.42,-0.52 -0.46,0.45 -0.52,-0.17 -0.49,0.44 -0.82,-0.21 -0.56,0.77 -0.3,-0.51 -1.06,0.02 -1.17,-0.42 -0.9,0.48 -0.01,0.97 -0.99,1.64 0,0 -1.81,-0.94 -0.67,0.13 -0.31,0.67 0.83,1.76 -0.13,0.75 -1.1,-0.32 -0.35,1.07 -1.29,0.13 -0.45,0.87 -0.46,0.1 -0.77,-0.77 -1.04,2.77 -0.57,0.28 -0.35,-0.4 -0.66,-0.01 -0.05,0.5 -0.37,0.1 -0.45,0.74 0,0 -1.37,0.26 -1.51,-0.59 -1.73,-0.19 -0.13,-0.87 -1.31,-1.21 0.29,-1 -0.52,-0.42 0.41,-0.9 0,0 0.88,0.17 -0.21,1.09 0.18,0.25 2.58,0.39 1.78,-0.38 0.27,-0.88 -0.65,0.27 -0.03,-0.5 -0.57,-0.11 0.52,-0.59 0.41,-0.08 z","gifu":"m 251.72993,266.75889 -0.72,-0.69 0.32,-0.21 0.02,-0.93 0.32,-0.52 0.04,-1.34 0.55,-0.44 -0.53,-0.85 0.09,-1 -0.63,-0.64 0.24,-0.89 -0.55,-0.71 -0.31,0.5 -0.78,-0.29 0.12,-1.6 -0.66,-0.07 -0.26,-1.07 0,0 0.98,-1.64 0.01,-0.97 0.9,-0.48 1.17,0.42 1.06,-0.01 0.3,0.51 0.56,-0.77 0.82,0.22 0.48,-0.44 0.52,0.17 0.46,-0.44 0.41,0.52 1.13,-0.49 1.35,0.02 0.17,-0.78 0.62,-0.46 -0.3,-1.22 -0.64,-0.52 0.12,-0.49 -0.79,-0.28 0.05,-0.53 -0.49,-0.37 0.24,-1.39 0.5,-0.37 -0.21,-0.49 0,0 0.5,-1.09 -0.23,-0.74 0.61,-0.23 0.94,-1.67 -0.04,-0.39 -0.76,-0.43 -0.25,-0.58 0,0 0.58,-0.08 0.29,-1.06 0.77,-0.56 0.25,0.59 0.35,-0.36 0.92,0.51 0.34,0.77 -0.26,0.73 0.34,0.08 1.39,-1.22 0.25,-1.15 2.08,-2.02 0.55,-0.02 0.25,0.44 1.46,-0.69 0.59,0.05 0.04,0.88 0.21,0.04 1.35,-0.8 0.28,0.78 1.13,0.35 0.71,-0.34 0.84,0.82 0.94,0.07 0,0 0.13,0.51 1.03,0.66 0.09,0.53 -0.09,0.78 -1.39,1.81 0.38,0.55 -0.05,0.52 -0.75,0.71 -0.01,0.81 0.46,0.5 0.72,0.25 -0.39,1.57 -1,0.76 -0.37,0.92 -0.44,0.1 -0.52,1.06 -0.42,0.07 -0.33,-0.33 -1.15,0.35 -0.35,1.06 -0.59,0.25 -0.11,0.54 0.29,0.39 1.04,0.01 0.05,0.51 1.23,0.37 0.8,1.79 0.78,0.7 -0.43,1.28 0.39,0.45 -0.07,1.1 0.31,0.55 1.07,-0.32 0.57,0.54 0,0.91 -0.65,0.7 0.71,0.98 -0.87,0.29 0.26,1.27 -0.84,0.65 0.01,0.53 0,0 -0.8,0.08 -1.72,1.4 -0.99,-0.49 0.02,-0.32 -0.84,-0.04 0.07,-0.24 -0.75,-0.48 -0.63,0.02 -0.92,0.73 -0.85,0.17 -0.52,-0.71 -0.94,-0.39 -0.3,0.21 -0.32,-0.15 -0.27,-0.32 0.09,-0.49 -0.49,-0.2 0.03,-0.65 -1.18,-0.87 0.02,-0.56 -1.49,1.12 -1.66,0.5 -1.27,-0.15 -1.69,2.98 -0.22,2.19 0,0 -1.08,-0.12 -1.69,-2.5 z","hyogo":"m 213.21993,277.54889 -1.09,0.9 -1.21,-0.22 0,0 -0.54,-1.37 -1.08,-0.96 -0.18,-0.47 0.7,-1.31 -0.68,-0.85 0.35,-0.32 0.15,-0.91 -0.2,-0.59 0.92,-0.54 0.06,-0.93 0.59,-0.25 0.24,-1.1 0.24,-0.26 0.67,0.07 0.08,-0.78 -0.63,-0.66 0.44,-0.8 0,0 0.58,0.26 1.64,-1.15 -0.26,-1.16 0.15,-0.43 -0.73,-0.96 0.09,-1.08 -0.73,-0.34 -0.49,-1.88 0.12,-1.02 -0.38,-0.77 -0.69,-0.52 0,0 2.13,-0.66 1.22,-0.74 1.2,0.31 0.42,0.47 0.82,-0.67 1.38,0.2 1.28,-0.29 0.45,0.33 0.98,-0.06 0,0 0.02,2.02 0.86,0.8 0.21,0.61 0.72,0.18 1.33,-0.66 0.32,0.54 0,2.63 -0.91,0.52 -1.14,-0.55 -0.37,1 0.02,1.27 1.49,0.61 1.32,1.13 0.76,-0.46 1.02,0.02 0.02,0.78 0.86,0.82 -0.25,0.55 0.55,0.24 0.43,-0.36 0.81,0.04 0.22,0.06 0.04,0.73 0.85,-0.18 0.97,0.49 0.29,1.26 -0.38,0.21 -0.17,0.54 0,0 -0.43,-0.05 -0.29,0.31 0.4,0.24 0.08,0.97 -0.24,0.36 1.4,0.81 0.96,0.14 -0.91,0.51 0.43,0.25 -0.47,2.04 0.74,1.24 0.15,1.43 -0.54,1.21 0,0 -0.44,-0.33 0.14,-0.47 -0.25,-0.52 -0.92,0.32 -0.42,-0.6 -0.97,-0.13 -1.98,0.94 -0.1,0.68 -2.58,0.64 -4.27,-1.72 -1.67,-1.65 -5.72,0.05 z m 9.4,11.08 0.22,0.77 -2.06,0.84 -0.98,0.82 -1.34,0.19 -0.01,-0.45 -0.59,-0.31 0.06,-0.5 -0.43,-0.16 -0.54,-1.01 0.67,-0.96 0.38,0.24 0.47,-0.24 1.33,-2.82 0.4,-0.46 0.41,0.01 0.95,-1.5 0.95,-0.43 0.77,-1.12 0.55,-0.29 0.44,0.83 -0.6,0.72 -0.15,0.77 -1.78,2.33 -0.01,1.54 0.89,1.19 z","kagawa":"m 199.67993,288.81889 2.14,-1.22 0.18,-0.96 2.08,0.7 1.61,0.07 1.07,-1.2 0.53,0.38 -0.19,0.96 0.18,0.37 0.36,0.06 0.13,-0.4 0.45,-0.09 1.11,0.23 -0.01,0.41 -0.39,0.31 0.19,0.48 1.13,0.26 0.82,0.63 0.39,-0.06 1.37,1.05 0,0 -0.16,0.96 -0.42,0.22 -1.09,-0.58 -0.28,0.3 -1.63,-0.26 -1.7,0.18 -0.74,0.58 0.06,0.42 -0.32,0.34 -1.24,0.14 -1.17,0.91 -0.47,0 -0.86,-0.97 -1.38,0.25 -0.76,0.29 -0.28,0.5 -0.58,-0.19 -1,0.84 -0.14,0.51 -0.62,0.22 0,0 -1.88,-0.74 0.69,-0.5 0.33,-3.08 -1.51,-1.21 0.07,-0.33 0.31,-0.09 1.59,0.8 0.55,-0.17 1.48,-1.32 z","kyoto":"m 231.14993,270.89889 0.17,-0.53 0.37,-0.21 -0.29,-1.26 -0.97,-0.49 -0.86,0.18 -0.04,-0.74 -0.22,-0.06 -0.81,-0.04 -0.42,0.36 -0.56,-0.24 0.25,-0.55 -0.86,-0.83 -0.02,-0.77 -1.02,-0.03 -0.77,0.47 -1.32,-1.14 -1.49,-0.61 -0.02,-1.26 0.37,-1 1.14,0.55 0.91,-0.52 0.01,-2.63 -0.33,-0.54 -1.33,0.66 -0.72,-0.18 -0.21,-0.61 -0.86,-0.8 -0.02,-2.02 0,0 0.26,0.3 0.97,-0.02 0.59,-0.3 0.45,-0.78 0.81,0.06 1.92,-1.35 1.89,-0.6 1.08,0.68 0.66,1.2 -1.07,1.01 -0.19,0.74 -1.09,1.32 0.06,0.6 0.3,-0.01 0.59,-0.97 0.61,0.34 0.13,0.17 -0.64,0.55 1.35,0.61 0.25,-0.33 0.14,1.38 0.48,-0.48 0.84,0.21 0.05,-0.51 -1.26,-0.79 0.85,-0.68 0.93,-0.11 0.15,-0.58 0.35,-0.01 0.01,0.57 0.41,0.25 0,0 -0.41,0.89 0.52,0.42 -0.29,1.01 1.31,1.21 0.13,0.87 1.73,0.19 1.5,0.59 1.37,-0.26 0,0 1.18,1.84 0.42,-0.01 -0.38,1.44 0.43,2.11 -0.31,1.74 -0.34,0.25 0.29,1.17 0.89,1.51 -0.24,1.07 0.71,0.47 0.73,-0.38 0.13,0.88 0.31,-0.05 0.3,0.37 0.4,-0.15 0.61,0.6 -0.26,0.26 0.15,0.41 0,0 0.45,1.2 0,0 -0.34,0.75 -0.58,-0.08 -0.49,-0.67 -0.99,-0.01 0.08,-0.36 -0.74,1.13 -0.73,0.08 -1.92,-0.52 -0.52,-1.22 0,0 0.28,-0.62 -1.02,-1.15 -0.31,-1.06 -1.24,-1.15 0,-0.62 -0.75,-0.02 -0.26,0.68 0.38,0.42 -0.79,0.26 -0.69,-0.73 -0.25,0.11 -0.07,-1.16 -2.16,-0.6 z","mie":"m 257.23993,288.86889 -0.19,0.13 0.66,-1.2 -0.57,-0.33 -0.66,1.41 -1.1,0.74 -0.37,0.05 -0.27,-0.79 -0.28,0.09 -0.23,0.84 -0.09,-0.69 -0.7,-0.01 0.28,0.94 -0.22,0.24 -2.95,0.72 -0.41,-0.11 -0.64,0.55 -0.55,1.01 0.35,0.61 0.42,-0.06 -0.35,0.69 -0.61,0.1 -0.37,-0.54 -0.41,0.11 0.18,0.32 -0.7,0.24 0.18,0.32 0.68,-0.1 0.01,0.68 0.72,0.37 -0.17,1.2 -0.66,0.09 -0.78,1.13 -0.94,0.18 -0.41,0.66 -0.61,-0.03 -1.06,1.88 -0.72,2 0,0 -1.29,-0.27 -1.7,-1.94 0.07,-1.92 0,0 1.1,-1.72 1.21,-0.39 0.83,-1.12 1.62,0.25 -0.14,-1.33 0.24,-0.27 0.12,-1.75 -0.37,-0.68 0.73,-1.36 -0.69,-1.15 0.67,-0.36 -1.16,-1.85 0.5,-0.95 2.18,-0.32 0.39,-0.94 -0.29,-0.96 -0.65,0.26 -0.46,-1.01 -0.82,0.27 -1.04,-0.51 -0.26,-0.41 0.44,-1 -0.05,-0.6 0.38,-0.52 -0.8,-1.57 0,0 -0.45,-1.21 0,0 1.34,-0.55 -0.07,-0.51 0.77,-0.63 -0.08,-0.25 -0.62,-0.05 -0.07,-0.25 0.47,-0.39 0.32,0.38 1.02,-0.02 1.34,0.66 2.33,-1.13 0.21,-0.92 0.79,-1.1 0.04,-1.38 0.73,-2.5 -0.71,-0.73 -0.08,-0.85 0,0 0,0 0,0 2.21,-0.95 1.7,2.49 1.08,0.12 0,0 0.32,1.21 0.97,1.57 0,0 -0.76,0.2 -0.92,0.69 -0.36,1.02 0.26,1.12 -1.93,2.95 -0.56,1.63 0.06,0.66 0.67,0.29 -0.38,1.33 2.1,0.61 0.28,0.68 1.28,0.47 1.08,0.81 1.18,0.03 0.22,0.65 0.56,0.13 -0.21,0.28 0.16,0.28 0.71,-0.13 0.28,0.29 0.08,0.73 -1.13,0.67 0.11,0.33 0.63,0.14 -0.63,0.71 0.29,0.47 -0.46,1.27 -0.97,0.27 -1.37,-0.47 1.08,-0.16 0.54,0.27 0.07,-0.65 -0.48,-0.12 -0.27,0.2 -1.46,-0.34 -0.53,0.36 z","nara":"m 244.43993,278.17889 0.8,1.57 -0.38,0.52 0.05,0.59 -0.43,1.01 0.26,0.41 1.03,0.5 0.82,-0.27 0.47,1.01 0.65,-0.27 0.29,0.96 -0.39,0.95 -2.18,0.32 -0.5,0.95 1.15,1.85 -0.66,0.36 0.69,1.16 -0.72,1.36 0.37,0.68 -0.13,1.75 -0.24,0.27 0.14,1.33 -1.62,-0.25 -0.82,1.11 -1.21,0.39 -1.1,1.72 0,0 -2.01,0.34 -0.66,-0.41 -0.66,-0.01 -1.15,0.68 -0.22,-0.57 -0.37,-0.13 0.71,-1.83 -0.28,-0.51 -0.58,-0.21 0.06,-0.52 -1.14,-0.96 0.12,-0.54 1.5,-1.45 0.38,-0.58 -0.01,-0.71 0.54,-0.27 0.81,0.37 0.39,-0.6 -0.21,-0.65 -0.89,-0.5 -0.2,-1.72 -0.4,-0.68 0,0 0.61,-0.37 0.19,-1.1 -0.08,-1.17 -0.53,-1.25 0.57,-0.9 -0.21,-0.45 -0.38,-0.07 0.51,-2.37 0.51,-0.44 0.16,-1.36 0.35,0.06 0,0 0.52,1.22 1.92,0.52 0.73,-0.08 0.74,-1.13 -0.08,0.36 0.99,0.01 0.49,0.67 0.58,0.08 z","okayama":"m 204.66993,282.20889 -1.41,1.09 -0.47,1.72 -1.96,-0.54 -0.52,0.34 -1.84,-0.34 -0.62,-0.78 -1.6,0.29 -0.27,0.31 0.24,0.22 -2.22,0.76 -0.69,-0.84 0,0 -0.12,-1.74 -1.21,-1.65 0.01,-1.38 -0.41,-1.9 0.29,-1.12 -1.6,-2 0.01,-1.6 0.46,-1.21 -1.01,-1.22 0,0 0.36,-0.25 0.24,-0.84 0.38,0.22 1.81,-0.63 -0.33,-1.19 0.27,-0.38 0.78,0.33 1.21,-0.49 0.21,-0.5 -0.21,-0.48 0.96,-0.25 0.78,-2.43 1.7,0.63 1.27,0.01 1.07,0.74 0.52,0.91 0.66,-0.5 0.2,-0.54 1.16,-0.49 0.03,-0.48 1.5,-0.43 -0.15,0.89 0.19,0.17 0.79,0.21 0.94,-0.17 0.69,0.59 0.22,0.42 -0.12,0.61 0.49,0.31 -0.19,0.71 0.51,0.63 1.48,-0.92 0.54,0.27 0.69,-0.13 1.39,-1.16 0.3,0.23 0,0 -0.44,0.8 0.63,0.66 -0.08,0.78 -0.67,-0.07 -0.24,0.26 -0.24,1.1 -0.59,0.25 -0.06,0.93 -0.92,0.54 0.2,0.59 -0.15,0.91 -0.35,0.32 0.68,0.85 -0.7,1.31 0.18,0.47 1.08,0.96 0.54,1.37 0,0 -0.5,0.33 -0.2,-0.28 -0.66,-0.01 -1.76,1.98 -0.37,0.89 -0.98,0.59 -1.28,0.06 -0.52,0.38 z m 5.26,2.84 -0.37,0.06 0.68,-0.71 -0.86,0.2 -0.67,1.29 -0.23,-0.59 0.37,-0.49 -0.11,-0.24 -0.5,-0.29 -1.17,0.5 -0.21,-0.25 0.45,-0.86 3.68,-1.35 -0.12,0.47 0.3,0.34 -0.4,2.25 -0.4,-0.52 -0.44,0.19 z","osaka":"m 232.13993,283.27889 0.37,-0.8 -0.64,-0.14 -0.03,-0.81 0.3,-0.51 0.74,-0.43 -0.46,-0.23 0,0 0.54,-1.21 -0.15,-1.43 -0.74,-1.24 0.47,-2.04 -0.43,-0.25 0.91,-0.51 -0.96,-0.14 -1.4,-0.81 0.24,-0.36 -0.08,-0.97 -0.4,-0.24 0.29,-0.31 0.43,0.05 0,0 0.19,0.74 2.16,0.6 0.07,1.16 0.25,-0.11 0.69,0.73 0.79,-0.26 -0.38,-0.42 0.26,-0.68 0.75,0.02 0,0.61 1.24,1.15 0.3,1.06 1.03,1.16 -0.29,0.62 0,0 -0.35,-0.06 -0.15,1.36 -0.51,0.44 -0.51,2.37 0.38,0.08 0.21,0.45 -0.57,0.9 0.53,1.26 0.08,1.16 -0.19,1.1 -0.61,0.37 0,0 -1.29,0.18 -1.2,0.8 -1.62,-0.14 -2.06,0.74 -1.63,0.09 -1.23,0.79 -1.04,0.18 -0.43,-0.04 -0.13,-0.88 -0.27,-0.09 0,0 2.57,-0.85 1.84,-1.68 0.97,-1.49 1.15,-1.04 z","shiga":"m 251.72993,266.75889 0.07,0.85 0.71,0.73 -0.73,2.5 -0.04,1.38 -0.78,1.1 -0.21,0.92 -2.34,1.13 -1.33,-0.66 -1.02,0.01 -0.33,-0.38 -0.47,0.39 0.07,0.26 0.62,0.04 0.08,0.26 -0.77,0.62 0.07,0.52 -1.34,0.55 0,0 -0.15,-0.41 0.26,-0.26 -0.61,-0.6 -0.4,0.15 -0.3,-0.37 -0.31,0.05 -0.13,-0.88 -0.73,0.38 -0.71,-0.47 0.24,-1.07 -0.89,-1.51 -0.29,-1.17 0.34,-0.25 0.31,-1.74 -0.43,-2.11 0.38,-1.44 -0.42,0.01 -1.18,-1.84 0,0 0.45,-0.74 0.37,-0.1 0.06,-0.5 0.65,0 0.35,0.4 0.57,-0.28 1.04,-2.76 0.77,0.77 0.46,-0.1 0.46,-0.88 1.29,-0.12 0.35,-1.07 1.1,0.32 0.14,-0.75 -0.83,-1.76 0.31,-0.67 0.67,-0.13 1.81,0.93 0,0 0.26,1.07 0.66,0.07 -0.12,1.6 0.78,0.29 0.31,-0.5 0.55,0.71 -0.24,0.89 0.63,0.64 -0.09,1 0.53,0.85 -0.55,0.44 -0.04,1.34 -0.32,0.52 -0.02,0.93 -0.32,0.21 z","tokushima":"m 218.38993,299.89889 -2.09,0.87 -0.89,0.77 -0.18,0.51 -1.25,0.91 -1.19,0.7 -0.92,0.19 -0.64,1.79 -0.89,-0.04 -0.21,0.47 0.26,0.14 -0.3,0.18 0,0 -2.11,-0.22 -0.78,-1.19 -0.1,-0.47 0.47,-0.54 -0.23,-0.8 -1.97,-0.05 -0.1,-2 -0.51,-1.26 -0.7,0.17 -0.25,-0.46 -0.39,0.13 -0.42,0.81 -0.61,0.2 -0.79,-0.32 -0.65,-0.9 -1.81,0.17 -1.34,-0.52 -0.37,-0.54 0,0 0.56,-0.9 0,-1.04 -0.27,-0.49 0.29,-0.68 0,0 0.62,-0.22 0.14,-0.51 1,-0.84 0.58,0.19 0.28,-0.5 0.76,-0.29 1.38,-0.25 0.86,0.97 0.47,0 1.17,-0.91 1.24,-0.14 0.32,-0.34 -0.06,-0.42 0.74,-0.58 1.7,-0.18 1.63,0.26 0.28,-0.3 1.09,0.58 0.42,-0.22 0.16,-0.96 0,0 2.81,-0.79 0,0.94 0.75,0.49 -0.72,2.96 0.09,1.1 0.48,0.53 0.36,-0.56 0.59,1.07 0.63,0.36 -0.52,0.39 0.7,0.19 -0.14,0.46 -1.29,0.94 -0.09,0.33 0.27,0.21 1.98,0.04 0.14,0.21 -0.44,0.2 z","tottori":"m 190.80993,260.73889 1.46,0.29 0.47,-0.16 0.47,-0.86 0.98,-0.5 1.8,-0.38 1.44,0.58 1.8,0.17 3.37,-0.23 0.67,-0.37 1.4,0.17 1.85,-0.2 2.78,-0.74 0.56,-0.77 0.76,-0.05 0.13,-0.39 0.61,-0.13 0,0 0.69,0.52 0.38,0.77 -0.12,1.02 0.49,1.88 0.73,0.34 -0.09,1.08 0.73,0.96 -0.15,0.43 0.26,1.16 -1.64,1.15 -0.58,-0.26 0,0 -0.3,-0.23 -1.39,1.16 -0.69,0.13 -0.54,-0.27 -1.48,0.92 -0.51,-0.63 0.19,-0.71 -0.49,-0.31 0.12,-0.61 -0.22,-0.42 -0.69,-0.59 -0.94,0.17 -0.79,-0.21 -0.19,-0.17 0.15,-0.89 -1.5,0.43 -0.03,0.48 -1.16,0.49 -0.2,0.54 -0.66,0.5 -0.52,-0.91 -1.07,-0.74 -1.27,-0.01 -1.7,-0.63 -0.78,2.43 -0.96,0.25 0.21,0.48 -0.21,0.5 -1.21,0.49 -0.78,-0.33 -0.27,0.38 0.33,1.19 -1.81,0.63 -0.38,-0.22 -0.24,0.84 -0.36,0.25 0,0 -0.42,-0.5 -2.1,0.32 0,-0.26 0,0 0.17,-1.54 0.89,-0.7 -0.23,-0.69 -0.61,-0.13 -0.02,-0.29 3.1,-1.38 -0.27,-1.63 0.42,-0.62 0.16,-2.44 z","wakayama":"m 240.04993,307.16889 -0.54,0.38 -0.32,0.69 0.09,0.71 -0.48,0.08 -0.25,-0.35 0.32,-0.75 -0.79,0.11 -1.88,-0.75 -2.35,-0.38 -2.02,-1.21 -0.41,-0.74 0.15,-0.79 -1.27,-0.63 0.98,-0.53 0.25,-0.57 -1.44,-1.22 -2.62,-1.21 -0.68,-1.41 -0.77,-0.38 -1.11,0.32 0.21,-2.33 1.57,-0.64 0.49,-0.63 -0.73,-0.76 -1.12,-0.25 0.61,-0.64 0.3,-0.83 0.87,0.07 0.3,-0.35 -0.13,-0.75 -0.75,-0.2 -0.43,-1.22 -1,-1.08 0.13,-0.48 0.36,-0.14 0,0 0.27,0.09 0.13,0.88 0.43,0.04 1.04,-0.18 1.23,-0.79 1.63,-0.09 2.06,-0.74 1.62,0.14 1.2,-0.8 1.29,-0.18 0,0 0.4,0.68 0.2,1.72 0.89,0.5 0.21,0.66 -0.39,0.6 -0.81,-0.37 -0.55,0.27 0.01,0.71 -0.38,0.57 -1.49,1.45 -0.13,0.54 1.14,0.96 -0.06,0.53 0.58,0.21 0.28,0.51 -0.71,1.83 0.38,0.13 0.21,0.57 1.15,-0.68 0.66,0.01 0.66,0.41 2.01,-0.34 0,0 -0.07,1.92 1.7,1.94 1.29,0.27 0,0 -0.33,0.45 -0.15,1.15 -0.96,0.26 -0.23,0.85 0.72,0.28 -0.07,0.35 -2.08,1.46 -0.52,0.09 z"};
var NS="http://www.w3.org/2000/svg",$=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return [].slice.call((r||document).querySelectorAll(s))};
var PC={"大阪":"#B97A62","京都":"#8A7495","兵庫":"#4F6681","奈良":"#6F8C68","滋賀":"#5F8F98","和歌山":"#C4925A"};
var PID={"大阪":"osaka","京都":"kyoto","兵庫":"hyogo","奈良":"nara","滋賀":"shiga","和歌山":"wakayama"};
var EN={"大阪":"OSAKA","京都":"KYOTO","兵庫":"HYOGO","奈良":"NARA","滋賀":"SHIGA","和歌山":"WAKAYAMA"};
// 府県名を置く位置（府県の形の中で、ピンとかぶりにくい所）
var LBL={"大阪":[.30,.62],"京都":[.42,.22],"兵庫":[.36,.30],"奈良":[.62,.62],"滋賀":[.50,.20],"和歌山":[.50,.62]};
var HOME=[200.5,251,60,60],BASE=60;
function X(lon){return 19.72*lon-2438.3}function Y(lat){return 255.75+(35.67-lat)*23.36}
var key=function(s){return String(s||"").replace(/\s+/g,"")};

// ---- 見た目 ----
var css=`
.tn{margin:0 0 18px}
.tn .hd{display:flex;justify-content:space-between;align-items:flex-end;margin:2px 0 10px}
.tn .hd .e{font-family:Jost,sans-serif;font-size:9.5px;letter-spacing:.36em;color:#A07E66}
.tn .hd .j{display:block;font-family:"Shippori Mincho",serif;font-weight:600;font-size:15px;letter-spacing:.1em;color:#2B2622;margin-top:4px}
.tn .hd .n{font-family:"Zen Kaku Gothic New",sans-serif;font-size:11px;color:#8C7B6E;letter-spacing:.06em}
.tn .hd .n b{font-family:Jost,sans-serif;font-weight:500;font-size:16px;color:#2B2622;margin:0 2px}
.tn .fr{position:relative;aspect-ratio:1/0.94;background:#FDFCFA;border:1px solid #E2D6CB;overflow:hidden;touch-action:manipulation}
.tn svg.m{position:absolute;inset:0;width:100%;height:100%;display:block}
.tn .mo{fill:#F4F0EA;stroke:#E6DDD2;stroke-width:1px;vector-effect:non-scaling-stroke}
.tn .mk{stroke:#2B2622;stroke-width:1.1px;vector-effect:non-scaling-stroke;stroke-linejoin:round;cursor:pointer;transition:fill .45s,stroke-opacity .45s}
.tn .mk.dim{stroke-opacity:.35}
.tn .lb{position:absolute;transform:translate(-50%,-50%);font-family:"Shippori Mincho",serif;font-weight:600;font-size:12px;letter-spacing:.18em;pointer-events:none;white-space:nowrap;text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 6px #fff;transition:opacity .3s}
.tn .lb small{display:block;font-family:Jost,sans-serif;font-weight:400;font-size:8px;letter-spacing:.3em;text-align:center;margin-top:1px;opacity:.8}
.tn .pin{cursor:pointer}
.tn .pin .sh{fill:rgba(43,38,34,.20)}
.tn .pin .hit{fill:transparent}
.tn .pin .dot{stroke:#fff;stroke-width:1.6px;vector-effect:non-scaling-stroke}
.tn .pin.soon .dot{fill:#fff!important;stroke-width:1.8px;stroke-dasharray:2.2 1.6}
.tn .pin .rg{fill:none;stroke-width:1.2px;vector-effect:non-scaling-stroke;opacity:0;transform-box:fill-box;transform-origin:center}
.tn .pin.sel .rg{animation:tnrp 1.8s ease-out infinite}
@keyframes tnrp{0%{opacity:.75;transform:scale(1)}100%{opacity:0;transform:scale(3.4)}}
.tn .pin .dw{transform-box:fill-box;transform-origin:center bottom}
.tn .cn{position:absolute;top:9px;font-family:Jost,sans-serif;font-size:8.5px;letter-spacing:.32em;color:#A39A90;pointer-events:none}
.tn .cn.a{left:11px}.tn .cn.b{right:11px;transition:color .3s}
.tn .bk{position:absolute;left:8px;bottom:8px;z-index:3;font-family:"Zen Kaku Gothic New",sans-serif;font-size:11px;letter-spacing:.06em;color:#2B2622;background:#fff;border:1px solid #CFC5BA;padding:5px 10px;cursor:pointer;opacity:0;pointer-events:none;transition:opacity .3s}
.tn .bk.on{opacity:1;pointer-events:auto}
.tn .cr{position:absolute;right:8px;bottom:5px;font-size:8px;color:#B3AAA1;pointer-events:none}
.tn .pop{position:relative;background:#fff;border:1px solid #E2D6CB;border-top:0;border-left:3px solid var(--pc,#2B2622);max-height:0;overflow:hidden;opacity:0;transition:max-height .38s cubic-bezier(.2,.8,.2,1),opacity .25s}
.tn .pop.on{max-height:420px;opacity:1;overflow:auto}
.tn .pop:before{content:"";position:absolute;left:0;right:0;top:0;height:2px;background:var(--pc,#2B2622);opacity:.25}
.tn .pop .x{position:absolute;right:4px;top:2px;width:34px;height:34px;background:none;border:0;font-family:Jost,sans-serif;font-size:18px;color:#8C7B6E;cursor:pointer}
.tn .pop .gh{font-family:Jost,sans-serif;font-size:9px;letter-spacing:.3em;color:#A07E66;padding:12px 14px 0}
.tn .pi{padding:12px 44px 12px 14px;border-bottom:1px solid #F0EAE3}
.tn .pi:last-child{border-bottom:0}
.tn .pi .d{font-size:11px;color:#8C7B6E;letter-spacing:.04em}
.tn .pi .d i{font-style:normal;font-weight:700;margin-right:6px}
.tn .pi .d u{text-decoration:none;font-size:9.5px;border:1px solid currentColor;padding:0 4px;margin-left:6px}
.tn .pi .t{font-family:"Shippori Mincho",serif;font-weight:600;font-size:15px;line-height:1.45;color:#2B2622;margin:3px 0 0}
.tn .pi .ac{display:flex;flex-wrap:wrap;gap:4px 18px;margin-top:8px}
.tn .pi .ac a{white-space:nowrap;display:inline-block;font-size:11.5px;letter-spacing:.08em;color:#2B2622;text-decoration:underline;text-decoration-color:#CFC5BA;text-underline-offset:4px;padding:4px 0}
.tn .pi.mini{cursor:pointer;padding:10px 44px 10px 14px}
.tn .pi.mini .t{font-size:13.5px}
.tn .lg{display:flex;justify-content:center;gap:14px;margin:8px 0 0;font-size:10px;color:#9C9187;letter-spacing:.06em}
.tn .lg span:before{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;background:#9C9187;margin-right:5px;vertical-align:0}
.tn .lg span.s:before{background:#fff;border:1px dashed #9C9187;width:6px;height:6px}
.it.tnf .card{box-shadow:0 0 0 2px var(--pc,#2B2622)!important;transition:box-shadow .3s}
`;
var st=document.createElement("style");st.textContent=css;document.head.appendChild(st);

// ---- 地図を作る ----
var box=document.createElement("div");box.className="tn";
box.innerHTML='<div class="hd"><div><span class="e">MAP</span><span class="j">地図で見る</span></div><div class="n" id="tnn"></div></div>'+
 '<div class="fr"><svg class="m" viewBox="'+HOME.join(" ")+'" preserveAspectRatio="xMidYMid slice"><g class="base"></g><g class="pins"></g></svg><div class="lbs"></div>'+
 '<span class="cn a">KANSAI</span><span class="cn b">ALL</span><button class="bk" type="button">← 関西全体</button><span class="cr">地図：mapsvg.com（CC BY 4.0）</span>'+
 '</div><div class="pop" role="dialog"><button class="x" type="button" aria-label="閉じる">×</button><div class="pb"></div></div>'+
 '<div class="lg" style="display:none"><span>開催・オープン</span><span class="s">これからできる</span></div>';
var svg=$("svg.m",box),base=$(".base",svg),pins=$(".pins",svg),lbs=$(".lbs",box),pop=$(".pop",box),bk=$(".bk",box),cnb=$(".cn.b",box);
Object.keys(PATHS).forEach(function(k){if(Object.values(PID).indexOf(k)<0){var p=document.createElementNS(NS,"path");p.setAttribute("class","mo");p.setAttribute("d",PATHS[k]);base.appendChild(p);}});
Object.keys(PID).forEach(function(pf){var p=document.createElementNS(NS,"path");p.setAttribute("class","mk");p.id="tn_"+PID[pf];p.setAttribute("d",PATHS[PID[pf]]);p.dataset.pref=pf;
 p.addEventListener("click",function(){pickPref(pf)});base.appendChild(p);
 var l=document.createElement("div");l.className="lb";l.dataset.pref=pf;l.style.color=PC[pf];l.innerHTML=pf+"<small>"+EN[pf]+"</small>";lbs.appendChild(l);});

// ---- 今のページの状態を読む ----
function curPref(){var b=$("#flt button.on");return b&&b.textContent!=="すべて"?b.textContent:""}
function curBlk(){return $(".paper .blk.tb:not(.toff)")||$(".paper .blk.b-now")}
function curTab(){var b=$(".tabs button.on b");return b?b.childNodes[0].textContent:"開催中"}
var GEO={};
function items(){var blk=curBlk();if(!blk)return[];var seen={},out=[],soon=blk.classList.contains("b-new");
 $$(".it",blk).forEach(function(w){if(w.style.display==="none")return;var a=$(".card",w);if(!a)return;var tt=$(".t",a),k=key(tt&&tt.textContent);if(!k||seen[k])return;seen[k]=1;
  var g=GEO[k];var d=$(".d",a),dt="",tags=[];if(d)[].forEach.call(d.childNodes,function(n){if(n.nodeType===3)dt+=n.textContent;else if(n.classList&&n.classList.contains("tg"))tags.push(n.textContent)});
  var mp=$(".mp",w);out.push({w:w,a:a,k:k,t:$$(".nwp",tt).map(function(s){return s.textContent}).join(" ")||tt.textContent,pref:w.getAttribute("data-pref")||"",d:dt.replace(/^\s*[｜|]\s*/,"").trim(),tags:tags,href:a.getAttribute("href"),map:mp?mp.href:"",lat:g&&g[0],lon:g&&g[1],soon:soon});});
 return out}

// ---- 表示する範囲 ----
var vb=HOME.slice(),anim=0;
function target(pf){if(!pf)return HOME;var bb=$("#tn_"+PID[pf]).getBBox(),s=Math.max(bb.width,bb.height/0.94)*1.16;return [bb.x+bb.width/2-s/2,bb.y+bb.height/2-s*0.94/2,s,s*0.94]}
function fly(to){var from=vb.slice(),t0=performance.now(),D=matchMedia("(prefers-reduced-motion: reduce)").matches?1:720;cancelAnimationFrame(anim);
 (function f(n){var k=Math.min(1,(n-t0)/D),e=k<.5?4*k*k*k:1-Math.pow(-2*k+2,3)/2;vb=from.map(function(v,i){return v+(to[i]-v)*e});place();if(k<1)anim=requestAnimationFrame(f);else labels()})(t0)}
function place(){svg.setAttribute("viewBox",vb.join(" "));var r=vb[2]/BASE;$$(".pin",pins).forEach(function(g){g.setAttribute("transform","translate("+g.dataset.x+" "+g.dataset.y+") scale("+r+")")});labels()}
function labels(){var m=svg.getScreenCTM(),fr=$(".fr",box).getBoundingClientRect(),pf=curPref();if(!m)return;
 $$(".lb",lbs).forEach(function(l){var p=l.dataset.pref,bb=$("#tn_"+PID[p]).getBBox(),pt=svg.createSVGPoint(),o=LBL[p];pt.x=bb.x+bb.width*o[0];pt.y=bb.y+bb.height*o[1];var q=pt.matrixTransform(m);
  l.style.left=(q.x-fr.left)+"px";l.style.top=(q.y-fr.top)+"px";l.style.opacity=pf?0:1;});}

// ---- ピン ----
var list=[],sel=null,lastSig="";
function draw(drop){list=items();var pf=curPref(),tab=curTab();pins.innerHTML="";var n=0,shown=0;
 list.slice().sort(function(a,b){return (b.lat||0)-(a.lat||0)}).forEach(function(it){if(it.lat==null)return;shown++;
  var g=document.createElementNS(NS,"g");g.setAttribute("class","pin"+(it.soon?" soon":"")+(sel&&sel.k===it.k?" sel":""));g.dataset.x=X(it.lon);g.dataset.y=Y(it.lat);g.dataset.k=it.k;
  var c=PC[it.pref]||"#2B2622";
  g.innerHTML='<ellipse class="sh" cx="0" cy=".55" rx=".75" ry=".24"/><circle class="rg" r=".8" stroke="'+c+'"/><g class="dw"><circle class="dot" r=".8" fill="'+c+'" stroke="'+(it.soon?c:"#fff")+'"/></g><circle class="hit" r="1.9"/>';
  g.addEventListener("click",function(e){e.stopPropagation();openPin(it)});pins.appendChild(g);
  if(drop&&!matchMedia("(prefers-reduced-motion: reduce)").matches){var dw=$(".dw",g),dl=Math.min(n++*22,560);
   dw.animate([{transform:"translateY(-5px)",opacity:0},{transform:"translateY(0)",opacity:1,offset:.62},{transform:"translateY(-.7px) scaleY(.92)",offset:.8},{transform:"none",opacity:1}],{duration:480,delay:dl,easing:"ease-out",fill:"backwards"});}});
 $("#tnn",box).innerHTML=(pf||"関西")+"の"+tab+"<b>"+shown+"</b>か所";
 $(".lg",box).style.display=tab==="もうすぐ"?"flex":"none";
 $$(".mk",base).forEach(function(p){var on=p.dataset.pref===pf;p.style.fill=hexA(PC[p.dataset.pref],pf?(on?.13:.03):.07);p.classList.toggle("dim",!!pf&&!on)});
 cnb.textContent=pf?EN[pf]:"ALL";cnb.style.color=pf?PC[pf]:"";bk.classList.toggle("on",!!pf);
 place()}
function hexA(h,a){var n=parseInt(h.slice(1),16);return "rgba("+(n>>16)+","+(n>>8&255)+","+(n&255)+","+a+")"}

// ---- ピンを押したとき：近くのピンもまとめて出す ----
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function row(it,full){var c=PC[it.pref]||"#2B2622";
 var h='<div class="d"><i style="color:'+c+'">● '+esc(it.pref)+'</i>'+esc(it.d)+it.tags.map(function(t){return '<u style="color:#5E8A4A">'+esc(t)+'</u>'}).join("")+'</div><div class="t">'+esc(it.t)+'</div>';
 if(full)h+='<div class="ac"><a href="'+esc(it.href)+'" target="_blank" rel="noopener" data-k="地図ピン｜'+esc(it.t)+'">くわしく見る →</a>'+(it.map?'<a href="'+esc(it.map)+'" target="_blank" rel="noopener" data-k="地図ピン地図｜'+esc(it.t)+'">行き方 ↗</a>':'')+'<a href="#" class="go2">リストで見る ↓</a></div>';
 return h}
function openPin(it){sel=it;var r=vb[2]/BASE*1.5,near=list.filter(function(o){return o.lat!=null&&Math.hypot(X(o.lon)-X(it.lon),Y(o.lat)-Y(it.lat))<r});
 near.sort(function(a,b){return a===it?-1:b===it?1:0});var pb=$(".pb",pop);pop.style.setProperty("--pc",PC[it.pref]||"#2B2622");
 if(near.length>1){pb.innerHTML='<div class="gh">この辺りに '+near.length+' 件</div>'+near.map(function(o,i){return '<div class="pi'+(i?" mini":"")+'" data-i="'+i+'">'+row(o,!i)+'</div>'}).join("");
  $$(".pi.mini",pb).forEach(function(e){e.addEventListener("click",function(){openPin(near[+e.dataset.i])})});}
 else pb.innerHTML='<div class="pi">'+row(it,true)+'</div>';
 var g2=$(".go2",pb);if(g2)g2.addEventListener("click",function(e){e.preventDefault();toList(it)});
 pop.classList.add("on");$$(".pin",pins).forEach(function(g){g.classList.toggle("sel",g.dataset.k===it.k)});}
function closePop(){pop.classList.remove("on");sel=null;$$(".pin.sel",pins).forEach(function(g){g.classList.remove("sel")})}
$(".x",pop).addEventListener("click",closePop);
svg.addEventListener("click",function(e){if(!e.target.closest(".pin")&&!e.target.closest(".mk"))closePop()});
function toList(it){var w=it.w;if(w.classList.contains("cap")){var m=$(".cmore",w.parentNode);if(m)m.click();}
 w.classList.add("tnf");w.style.setProperty("--pc",PC[it.pref]||"#2B2622");w.scrollIntoView({behavior:"smooth",block:"center"});setTimeout(function(){w.classList.remove("tnf")},2200)}

// ---- 府県を押す＝上の府県ボタンを押すのと同じ ----
function pickPref(pf){var b=$$("#flt button").filter(function(x){return x.textContent===(pf||"すべて")})[0];if(b)b.click();}
bk.addEventListener("click",function(){pickPref("")});

// ---- 地図をタブの下に置く。タブ・府県が変わったら描き直す ----
function mount(){var bar=$(".tabs");if(bar&&bar.nextSibling!==box)bar.parentNode.insertBefore(box,bar.nextSibling);}
function sync(){mount();var pf=curPref(),sig=pf+"|"+curTab();if(sig===lastSig)return;var pfChanged=lastSig.split("|")[0]!==pf||!lastSig;lastSig=sig;closePop();draw(true);if(pfChanged)fly(target(pf));}
document.addEventListener("click",function(e){if(e.target.closest("#flt,.tabs,.dflt"))setTimeout(sync,90)});
addEventListener("resize",labels);
fetch("/townnotes/geo.json",{cache:"no-store"}).then(function(r){return r.json()}).catch(function(){return{}}).then(function(g){Object.keys(g).forEach(function(k){if(g[k][0]!=null)GEO[key(k)]=g[k]});mount();lastSig="";sync();});
})();
