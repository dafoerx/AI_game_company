'use strict';

/** 内部工具：去掉小数末尾多余的 0 */
function _trimZero(str) {
  return String(str).replace(/\.?0+$/, '');
}

/** 内部工具：将文本数字（支持 K/M）还原为真实数值 */
function _parseDisplayNumber(text) {
  const raw = String(text == null ? '' : text).trim().toUpperCase().replace(/,/g, '');
  const match = raw.match(/^(-?\d+(?:\.\d+)?)([KMB])?$/);
  if (match) {
    let value = parseFloat(match[1]);
    const unit = match[2];
    if (unit === 'K') value *= 1e3;
    if (unit === 'M') value *= 1e6;
    if (unit === 'B') value *= 1e9;
    return Number.isFinite(value) ? value : 0;
  }
  const fallback = parseFloat(raw.replace(/[^\d.-]/g, ''));
  return Number.isFinite(fallback) ? fallback : 0;
}

/** 内部工具：注入粒子和浮动文字所需样式（仅注入一次） */
function _ensureUtilsEffectStyle() {
  if (typeof document === 'undefined') return;
  if (document.getElementById('hotpot-utils-effects-style')) return;

  const style = document.createElement('style');
  style.id = 'hotpot-utils-effects-style';
  style.textContent = `
    .utils-particle {
      position: absolute;
      left: 0;
      top: 0;
      pointer-events: none;
      user-select: none;
      z-index: 9998;
      will-change: transform, opacity;
      filter: drop-shadow(0 2px 6px rgba(0,0,0,.25));
      transform: translate3d(0,0,0);
    }

    .utils-floating-text {
      position: fixed;
      left: 0;
      top: 0;
      transform: translate(-50%, -50%);
      pointer-events: none;
      user-select: none;
      white-space: nowrap;
      z-index: 10000;
      font-weight: 900;
      letter-spacing: .5px;
      text-shadow:
        0 2px 0 rgba(0,0,0,.18),
        0 6px 14px rgba(0,0,0,.35);
      animation: utils-float-up 1000ms cubic-bezier(.2,.7,.2,1) forwards;
    }

    .utils-floating-text.type-gold { color: #FFD86B; }
    .utils-floating-text.type-heal { color: #70F7A4; }
    .utils-floating-text.type-damage { color: #FF7070; }
    .utils-floating-text.type-exp { color: #7CCBFF; }
    .utils-floating-text.type-tip { color: #FFFFFF; }

    @keyframes utils-float-up {
      0% {
        opacity: 0;
        transform: translate(-50%, -50%) translateY(0) scale(.75);
      }
      12% {
        opacity: 1;
        transform: translate(-50%, -50%) translateY(-8px) scale(1.03);
      }
      100% {
        opacity: 0;
        transform: translate(-50%, -50%) translateY(-72px) scale(1.08);
      }
    }
  `;
  document.head.appendChild(style);
}

/**
 * 1. 格式化数字（K/M 单位）
 * 例如：950 => "950", 1200 => "1.2K", 2580000 => "2.58M"
 */
function formatNumber(num) {
  const n = Number(num);
  if (!Number.isFinite(n)) return '0';

  const abs = Math.abs(n);
  if (abs >= 1e6) {
    const value = n / 1e6;
    const fixed = abs >= 1e8 ? 1 : 2;
    return `${_trimZero(value.toFixed(fixed))}M`;
  }
  if (abs >= 1e3) {
    const value = n / 1e3;
    const fixed = abs >= 1e5 ? 1 : 2;
    return `${_trimZero(value.toFixed(fixed))}K`;
  }
  if (Number.isInteger(n)) return String(n);
  return _trimZero(n.toFixed(2));
}

/**
 * 2. 随机整数（包含 min 和 max）
 */
function randomInt(min, max) {
  let a = Math.ceil(Number(min));
  let b = Math.floor(Number(max));
  if (!Number.isFinite(a) || !Number.isFinite(b)) return 0;
  if (a > b) [a, b] = [b, a];
  return Math.floor(Math.random() * (b - a + 1)) + a;
}

/**
 * 3. 随机选择数组中的一个元素
 */
function randomChoice(array) {
  if (!Array.isArray(array) || array.length === 0) return undefined;
  return array[randomInt(0, array.length - 1)];
}

/**
 * 4. Promise 延迟函数
 * 用法：await delay(500)
 */
function delay(ms) {
  const time = Math.max(0, Number(ms) || 0);
  return new Promise((resolve) => setTimeout(resolve, time));
}

/**
 * 5. 深拷贝（支持对象/数组/Map/Set/Date/RegExp，处理循环引用）
 */
function deepClone(obj) {
  if (typeof structuredClone === 'function') {
    try {
      return structuredClone(obj);
    } catch (e) {
      // structuredClone 失败时自动走手写克隆逻辑
    }
  }

  const cache = new WeakMap();

  const cloneRecursively = (target) => {
    if (target === null || typeof target !== 'object') return target;
    if (cache.has(target)) return cache.get(target);

    if (target instanceof Date) return new Date(target.getTime());
    if (target instanceof RegExp) return new RegExp(target.source, target.flags);

    if (target instanceof Map) {
      const result = new Map();
      cache.set(target, result);
      target.forEach((value, key) => {
        result.set(cloneRecursively(key), cloneRecursively(value));
      });
      return result;
    }

    if (target instanceof Set) {
      const result = new Set();
      cache.set(target, result);
      target.forEach((value) => {
        result.add(cloneRecursively(value));
      });
      return result;
    }

    if (ArrayBuffer.isView(target)) {
      return new target.constructor(target);
    }

    if (target instanceof ArrayBuffer) {
      return target.slice(0);
    }

    const result = Array.isArray(target)
      ? []
      : Object.create(Object.getPrototypeOf(target));

    cache.set(target, result);

    Reflect.ownKeys(target).forEach((key) => {
      result[key] = cloneRecursively(target[key]);
    });

    return result;
  };

  return cloneRecursively(obj);
}

/**
 * 6. 限制数值范围
 * 小于 min 返回 min，大于 max 返回 max
 */
function clamp(value, min, max) {
  let v = Number(value);
  let a = Number(min);
  let b = Number(max);

  if (!Number.isFinite(v)) v = 0;
  if (!Number.isFinite(a)) a = 0;
  if (!Number.isFinite(b)) b = 0;
  if (a > b) [a, b] = [b, a];

  return Math.min(b, Math.max(a, v));
}

/**
 * 7. 线性插值
 * t=0 返回 start，t=1 返回 end
 */
function lerp(start, end, t) {
  const s = Number(start) || 0;
  const e = Number(end) || 0;
  const ratio = Number(t) || 0;
  return s + (e - s) * ratio;
}

/**
 * 8. 数值滚动动画（DOM 元素数字逐步变化）
 * 返回 Promise，动画结束后 resolve
 */
function animateNumber(element, from, to, duration) {
  return new Promise((resolve) => {
    if (!element || typeof element.textContent === 'undefined') {
      resolve(Number(to) || 0);
      return;
    }

    const startValue = Number.isFinite(Number(from))
      ? Number(from)
      : _parseDisplayNumber(element.textContent);

    const endValue = Number(to) || 0;
    const total = Math.max(0, Number(duration) || 0);

    const render = (value, isEnd) => {
      const useCompact = Math.abs(startValue) >= 1000 || Math.abs(endValue) >= 1000;
      const isIntegerAnim = Number.isInteger(startValue) && Number.isInteger(endValue);
      let text;

      if (useCompact) {
        text = formatNumber(isEnd ? endValue : value);
      } else if (isIntegerAnim) {
        text = String(Math.round(value));
      } else {
        text = _trimZero(value.toFixed(2));
      }

      element.textContent = text;
      element.dataset.rawValue = String(value);
    };

    if (total === 0) {
      render(endValue, true);
      resolve(endValue);
      return;
    }

    const raf = (typeof requestAnimationFrame !== 'undefined')
      ? requestAnimationFrame
      : (fn) => setTimeout(() => fn(Date.now()), 16);

    const nowFn = (typeof performance !== 'undefined' && performance.now)
      ? () => performance.now()
      : () => Date.now();

    const startTime = nowFn();

    const step = (now) => {
      const progress = clamp((now - startTime) / total, 0, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // 缓出动画
      const current = lerp(startValue, endValue, eased);

      render(current, progress >= 1);

      if (progress < 1) {
        raf(step);
      } else {
        resolve(endValue);
      }
    };

    raf(step);
  });
}

/**
 * 9. 创建粒子效果
 * container：粒子挂载容器（可传 DOM 或选择器）
 * options：支持 count/x/y/emoji/emojiPool/sizeMin/sizeMax/lifeMin/lifeMax/spreadX/spreadY/color
 */
function createParticle(container, options = {}) {
  if (typeof document === 'undefined') return null;
  _ensureUtilsEffectStyle();

  let target = container;
  if (typeof target === 'string') target = document.querySelector(target);
  if (!target || !target.appendChild) target = document.body;

  if (target !== document.body && typeof getComputedStyle === 'function') {
    const pos = getComputedStyle(target).position;
    if (!pos || pos === 'static') target.style.position = 'relative';
  }

  const count = clamp(parseInt(options.count ?? 1, 10) || 1, 1, 200);
  const sizeMin = Number(options.sizeMin ?? 12);
  const sizeMax = Number(options.sizeMax ?? 26);
  const lifeMin = Number(options.lifeMin ?? 450);
  const lifeMax = Number(options.lifeMax ?? 1000);
  const spreadX = Number(options.spreadX ?? 80);
  const spreadY = Number(options.spreadY ?? 75);

  const defaultPool = ['✨', '🔥', '⭐', '💥', '🍲'];
  const pool = Array.isArray(options.emojiPool) && options.emojiPool.length
    ? options.emojiPool
    : defaultPool;

  const result = [];
  const rect = target.getBoundingClientRect ? target.getBoundingClientRect() : { width: window.innerWidth, height: window.innerHeight };

  for (let i = 0; i < count; i++) {
    const particle = document.createElement('span');
    particle.className = 'utils-particle';

    const emoji = options.emoji || randomChoice(pool);
    particle.textContent = emoji;

    const minSize = Math.min(sizeMin, sizeMax);
    const maxSize = Math.max(sizeMin, sizeMax);
    particle.style.fontSize = `${randomInt(minSize, maxSize)}px`;
    if (options.color) particle.style.color = options.color;

    const startX = Number.isFinite(Number(options.x))
      ? Number(options.x)
      : randomInt(0, Math.max(0, Math.floor(rect.width)));
    const startY = Number.isFinite(Number(options.y))
      ? Number(options.y)
      : randomInt(0, Math.max(0, Math.floor(rect.height)));

    if (target === document.body) {
      particle.style.position = 'fixed';
    }
    particle.style.left = `${startX}px`;
    particle.style.top = `${startY}px`;
    particle.style.opacity = '1';

    const life = randomInt(Math.min(lifeMin, lifeMax), Math.max(lifeMin, lifeMax));
    const dx = Number.isFinite(Number(options.dx))
      ? Number(options.dx)
      : randomInt(-spreadX, spreadX);
    const dy = Number.isFinite(Number(options.dy))
      ? Number(options.dy)
      : -randomInt(20, spreadY);
    const rotate = Number.isFinite(Number(options.rotate))
      ? Number(options.rotate)
      : randomInt(-200, 200);
    const scale = Number.isFinite(Number(options.scale))
      ? Number(options.scale)
      : Number((Math.random() * 0.6 + 0.8).toFixed(2));

    particle.style.transition = `transform ${life}ms cubic-bezier(.17,.67,.28,1.03), opacity ${life}ms ease-out`;

    target.appendChild(particle);

    const raf = (typeof requestAnimationFrame !== 'undefined')
      ? requestAnimationFrame
      : (fn) => setTimeout(fn, 16);

    raf(() => {
      particle.style.transform = `translate(${dx}px, ${dy}px) rotate(${rotate}deg) scale(${scale})`;
      particle.style.opacity = '0';
    });

    setTimeout(() => {
      if (particle.parentNode) particle.parentNode.removeChild(particle);
    }, life + 80);

    result.push(particle);
  }

  return count === 1 ? result[0] : result;
}

/**
 * 10. 显示浮动文字（如：+100 金币）
 * x/y 使用视口坐标（clientX/clientY）
 * type 可选：gold/heal/damage/exp/tip
 */
function showFloatingText(text, x, y, type = 'gold') {
  if (typeof document === 'undefined') return null;
  _ensureUtilsEffectStyle();

  const el = document.createElement('div');
  el.className = `utils-floating-text type-${type || 'gold'}`;
  el.textContent = String(text ?? '');

  const px = Math.round(Number(x) || 0);
  const py = Math.round(Number(y) || 0);
  el.style.left = `${px}px`;
  el.style.top = `${py}px`;

  if (type === 'damage') el.style.fontSize = '30px';
  else if (type === 'tip') el.style.fontSize = '20px';
  else el.style.fontSize = '26px';

  const duration = type === 'tip' ? 850 : 1050;
  el.style.animationDuration = `${duration}ms`;

  document.body.appendChild(el);
  el.addEventListener('animationend', () => {
    if (el.parentNode) el.parentNode.removeChild(el);
  }, { once: true });

  return el;
}

/** 统一导出，方便通过 Utils.xxx 调用 */
const Utils = {
  formatNumber,
  randomInt,
  randomChoice,
  delay,
  deepClone,
  clamp,
  lerp,
  animateNumber,
  createParticle,
  showFloatingText
};

if (typeof globalThis !== 'undefined') {
  globalThis.Utils = Object.assign(globalThis.Utils || {}, Utils);
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Utils;
}