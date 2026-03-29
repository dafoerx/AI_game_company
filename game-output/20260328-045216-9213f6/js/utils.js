'use strict';

/**
 * 内部：确保特效样式只注入一次
 */
function ensureUtilsEffectStyles() {
  if (typeof document === 'undefined') return;
  const styleId = 'zzj-utils-effects-style';
  if (document.getElementById(styleId)) return;

  const style = document.createElement('style');
  style.id = styleId;
  style.textContent = `
    .utils-particle {
      position: absolute;
      pointer-events: none;
      z-index: 999;
      will-change: transform, opacity, filter;
      animation: utils-particle-fly var(--dur, 900ms) cubic-bezier(.12,.8,.3,1) forwards;
      box-shadow: 0 0 8px rgba(255,255,255,.35);
    }

    @keyframes utils-particle-fly {
      0% {
        transform: translate(-50%, -50%) scale(1);
        opacity: 1;
        filter: blur(0);
      }
      100% {
        transform: translate(
          calc(-50% + var(--dx, 0px)),
          calc(-50% + var(--dy, -60px))
        ) scale(0.15);
        opacity: 0;
        filter: blur(1px);
      }
    }

    .utils-floating-text {
      position: fixed;
      pointer-events: none;
      z-index: 9999;
      font-weight: 800;
      font-size: 28px;
      line-height: 1;
      white-space: nowrap;
      transform: translate(-50%, -50%);
      text-shadow: 0 2px 8px rgba(0,0,0,.35);
      animation: utils-floating-up var(--dur, 1100ms) cubic-bezier(.2,.9,.2,1) forwards;
      user-select: none;
    }

    @keyframes utils-floating-up {
      0% {
        transform: translate(-50%, -35%) scale(0.75);
        opacity: 0;
      }
      12% {
        transform: translate(-50%, -50%) scale(1.08);
        opacity: 1;
      }
      100% {
        transform: translate(-50%, -170%) scale(1);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(style);
}

/**
 * 内部：去掉小数末尾无用的 0
 */
function trimZero(numStr) {
  return String(numStr).replace(/(\.\d*?[1-9])0+$/g, '$1').replace(/\.0+$/g, '');
}

/**
 * 1. 格式化数字（K/M 单位）
 * 例如：950 => "950"、1200 => "1.2K"、2500000 => "2.5M"
 */
function formatNumber(num) {
  const n = Number(num);
  if (!Number.isFinite(n)) return '0';

  const sign = n < 0 ? '-' : '';
  const abs = Math.abs(n);

  if (abs >= 1_000_000) {
    const value = abs >= 10_000_000 ? (abs / 1_000_000).toFixed(0) : (abs / 1_000_000).toFixed(1);
    return sign + trimZero(value) + 'M';
  }

  if (abs >= 1_000) {
    const value = abs >= 10_000 ? (abs / 1_000).toFixed(0) : (abs / 1_000).toFixed(1);
    return sign + trimZero(value) + 'K';
  }

  if (Number.isInteger(abs)) return sign + String(abs);
  return sign + trimZero(abs.toFixed(2));
}

/**
 * 2. 随机整数（包含 min 和 max）
 */
function randomInt(min, max) {
  let a = Number(min);
  let b = Number(max);
  if (!Number.isFinite(a) || !Number.isFinite(b)) return 0;
  if (a > b) [a, b] = [b, a];
  a = Math.ceil(a);
  b = Math.floor(b);
  return Math.floor(Math.random() * (b - a + 1)) + a;
}

/**
 * 3. 从数组中随机选择一个元素
 */
function randomChoice(array) {
  if (!Array.isArray(array) || array.length === 0) return undefined;
  return array[randomInt(0, array.length - 1)];
}

/**
 * 4. Promise 延迟
 */
function delay(ms) {
  const time = Math.max(0, Number(ms) || 0);
  return new Promise((resolve) => setTimeout(resolve, time));
}

/**
 * 内部：获取数值的小数位数
 */
function getDecimalPlaces(num) {
  const n = Number(num);
  if (!Number.isFinite(n)) return 0;
  const text = String(n);
  if (text.includes('e-')) {
    const [, exp] = text.split('e-');
    return Number(exp) || 0;
  }
  const part = text.split('.')[1];
  return part ? part.length : 0;
}

/**
 * 5. 深拷贝（支持对象、数组、Date、RegExp、Map、Set，处理循环引用）
 */
function deepClone(obj, cache = new WeakMap()) {
  if (obj === null || typeof obj !== 'object') return obj;
  if (cache.has(obj)) return cache.get(obj);

  if (obj instanceof Date) return new Date(obj.getTime());
  if (obj instanceof RegExp) return new RegExp(obj.source, obj.flags);

  if (obj instanceof Map) {
    const clonedMap = new Map();
    cache.set(obj, clonedMap);
    obj.forEach((value, key) => {
      clonedMap.set(deepClone(key, cache), deepClone(value, cache));
    });
    return clonedMap;
  }

  if (obj instanceof Set) {
    const clonedSet = new Set();
    cache.set(obj, clonedSet);
    obj.forEach((value) => {
      clonedSet.add(deepClone(value, cache));
    });
    return clonedSet;
  }

  const cloned = Array.isArray(obj) ? [] : Object.create(Object.getPrototypeOf(obj));
  cache.set(obj, cloned);

  Reflect.ownKeys(obj).forEach((key) => {
    cloned[key] = deepClone(obj[key], cache);
  });

  return cloned;
}

/**
 * 6. 限制数值范围
 */
function clamp(value, min, max) {
  let a = Number(min);
  let b = Number(max);
  const v = Number(value);

  if (!Number.isFinite(v)) return Number.isFinite(a) ? a : 0;
  if (!Number.isFinite(a) && !Number.isFinite(b)) return v;
  if (!Number.isFinite(a)) a = b;
  if (!Number.isFinite(b)) b = a;
  if (a > b) [a, b] = [b, a];

  return Math.min(b, Math.max(a, v));
}

/**
 * 7. 线性插值
 * t 通常在 0~1 之间：0 返回 start，1 返回 end
 */
function lerp(start, end, t) {
  return Number(start) + (Number(end) - Number(start)) * Number(t);
}

/**
 * 内部：把容器参数解析为 DOM 元素
 */
function resolveContainer(container) {
  if (typeof document === 'undefined') return null;
  if (container instanceof Element) return container;
  if (typeof container === 'string') return document.querySelector(container);
  return document.body;
}

/**
 * 8. 数值滚动动画（DOM 元素数字逐步变化）
 * - element: 目标 DOM
 * - from/to: 起止数值
 * - duration: 动画时长（毫秒）
 */
function animateNumber(element, from, to, duration = 600) {
  return new Promise((resolve) => {
    if (!element || typeof window === 'undefined') {
      resolve(to);
      return;
    }

    const startValue = Number(from) || 0;
    const endValue = Number(to) || 0;
    const total = Math.max(0, Number(duration) || 0);
    const decimalPlaces = Math.min(4, Math.max(getDecimalPlaces(startValue), getDecimalPlaces(endValue)));
    const useInteger = decimalPlaces === 0;

    // 用于避免同一个元素多个动画互相抢占
    element.__numAnimToken = (element.__numAnimToken || 0) + 1;
    const token = element.__numAnimToken;

    const render = (value) => {
      const mode = element.dataset && element.dataset.format ? element.dataset.format : 'locale';
      if (mode === 'abbr') {
        element.textContent = formatNumber(value);
      } else if (useInteger) {
        element.textContent = Math.round(value).toLocaleString('zh-CN');
      } else {
        element.textContent = value.toFixed(decimalPlaces);
      }
    };

    if (total === 0) {
      render(endValue);
      resolve(endValue);
      return;
    }

    const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3);
    const diff = endValue - startValue;
    const startTime = performance.now();

    const tick = (now) => {
      // 如果被新的动画覆盖，直接终止当前动画
      if (element.__numAnimToken !== token) {
        resolve(undefined);
        return;
      }

      const progress = clamp((now - startTime) / total, 0, 1);
      const eased = easeOutCubic(progress);
      const current = startValue + diff * eased;
      render(current);

      if (progress < 1) {
        requestAnimationFrame(tick);
      } else {
        render(endValue);
        resolve(endValue);
      }
    };

    render(startValue);
    requestAnimationFrame(tick);
  });
}

/**
 * 9. 创建粒子效果
 * options 常用参数：
 * - x, y: 粒子起点（相对容器）
 * - size: 尺寸
 * - color: 颜色
 * - duration: 动画时长
 * - distance: 飞行距离
 * - angle: 飞行角度（弧度）
 * - shape: circle | square | diamond | star
 * - fixed: true 时按屏幕坐标 fixed 定位
 */
function createParticle(container, options = {}) {
  if (typeof document === 'undefined') return null;
  ensureUtilsEffectStyles();

  const target = resolveContainer(container);
  if (!target) return null;

  const palette = ['#FFD166', '#FF7A59', '#7AE582', '#74C0FC', '#C77DFF', '#FFFFFF'];
  const isFixed = !!options.fixed;
  const rect = target.getBoundingClientRect();

  const x = Number.isFinite(options.x) ? options.x : randomInt(0, Math.max(0, Math.floor(rect.width)));
  const y = Number.isFinite(options.y) ? options.y : randomInt(0, Math.max(0, Math.floor(rect.height)));
  const size = Math.max(2, Number(options.size) || randomInt(4, 10));
  const duration = Math.max(120, Number(options.duration) || randomInt(600, 1100));
  const distance = Math.max(10, Number(options.distance) || randomInt(30, 90));
  const angle = Number.isFinite(options.angle) ? options.angle : Math.random() * Math.PI * 2;
  const color = options.color || randomChoice(palette);
  const shape = options.shape || 'circle';

  const dx = Math.cos(angle) * distance;
  const dy = Math.sin(angle) * distance - randomInt(12, 42); // 稍微向上，视觉更有“爆开感”

  const particle = document.createElement('span');
  particle.className = 'utils-particle';
  particle.style.width = `${size}px`;
  particle.style.height = `${size}px`;
  particle.style.background = color;
  particle.style.setProperty('--dx', `${dx.toFixed(2)}px`);
  particle.style.setProperty('--dy', `${dy.toFixed(2)}px`);
  particle.style.setProperty('--dur', `${duration}ms`);
  particle.style.opacity = '1';

  // 不同形状样式
  if (shape === 'square') {
    particle.style.borderRadius = '2px';
  } else if (shape === 'diamond') {
    particle.style.borderRadius = '2px';
    particle.style.transform = 'translate(-50%, -50%) rotate(45deg)';
  } else if (shape === 'star') {
    particle.style.background = color;
    particle.style.clipPath = 'polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%)';
  } else {
    particle.style.borderRadius = '50%';
  }

  if (isFixed) {
    particle.style.position = 'fixed';
    particle.style.left = `${x}px`;
    particle.style.top = `${y}px`;
    document.body.appendChild(particle);
  } else {
    const style = window.getComputedStyle(target);
    if (style.position === 'static') target.style.position = 'relative';
    particle.style.left = `${x}px`;
    particle.style.top = `${y}px`;
    target.appendChild(particle);
  }

  const remove = () => particle && particle.parentNode && particle.parentNode.removeChild(particle);
  particle.addEventListener('animationend', remove, { once: true });
  setTimeout(remove, duration + 120);

  return particle;
}

/**
 * 10. 显示浮动文字（如：+100 金币）
 * - x, y 使用屏幕坐标（clientX/clientY）
 * - type 支持：gold/heal/damage/warning/info/love/default
 */
function showFloatingText(text, x, y, type = 'default') {
  if (typeof document === 'undefined') return null;
  ensureUtilsEffectStyles();

  const presets = {
    gold:    { color: '#FFD166', shadow: '0 0 16px rgba(255,209,102,.55)' },
    heal:    { color: '#7AE582', shadow: '0 0 16px rgba(122,229,130,.55)' },
    damage:  { color: '#FF6B6B', shadow: '0 0 16px rgba(255,107,107,.55)' },
    warning: { color: '#FFA94D', shadow: '0 0 16px rgba(255,169,77,.55)' },
    info:    { color: '#74C0FC', shadow: '0 0 16px rgba(116,192,252,.55)' },
    love:    { color: '#FF87B5', shadow: '0 0 16px rgba(255,135,181,.55)' },
    default: { color: '#FFFFFF', shadow: '0 0 14px rgba(255,255,255,.45)' }
  };

  const styleInfo = presets[type] || presets.default;
  const fx = Number.isFinite(x) ? x : window.innerWidth / 2;
  const fy = Number.isFinite(y) ? y : window.innerHeight / 2;
  const duration = randomInt(900, 1250);

  const el = document.createElement('div');
  el.className = 'utils-floating-text';
  el.textContent = String(text ?? '');
  el.style.left = `${fx}px`;
  el.style.top = `${fy}px`;
  el.style.color = styleInfo.color;
  el.style.textShadow = `${styleInfo.shadow}, 0 2px 8px rgba(0,0,0,.35)`;
  el.style.setProperty('--dur', `${duration}ms`);

  document.body.appendChild(el);

  const remove = () => el && el.parentNode && el.parentNode.removeChild(el);
  el.addEventListener('animationend', remove, { once: true });
  setTimeout(remove, duration + 120);

  return el;
}

// 导出为全局工具对象（浏览器）
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

if (typeof window !== 'undefined') {
  window.Utils = Utils;
}

// 兼容 CommonJS（如需在构建工具中使用）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Utils;
}