/**
 * Telegram Gift backdrop color map.
 * Extracted from Telegram's gift attribute system.
 * Each backdrop has center_color and edge_color (as integer RGB values).
 */

interface BackdropColor {
  center: number
  edge: number
}

const BACKDROP_COLORS: Record<string, BackdropColor> = {
  'Gunmetal': { center: 5004643, edge: 3095362 },
  'Electric Indigo': { center: 11108595, edge: 5989080 },
  'Ranger Green': { center: 6256713, edge: 3952443 },
  'Lemongrass': { center: 11450458, edge: 5608261 },
  'Lavender': { center: 12028388, edge: 9067196 },
  'Hunter Green': { center: 9416312, edge: 4948571 },
  'Khaki Green': { center: 11382896, edge: 7044436 },
  'Raspberry': { center: 14711685, edge: 11950464 },
  'Cyberpunk': { center: 8753139, edge: 8806355 },
  'Pacific Green': { center: 7325587, edge: 3906692 },
  'Sky Blue': { center: 5813448, edge: 5475266 },
  'Roman Silver': { center: 10725557, edge: 8159370 },
  'Pine Green': { center: 7055740, edge: 4094320 },
  'Coral Red': { center: 14322027, edge: 12870991 },
  'French Violet': { center: 12738790, edge: 9522905 },
  'Electric Purple': { center: 13267142, edge: 9855700 },
  'Pacific Cyan': { center: 5947046, edge: 4036026 },
  'Pure Gold': { center: 13413185, edge: 9993010 },
  'Copper': { center: 13665878, edge: 10315057 },
  'Mustard': { center: 13932557, edge: 12875538 },
  'Onyx Black': { center: 5067348, edge: 3225144 },
  'English Violet': { center: 11634363, edge: 8870545 },
  'Battleship Grey': { center: 9211013, edge: 7105638 },
  'Light Olive': { center: 12758884, edge: 8945221 },
  'Cappuccino': { center: 11636862, edge: 8151894 },
  'Platinum': { center: 11710119, edge: 8946814 },
  'Rosewood': { center: 12024439, edge: 8473682 },
  'Navy Blue': { center: 7118557, edge: 6057673 },
  'Tomato': { center: 15104318, edge: 13913663 },
  'Steel Grey': { center: 9937580, edge: 6517372 },
  'Midnight Blue': { center: 6056325, edge: 3489879 },
  'Mint Green': { center: 8309634, edge: 4562522 },
  'Chocolate': { center: 10776152, edge: 7619643 },
  'Emerald': { center: 7914885, edge: 4366705 },
  'Cobalt Blue': { center: 6326479, edge: 5333688 },
  'Desert Sand': { center: 11771778, edge: 8287067 },
  'Persimmon': { center: 15181658, edge: 12937055 },
  'Mexican Pink': { center: 14902930, edge: 13191548 },
  'Strawberry': { center: 14519919, edge: 12016224 },
  'Sapphire': { center: 5809096, edge: 5470658 },
  'Turquoise': { center: 6209720, edge: 4035214 },
  'Carrot Juice': { center: 14391399, edge: 13070159 },
  'French Blue': { center: 6069188, edge: 3634074 },
  'Fandango': { center: 14846646, edge: 10770571 },
  'Carmine': { center: 14702410, edge: 11024443 },
  'Burnt Sienna': { center: 14053180, edge: 11881261 },
  'Feldgrau': { center: 9015944, edge: 6187875 },
  'Jade Green': { center: 5620892, edge: 3905911 },
  'Moonstone': { center: 8303028, edge: 5800848 },
  'Pistachio': { center: 9941116, edge: 6062412 },
  'Rifle Green': { center: 6580572, edge: 4936257 },
  'Amber': { center: 14332741, edge: 11632682 },
  'Satin Gold': { center: 12557127, edge: 9271097 },
  'Azure Blue': { center: 6140363, edge: 4492203 },
  'Tactical Pine': { center: 4489835, edge: 3105641 },
  'Fire Engine': { center: 15753039, edge: 12859721 },
  'Indigo Dye': { center: 5470609, edge: 4285561 },
  'Grape': { center: 10319041, edge: 7949728 },
  'Black': { center: 3553080, edge: 921359 },
  'Burgundy': { center: 10706534, edge: 7160138 },
  'Shamrock Green': { center: 9089379, edge: 5608261 },
  'Mystic Pearl': { center: 13667181, edge: 11556720 },
  'Dark Lilac': { center: 11632037, edge: 9197434 },
  'Chestnut': { center: 12480340, edge: 10045496 },
  'Malachite': { center: 9811031, edge: 4036437 },
  'Aquamarine': { center: 6336917, edge: 4631476 },
  'Ivory White': { center: 12236465, edge: 10591639 },
  'Old Gold': { center: 11898168, edge: 9726245 },
  'Gunship Green': { center: 5605989, edge: 4023895 },
  'Deep Cyan': { center: 3257770, edge: 1611161 },
  'Seal Brown': { center: 6704453, edge: 4666926 },
  'Camo Green': { center: 7705677, edge: 5534529 },
  'Orange': { center: 13736506, edge: 12611399 },
  'Celtic Blue': { center: 4569325, edge: 3704537 },
  'Purple': { center: 11431086, edge: 8669060 },
  'Neon Blue': { center: 7706361, edge: 6841060 },
  'Dark Green': { center: 5333825, edge: 2835759 },
  'Marine Blue': { center: 5138588, edge: 3885946 },
  'Caramel': { center: 13670706, edge: 12022833 },
  'Silver Blue': { center: 8430776, edge: 6323345 },
}

function intToHex(n: number): string {
  return '#' + (n & 0xFFFFFF).toString(16).padStart(6, '0')
}

/**
 * Get CSS gradient for a gift backdrop name.
 * Returns a linear-gradient string for use in CSS background.
 */
export function getBackdropGradient(backdropName: string | undefined | null): string {
  if (!backdropName) return 'linear-gradient(180deg, #3A3A3A 0%, #282727 100%)'

  const colors = BACKDROP_COLORS[backdropName]
  if (colors) {
    return `linear-gradient(180deg, ${intToHex(colors.center)} 0%, ${intToHex(colors.edge)} 100%)`
  }

  // Fallback: deterministic color from name hash
  let h = 0
  for (let i = 0; i < backdropName.length; i++) {
    h = ((h << 5) - h + backdropName.charCodeAt(i)) | 0
  }
  const hue = Math.abs(h) % 360
  return `linear-gradient(180deg, hsl(${hue}, 25%, 28%) 0%, hsl(${hue}, 30%, 18%) 100%)`
}

export default BACKDROP_COLORS
