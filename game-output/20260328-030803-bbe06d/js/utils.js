(function (global) {
  'use strict';

  const STYLE_ID = 'feiting-utils-effects-style';
  const NUMBER_ANIM_KEY = '__feitingNumberAnimFrame__';

  // 注入粒子与浮动文字所需的基础样式（只注入一次）
  function ensureEffectsStyle() {
    if (typeof document === 'undefined') return;
    if (document.getElementById(STYLE_ID)) return;

    const style = document.createElement('style');
    style.id = STYLE_ID;
    style.textContent = `
      .btz-particle {
        position: absolute;
        pointer-events: none;
        user-select: none;
        z-index: 9998;
        will-change: transform, opacity, filter;
      }

      .btz-floating-text {
        position: fixed;
        left: 0;
        top: 0;
        transform: translate(-50%, -50%);
        pointer-events: none;
        user-select: none;
        white-space: nowrap;
        z-index: 10000;
        font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
        font-weight: 900;
        letter-spacing: 0.5px;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
        will-change: transform, opacity, filter;
      }

      .btz-type-coin {
        color: #ffd86b;
        text-shadow: 0 2px 8px rgba(255, 153, 0, 0.45), 0 0 14px rgba(255, 196, 72, 0.35);
      }

      .btz-type-income,
      .btz-type-success {
        color: #7CFFB2;
        text-shadow: 0 2px 8px rgba(20, 180, 120, 0.45), 0 0 14px rgba(90, 255, 180, 0.3);
      }

      .btz-type-warning {
        color: #ff9b7a;
        text-shadow: 0 2px 8px rgba(255, 110, 90, 0.45), 0 0 14px rgba(255, 133, 106, 0.25);
      }

      .btz-type-exp,
      .btz-type-info {
        color: #9ec8ff;
        text-shadow: 0 2px 8px rgba(80, 130, 255, 0.45), 0 0 14px rgba(120, 170, 255, 0.3);
      }

      .btz-type-critical {
        color: #ff5f82;
        text-shadow: 0 2px 8px rgba(255, 60, 90, 0.5), 0 0 16px rgba(255, 90, 120, 0.35);
      }

      @keyframes btzFloatFallback {
        0%   { opacity: 0; transform: translate(-50%, -50%) scale(0.5); }
        20%  { opacity: 1; transform: translate(-50%, -62%) scale(1.06); }
        100% { opacity: 0; transform: translate(-50%, -120%) scale(0.92); }
      }
    `;

    if (document.head) {
      document.head.appendChild(style);
    } else {
      document.addEventListener(
        'DOMContentLoaded',
        () => document.head && document.head.appendChild(style),
        { once: true }
      );
    }
  }

  // 统计小数位数（用于数值动画精度控制）
  function getDecimalPlaces(num) {
    if (!Number.isFinite(num)) return 0;
    const str = String(num);
    if (str.indexOf('e-') > -1) {
      const parts = str.split('e-');
      const sci = parseInt(parts[1], 10);
      return Number.isNaN(sci) ? 0 : sci;
    }
    const idx = str.indexOf('.');
    return idx === -1 ? 0 : str.length - idx - 1;
  }

  // 去除末尾无意义的 0（例如 1.50 -> 1.5）
  function trimTrailingZeros(valueStr) {
    return valueStr.replace(/\.0+$|(\.\d*[1-9])0+$/, '$1');
  }

  // 将数字格式化为 K/M 显示（例如 1200 -> 1.2K，3500000 -> 3.5M）
  function formatNumber(num) {
    const n = Number(num);
    if (!Number.isFinite(n)) return '0';

    const abs = Math.abs(n);
    if (abs < 1000) {
      return Number.isInteger(n) ? String(n) : trimTrailingZeros(n.toFixed(2));
    }

    let value = n;
    let unit = '';

    if (abs >= 1_000_000) {
      value = n / 1_000_000;
      unit = 'M';
    } else {
      value = n / 1_000;
      unit = 'K';
    }

    const precision = Math.abs(value) >= 100 ? 0 : Math.abs(value) >= 10 ? 1 : 2;
    return trimTrailingZeros(value.toFixed(precision)) + unit;
  }

  // 生成 [min, max] 区间内的随机整数（包含端点）
  function randomInt(min, max) {
    let a = Math.ceil(Number(min));
    let b = Math.floor(Number(max));

    if (!Number.isFinite(a) || !Number.isFinite(b)) return 0;
    if (a > b) [a, b] = [b, a];

    return Math.floor(Math.random() * (b - a + 1)) + a;
  }

  // 从数组中随机返回一个元素（数组为空时返回 undefined）
  function randomChoice(array) {
    if (!Array.isArray(array) || array.length === 0) return undefined;
    return array[randomInt(0, array.length - 1)];
  }

  // Promise 延迟函数（用于 async/await 节奏控制）
  function delay(ms) {
    const time = Math.max(0, Number(ms) || 0);
    return new Promise((resolve) => setTimeout(resolve, time));
  }

  // 深拷贝：支持 Object、Array、Date、RegExp、Map、Set、TypedArray，并处理循环引用
  function deepClone(obj, cache = new WeakMap()) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (cache.has(obj)) return cache.get(obj);

    if (obj instanceof Date) return new Date(obj.getTime());
    if (obj instanceof RegExp) return new RegExp(obj.source, obj.flags);

    if (obj instanceof Map) {
      const mapClone = new Map();
      cache.set(obj, mapClone);
      obj.forEach((value, key) => {
        mapClone.set(deepClone(key, cache), deepClone(value, cache));
      });
      return mapClone;
    }

    if (obj instanceof Set) {
      const setClone = new Set();
      cache.set(obj, setClone);
      obj.forEach((value) => {
        setClone.add(deepClone(value, cache));
      });
      return setClone;
    }

    if (ArrayBuffer.isView(obj)) {
      return new obj.constructor(obj);
    }

    if (obj instanceof ArrayBuffer) {
      return obj.slice(0);
    }

    const cloneTarget = Array.isArray(obj) ? [] : Object.create(Object.getPrototypeOf(obj));
    cache.set(obj, cloneTarget);

    Reflect.ownKeys(obj).forEach((key) => {
      const descriptor = Object.getOwnPropertyDescriptor(obj, key);
      if (!descriptor) return;

      if ('value' in descriptor) {
        descriptor.value = deepClone(descriptor.value, cache);
      }

      Object.defineProperty(cloneTarget, key, descriptor);
    });

    return cloneTarget;
  }

  // 将 value 限制在 [min, max] 区间内
  function clamp(value, min, max) {
    let a = Number(min);
    let b = Number(max);
    const v = Number(value);

    if (!Number.isFinite(a)) a = 0;
    if (!Number.isFinite(b)) b = 0;
    if (a > b) [a, b] = [b, a];
    if (!Number.isFinite(v)) return a;

    return Math.min(Math.max(v, a), b);
  }

  // 线性插值：在 start 和 end 之间按 t 比例取值（t=0 返回 start，t=1 返回 end）
  function lerp(start, end, t) {
    const s = Number(start) || 0;
    const e = Number(end) || 0;
    const ratio = Number(t) || 0;
    return s + (e - s) * ratio;
  }

  // 数值滚动动画：让 DOM 元素中的数字从 from 平滑变化到 to
  function animateNumber(element, from, to, duration = 600) {
    return new Promise((resolve) => {
      if (!element || typeof element.textContent === 'undefined') {
        resolve(Number(to) || 0);
        return;
      }

      const startValue = Number(from);
      const endValue = Number(to);

      if (!Number.isFinite(startValue) || !Number.isFinite(endValue)) {
        const finalValue = Number.isFinite(endValue) ? endValue : 0;
        element.textContent = String(finalValue);
        resolve(finalValue);
        return;
      }

      const total = Math.max(0, Number(duration) || 0);
      const prefix = element.dataset && element.dataset.prefix ? element.dataset.prefix : '';
      const suffix = element.dataset && element.dataset.suffix ? element.dataset.suffix : '';
      const isIntAnim = Number.isInteger(startValue) && Number.isInteger(endValue);
      const decimals = isIntAnim ? 0 : Math.max(getDecimalPlaces(startValue), getDecimalPlaces(endValue), 2);

      // 若该元素已有上一段数值动画，先取消，避免重叠闪烁
      if (element[NUMBER_ANIM_KEY]) {
        cancelAnimationFrame(element[NUMBER_ANIM_KEY]);
        element[NUMBER_ANIM_KEY] = null;
      }

      const renderValue = (num) => {
        if (isIntAnim) {
          const rounded = Math.round(num);
          const display = Math.abs(rounded) >= 1000 ? formatNumber(rounded) : String(rounded);
          element.textContent = prefix + display + suffix;
        } else {
          const fixed = trimTrailingZeros(num.toFixed(decimals));
          element.textContent = prefix + fixed + suffix;
        }
      };

      if (total === 0) {
        renderValue(endValue);
        resolve(endValue);
        return;
      }

      const startTime = performance.now();
      const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3);

      const step = (now) => {
        const elapsed = now - startTime;
        const progress = clamp(elapsed / total, 0, 1);
        const eased = easeOutCubic(progress);
        const current = lerp(startValue, endValue, eased);

        renderValue(current);

        if (progress < 1) {
          element[NUMBER_ANIM_KEY] = requestAnimationFrame(step);
        } else {
          element[NUMBER_ANIM_KEY] = null;
          renderValue(endValue);
          resolve(endValue);
        }
      };

      element[NUMBER_ANIM_KEY] = requestAnimationFrame(step);
    });
  }

  // 创建粒子效果：可用于金币爆开、火花、奖励喷发等视觉反馈
  function createParticle(container, options = {}) {
    if (typeof document === 'undefined') return null;
    ensureEffectsStyle();

    // 允许省略 container：直接传 options
    if (!container || !(container instanceof Element)) {
      options = container && typeof container === 'object' ? container : options;
      container = document.body;
    }

    const opts = options || {};
    const palette = opts.colors || ['#FFD166', '#FF9F43', '#FF6B6B', '#FFE082', '#FFC107'];
    const isEmoji = opts.shape === 'emoji' || !!opts.emoji;
    const lifetime = Math.max(120, Number(opts.lifetime) || randomInt(650, 1200));
    const size = Math.max(2, Number(opts.size) || randomInt(4, 10));
    const angleDeg = Number.isFinite(Number(opts.angle)) ? Number(opts.angle) : randomInt(-140, -40);
    const speed = Math.max(10, Number(opts.speed) || randomInt(90, 220));
    const gravity = Number.isFinite(Number(opts.gravity)) ? Number(opts.gravity) : 180;
    const rotation = Number.isFinite(Number(opts.rotate)) ? Number(opts.rotate) : randomInt(-160, 160);

    const relativeToViewport =
      opts.fixed === true || container === document.body || container === document.documentElement;

    if (!relativeToViewport) {
      const pos = getComputedStyle(container).position;
      if (pos === 'static') container.style.position = 'relative';
    }

    const rect = relativeToViewport
      ? { left: 0, top: 0, width: window.innerWidth, height: window.innerHeight }
      : container.getBoundingClientRect();

    const x = Number.isFinite(Number(opts.x)) ? Number(opts.x) : rect.width / 2;
    const y = Number.isFinite(Number(opts.y)) ? Number(opts.y) : rect.height / 2;

    const particle = document.createElement('span');
    particle.className = 'btz-particle';
    particle.style.position = relativeToViewport ? 'fixed' : 'absolute';
    particle.style.left = `${x}px`;
    particle.style.top = `${y}px`;
    particle.style.opacity = '1';

    if (isEmoji) {
      particle.textContent = opts.emoji || randomChoice(['✨', '🔥', '⭐', '💰']);
      particle.style.fontSize = `${Math.max(10, size * 1.8)}px`;
      particle.style.lineHeight = '1';
      particle.style.filter = 'drop-shadow(0 2px 4px rgba(0,0,0,0.25))';
    } else {
      const color = opts.color || randomChoice(palette);
      particle.style.width = `${size}px`;
      particle.style.height = `${size}px`;
      particle.style.background = `radial-gradient(circle at 35% 35%, #ffffff, ${color})`;
      particle.style.borderRadius = opts.shape === 'square' ? '2px' : '50%';
      particle.style.boxShadow = `0 0 ${Math.max(4, size)}px ${color}66`;
    }

    container.appendChild(particle);

    const rad = (angleDeg * Math.PI) / 180;
    const timeSec = lifetime / 1000;
    const dx = Math.cos(rad) * speed * timeSec;
    const dy = Math.sin(rad) * speed * timeSec + 0.5 * gravity * timeSec * timeSec;
    const endScale = Number.isFinite(Number(opts.endScale)) ? Number(opts.endScale) : 0.2;

    if (typeof particle.animate === 'function') {
      const anim = particle.animate(
        [
          { transform: 'translate(0px, 0px) scale(1) rotate(0deg)', opacity: 1, filter: 'blur(0px)' },
          {
            transform: `translate(${dx}px, ${dy}px) scale(${endScale}) rotate(${rotation}deg)`,
            opacity: 0,
            filter: 'blur(0.5px)'
          }
        ],
        {
          duration: lifetime,
          easing: 'cubic-bezier(0.15, 0.75, 0.25, 1)',
          fill: 'forwards'
        }
      );

      anim.onfinish = () => {
        if (particle.parentNode) particle.parentNode.removeChild(particle);
      };
    } else {
      // 兼容性降级：使用 CSS transition
      particle.style.transition = `transform ${lifetime}ms cubic-bezier(0.15, 0.75, 0.25, 1), opacity ${lifetime}ms`;
      requestAnimationFrame(() => {
        particle.style.transform = `translate(${dx}px, ${dy}px) scale(${endScale}) rotate(${rotation}deg)`;
        particle.style.opacity = '0';
      });
      setTimeout(() => {
        if (particle.parentNode) particle.parentNode.removeChild(particle);
      }, lifetime + 30);
    }

    return particle;
  }

  // 显示浮动文字：如“+100 金币”“升级成功”等，自动上浮并淡出
  function showFloatingText(text, x, y, type = 'coin') {
    if (typeof document === 'undefined') return null;
    ensureEffectsStyle();

    const label = document.createElement('div');
    const safeType = String(type || 'coin').toLowerCase();

    label.className = `btz-floating-text btz-type-${safeType}`;
    label.textContent = String(text == null ? '' : text);
    label.style.left = `${Math.round(Number(x) || 0)}px`;
    label.style.top = `${Math.round(Number(y) || 0)}px`;
    label.style.fontSize = safeType === 'critical' ? '30px' : '24px';
    label.style.opacity = '0';

    document.body.appendChild(label);

    const driftX = randomInt(-20, 20);
    const rise = safeType === 'warning' ? 46 : 58;
    const duration = safeType === 'critical' ? 1100 : 900;

    if (typeof label.animate === 'function') {
      const anim = label.animate(
        [
          { transform: 'translate(-50%, -50%) scale(0.5)', opacity: 0, filter: 'blur(1px)' },
          {
            transform: `translate(calc(-50% + ${driftX * 0.35}px), calc(-50% - 14px)) scale(1.1)`,
            opacity: 1,
            filter: 'blur(0px)',
            offset: 0.22
          },
          {
            transform: `translate(calc(-50% + ${driftX}px), calc(-50% - ${rise}px)) scale(0.95)`,
            opacity: 0,
            filter: 'blur(0.4px)'
          }
        ],
        {
          duration,
          easing: 'cubic-bezier(0.2, 0.8, 0.2, 1)',
          fill: 'forwards'
        }
      );

      anim.onfinish = () => {
        if (label.parentNode) label.parentNode.removeChild(label);
      };
    } else {
      // 兼容性降级：使用 keyframes 动画
      label.style.animation = `btzFloatFallback ${duration}ms ease-out forwards`;
      setTimeout(() => {
        if (label.parentNode) label.parentNode.removeChild(label);
      }, duration + 30);
    }

    return label;
  }

  // 默认在浏览器环境下提前准备样式
  if (typeof document !== 'undefined') {
    ensureEffectsStyle();
  }

  const utils = {
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

  // 挂载到全局，便于直接在其他脚本中使用
  global.Utils = Object.assign({}, global.Utils || {}, utils);
  global.GameUtils = global.Utils;

  // 同时暴露单个函数（兼容旧代码调用习惯）
  Object.assign(global, utils);

  // 兼容 CommonJS（如部分打包工具）
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = utils;
  }
})(typeof window !== 'undefined' ? window : globalThis);