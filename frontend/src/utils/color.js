/**
 * Color conversion utilities for Hue lights.
 *
 * Hue uses CIE 1931 xy color space.
 * We convert between RGB/HSV and CIE xy.
 */

// ===== HSV <-> RGB =====

/**
 * HSV to RGB.
 * @param {number} h Hue 0-360
 * @param {number} s Saturation 0-1
 * @param {number} v Value 0-1
 * @returns {[number, number, number]} [r, g, b] each 0-255
 */
export function hsvToRgb(h, s, v) {
  h = ((h % 360) + 360) % 360;
  const c = v * s;
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
  const m = v - c;
  let r, g, b;

  if (h < 60) { r = c; g = x; b = 0; }
  else if (h < 120) { r = x; g = c; b = 0; }
  else if (h < 180) { r = 0; g = c; b = x; }
  else if (h < 240) { r = 0; g = x; b = c; }
  else if (h < 300) { r = x; g = 0; b = c; }
  else { r = c; g = 0; b = x; }

  return [
    Math.round((r + m) * 255),
    Math.round((g + m) * 255),
    Math.round((b + m) * 255),
  ];
}

/**
 * RGB to HSV.
 * @param {number} r 0-255
 * @param {number} g 0-255
 * @param {number} b 0-255
 * @returns {{ h: number, s: number, v: number }}
 */
export function rgbToHsv(r, g, b) {
  r /= 255; g /= 255; b /= 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const d = max - min;
  let h = 0;

  if (d !== 0) {
    if (max === r) h = 60 * (((g - b) / d) % 6);
    else if (max === g) h = 60 * ((b - r) / d + 2);
    else h = 60 * ((r - g) / d + 4);
  }
  if (h < 0) h += 360;

  return {
    h,
    s: max === 0 ? 0 : d / max,
    v: max,
  };
}

// ===== RGB <-> Hex =====

export function rgbToHex(r, g, b) {
  return '#' + [r, g, b].map((c) => c.toString(16).padStart(2, '0')).join('');
}

export function hexToRgb(hex) {
  hex = hex.replace('#', '');
  return {
    r: parseInt(hex.slice(0, 2), 16),
    g: parseInt(hex.slice(2, 4), 16),
    b: parseInt(hex.slice(4, 6), 16),
  };
}

// ===== RGB <-> CIE xy =====

/**
 * RGB to CIE xy color space.
 * Uses Wide RGB D65 conversion formula from Philips.
 */
export function rgbToXy(r, g, b) {
  // Normalize to 0-1
  r /= 255; g /= 255; b /= 255;

  // Gamma correction
  r = r > 0.04045 ? Math.pow((r + 0.055) / 1.055, 2.4) : r / 12.92;
  g = g > 0.04045 ? Math.pow((g + 0.055) / 1.055, 2.4) : g / 12.92;
  b = b > 0.04045 ? Math.pow((b + 0.055) / 1.055, 2.4) : b / 12.92;

  // Wide gamut D65 conversion
  const X = r * 0.664511 + g * 0.154324 + b * 0.162028;
  const Y = r * 0.283881 + g * 0.668433 + b * 0.047685;
  const Z = r * 0.000088 + g * 0.072310 + b * 0.986039;

  const sum = X + Y + Z;
  if (sum === 0) return { x: 0.3127, y: 0.3290 }; // D65 white point

  return { x: X / sum, y: Y / sum };
}

/**
 * CIE xy + brightness to RGB.
 */
export function xyToRgb(x, y, brightness = 1.0) {
  if (y === 0) return { r: 0, g: 0, b: 0 };

  const z = 1.0 - x - y;
  const Y = brightness;
  const X = (Y / y) * x;
  const Z = (Y / y) * z;

  // Reverse wide gamut D65 conversion
  let r = X * 1.656492 - Y * 0.354851 - Z * 0.255038;
  let g = -X * 0.707196 + Y * 1.655397 + Z * 0.036152;
  let b = X * 0.051713 - Y * 0.121364 + Z * 1.011530;

  // Clamp
  const maxVal = Math.max(r, g, b, 1);
  r /= maxVal; g /= maxVal; b /= maxVal;

  // Gamma correction
  r = r <= 0.0031308 ? 12.92 * r : 1.055 * Math.pow(r, 1.0 / 2.4) - 0.055;
  g = g <= 0.0031308 ? 12.92 * g : 1.055 * Math.pow(g, 1.0 / 2.4) - 0.055;
  b = b <= 0.0031308 ? 12.92 * b : 1.055 * Math.pow(b, 1.0 / 2.4) - 0.055;

  return {
    r: Math.max(0, Math.min(255, Math.round(r * 255))),
    g: Math.max(0, Math.min(255, Math.round(g * 255))),
    b: Math.max(0, Math.min(255, Math.round(b * 255))),
  };
}

// ===== Gamut Clipping =====

/**
 * Clip a CIE xy point to a color gamut triangle.
 * Gamut: { red: {x, y}, green: {x, y}, blue: {x, y} }
 */
export function clipToGamut(x, y, gamut) {
  if (!gamut || !gamut.red) return { x, y };

  const r = gamut.red;
  const g = gamut.green;
  const b = gamut.blue;

  if (isInsideTriangle(x, y, r, g, b)) {
    return { x, y };
  }

  // Find closest point on triangle edges
  const pAB = closestPointOnLine(x, y, r, g);
  const pBC = closestPointOnLine(x, y, g, b);
  const pCA = closestPointOnLine(x, y, b, r);

  const dAB = distance(x, y, pAB.x, pAB.y);
  const dBC = distance(x, y, pBC.x, pBC.y);
  const dCA = distance(x, y, pCA.x, pCA.y);

  if (dAB <= dBC && dAB <= dCA) return pAB;
  if (dBC <= dCA) return pBC;
  return pCA;
}

function isInsideTriangle(px, py, a, b, c) {
  const d1 = sign(px, py, a.x, a.y, b.x, b.y);
  const d2 = sign(px, py, b.x, b.y, c.x, c.y);
  const d3 = sign(px, py, c.x, c.y, a.x, a.y);

  const hasNeg = d1 < 0 || d2 < 0 || d3 < 0;
  const hasPos = d1 > 0 || d2 > 0 || d3 > 0;

  return !(hasNeg && hasPos);
}

function sign(x1, y1, x2, y2, x3, y3) {
  return (x1 - x3) * (y2 - y3) - (x2 - x3) * (y1 - y3);
}

function closestPointOnLine(px, py, a, b) {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const t = Math.max(0, Math.min(1,
    ((px - a.x) * dx + (py - a.y) * dy) / (dx * dx + dy * dy)
  ));
  return { x: a.x + t * dx, y: a.y + t * dy };
}

function distance(x1, y1, x2, y2) {
  return Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
}

// ===== Convenience =====

/**
 * Convert HSV wheel position to CIE xy (for sending to Hue).
 */
export function hsvToXy(h, s, v) {
  const [r, g, b] = hsvToRgb(h, s, v);
  return rgbToXy(r, g, b);
}

/**
 * Convert CIE xy to HSV (for positioning on color wheel).
 */
export function xyToHsv(x, y, brightness) {
  const { r, g, b } = xyToRgb(x, y, brightness || 1.0);
  return rgbToHsv(r, g, b);
}

/**
 * Get a CSS color string from CIE xy + brightness.
 */
export function xyToCss(x, y, brightness) {
  const { r, g, b } = xyToRgb(x, y, brightness || 1.0);
  return `rgb(${r}, ${g}, ${b})`;
}

/**
 * Draw a color wheel on a canvas.
 */
export function drawColorWheel(canvas, size) {
  const ctx = canvas.getContext('2d');
  const imageData = ctx.createImageData(size, size);
  const data = imageData.data;
  const cx = size / 2;
  const cy = size / 2;
  const radius = size / 2 - 2;

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const dx = x - cx;
      const dy = y - cy;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist <= radius) {
        const angle = Math.atan2(dy, dx);
        const hue = ((angle * 180) / Math.PI + 360) % 360;
        const saturation = dist / radius;
        const [r, g, b] = hsvToRgb(hue, saturation, 1);
        const idx = (y * size + x) * 4;
        data[idx] = r;
        data[idx + 1] = g;
        data[idx + 2] = b;
        data[idx + 3] = 255;
      }
    }
  }

  ctx.putImageData(imageData, 0, 0);
}
