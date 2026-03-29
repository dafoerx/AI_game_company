(function (global) {
  'use strict';

  const raf =
    (global.requestAnimationFrame && global.requestAnimationFrame.bind(global)) ||
    function (cb) {
      return setTimeout(function () {
        cb(Date.now());
      }, 16);
    };

  const caf =
    (global.cancelAnimationFrame && global.cancelAnimationFrame.bind(global)) ||
    function (id) {
      clearTimeout(id);
    };

  function trimZeros(str) {
    return String(str).replace(/\.?0+$/, '');
  }

  function toFiniteNumber(value, fallback) {
    const n = Number(value);
    return Number.isFinite(n) ? n : fallback;
  }

  /**
   * 格式化数字（K/M 单位），用于游戏金币、评分等数值展示
   * @param {number} num 原始数字
   * @returns {string} 格式化后的字符串
   */
  function formatNumber(num) {
    const n = Number(num);
    if (!Number.isFinite(n)) return '0';

    const sign = n < 0 ? '-' : '';
    const abs = Math.abs(n);

    if (abs >= 1e6) {
      const value = abs >= 1e8 ? (abs / 1e6).toFixed(0) : (abs / 1e6).toFixed(2);
      return sign + trimZeros(value) + 'M';
    }

    if (abs >= 1e3) {
      const value = abs >= 1e5 ? (abs / 1e3).toFixed(0) : (abs / 1e3).toFixed(2);
      return sign + trimZeros(value) + 'K';
    }

    if (Number.isInteger(abs)) return sign + String(abs);
    return sign + trimZeros(abs.toFixed(2));
  }

  /**
   * 生成指定范围内的随机整数（包含 min 和 max）
   * @param {number} min 最小值
   * @param {number} max 最大值
   * @returns {number} 随机整数
   */
  function randomInt(min, max) {
    let a = Math.ceil(toFiniteNumber(min, 0));
    let b = Math.floor(toFiniteNumber(max, 0));
    if (a > b) {
      const t = a;
      a = b;
      b = t;
    }
    return Math.floor(Math.random() * (b - a + 1)) + a;
  }

  /**
   * 从数组中随机选择一个元素
   * @param {Array} array 数据数组
   * @returns {*} 随机元素；若数组为空返回 undefined
   */
  function randomChoice(array) {
    if (!Array.isArray(array) || array.length === 0) return undefined;
    return array[randomInt(0, array.length - 1)];
  }

  /**
   * Promise 延迟函数，可配合 async/await 使用
   * @param {number} ms 延迟毫秒
   * @returns {Promise<void>}
   */
  function delay(ms) {
    const time = Math.max(0, toFiniteNumber(ms, 0));
    return new Promise(function (resolve) {
      setTimeout(resolve, time);
    });
  }

  /**
   * 深拷贝对象（支持常见 Object/Array/Map/Set/Date/RegExp，并处理循环引用）
   * @param {*} obj 需要克隆的数据
   * @returns {*} 深拷贝结果
   */
  function deepClone(obj) {
    if (typeof global.structuredClone === 'function') {
      try {
        return global.structuredClone(obj);
      } catch (e) {
        // 某些不可克隆对象会抛错，自动走后备方案
      }
    }

    const cache = new WeakMap();

    function clone(target) {
      if (target === null || typeof target !== 'object') return target;
      if (cache.has(target)) return cache.get(target);

      if (target instanceof Date) return new Date(target.getTime());
      if (target instanceof RegExp) return new RegExp(target.source, target.flags);

      if (target instanceof Map) {
        const result = new Map();
        cache.set(target, result);
        target.forEach(function (v, k) {
          result.set(clone(k), clone(v));
        });
        return result;
      }

      if (target instanceof Set) {
        const result = new Set();
        cache.set(target, result);
        target.forEach(function (v) {
          result.add(clone(v));
        });
        return result;
      }

      if (Array.isArray(target)) {
        const result = [];
        cache.set(target, result);
        for (let i = 0; i < target.length; i++) {
          result[i] = clone(target[i]);
        }
        return result;
      }

      const proto = Object.getPrototypeOf(target);
      const result = Object.create(proto);
      cache.set(target, result);

      Reflect.ownKeys(target).forEach(function (key) {
        const desc = Object.getOwnPropertyDescriptor(target, key);
        if (!desc) return;
        if ('value' in desc) desc.value = clone(desc.value);
        Object.defineProperty(result, key, desc);
      });

      return result;
    }

    return clone(obj);
  }

  /**
   * 将数值限制在指定区间范围内
   * @param {number} value 当前值
   * @param {number} min 最小值
   * @param {number} max 最大值
   * @returns {number} 限制后的结果
   */
  function clamp(value, min, max) {
    let v = toFiniteNumber(value, 0);
    let a = toFiniteNumber(min, 0);
    let b = toFiniteNumber(max, 0);
    if (a > b) {
      const t = a;
      a = b;
      b = t;
    }
    if (v < a) v = a;
    if (v > b) v = b;
    return v;
  }

  /**
   * 线性插值：根据 t 在 start 与 end 之间取值
   * @param {number} start 起点值
   * @param {number} end 终点值
   * @param {number} t 插值系数（通常 0~1）
   * @returns {number} 插值结果
   */
  function lerp(start, end, t) {
    const s = toFiniteNumber(start, 0);
    const e = toFiniteNumber(end, 0);
    const p = toFiniteNumber(t, 0);
    return s + (e - s) * p;
  }

  /**
   * 数值滚动动画：让 DOM 元素中的数字从 from 平滑变化到 to
   * 额外支持：data-prefix / data-suffix / data-format="compact" / data-precision
   * @param {HTMLElement} element 目标元素
   * @param {number} from 起始数字
   * @param {number} to 结束数字
   * @param {number} duration 动画时长（毫秒）
   * @returns {Promise<number>} 动画完成时返回最终值
   */
  function animateNumber(element, from, to, duration) {
    if (!element) return Promise.resolve(toFiniteNumber(to, 0));

    const startValue = toFiniteNumber(from, 0);
    const endValue = toFiniteNumber(to, 0);
    const time = Math.max(0, toFiniteNumber(duration, 0));

    const data = element.dataset || {};
    const prefix = data.prefix || '';
    const suffix = data.suffix || '';
    const compact = data.format === 'compact' || data.compact === 'true';

    let precision = 0;
    if (!Number.isInteger(startValue) || !Number.isInteger(endValue)) {
      const fromDec = (String(startValue).split('.')[1] || '').length;
      const toDec = (String(endValue).split('.')[1] || '').length;
      precision = Math.max(fromDec, toDec, 2);
      precision = clamp(precision, 0, 6);
    }
    if (data.precision !== undefined) {
      precision = clamp(parseInt(data.precision, 10) || 0, 0, 6);
    }

    function formatValue(v, forceFinal) {
      const value = forceFinal ? endValue : v;
      let text = '';

      if (compact) {
        text = formatNumber(value);
      } else if (precision === 0) {
        text = String(Math.round(value));
      } else {
        text = trimZeros(Number(value).toFixed(precision));
      }

      return prefix + text + suffix;
    }

    if (typeof element.__numAnimCancel === 'function') {
      element.__numAnimCancel(true);
    }

    if (time === 0) {
      element.textContent = formatValue(endValue, true);
      return Promise.resolve(endValue);
    }

    return new Promise(function (resolve) {
      const startTime = (global.performance && performance.now()) || Date.now();
      let frameId = null;
      let stopped = false;

      function easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
      }

      function stop(jumpToEnd) {
        if (stopped) return;
        stopped = true;
        if (frameId !== null) caf(frameId);
        if (jumpToEnd) {
          element.textContent = formatValue(endValue, true);
          resolve(endValue);
        }
      }

      element.__numAnimCancel = stop;
      element.textContent = formatValue(startValue, false);

      function tick(now) {
        if (stopped) return;

        const p = clamp((now - startTime) / time, 0, 1);
        const eased = easeOutCubic(p);
        const current = lerp(startValue, endValue, eased);

        element.textContent = formatValue(current, false);

        if (p < 1) {
          frameId = raf(tick);
        } else {
          element.__numAnimCancel = null;
          resolve(endValue);
        }
      }

      frameId = raf(tick);
    });
  }

  function ensureFxStyles() {
    if (typeof document === 'undefined') return;
    if (document.getElementById('game-utils-fx-style')) return;

    const style = document.createElement('style');
    style.id = 'game-utils-fx-style';
    style.textContent = `
      .game-floating-text{
        position: fixed;
        left: 0;
        top: 0;
        transform: translate(-50%, 0);
        pointer-events: none;
        user-select: none;
        white-space: nowrap;
        z-index: 99999;
        font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
        font-size: 28px;
        font-weight: 900;
        letter-spacing: 0.5px;
        animation: game-utils-float-up var(--duration, 950ms) cubic-bezier(.2,.75,.25,1) forwards;
        text-shadow: 0 3px 10px rgba(0,0,0,.35);
        will-change: transform, opacity;
      }
      .game-floating-text.type-gold{
        color: #ffd54f;
        text-shadow: 0 0 8px rgba(255,193,7,.65), 0 2px 10px rgba(0,0,0,.35);
      }
      .game-floating-text.type-success{
        color: #7CFFB2;
        text-shadow: 0 0 8px rgba(46, 255, 159, .5), 0 2px 10px rgba(0,0,0,.35);
      }
      .game-floating-text.type-damage{
        color: #ff6b6b;
        text-shadow: 0 0 8px rgba(255,77,77,.5), 0 2px 10px rgba(0,0,0,.35);
      }
      .game-floating-text.type-info{
        color: #8ecbff;
        text-shadow: 0 0 8px rgba(92,173,255,.5), 0 2px 10px rgba(0,0,0,.35);
      }
      .game-floating-text.type-warn{
        color: #ffb86b;
        text-shadow: 0 0 8px rgba(255,152,0,.55), 0 2px 10px rgba(0,0,0,.35);
      }
      @keyframes game-utils-float-up{
        0%{
          opacity: 0;
          transform: translate(-50%, 0) scale(.75);
          filter: blur(1px);
        }
        12%{
          opacity: 1;
          transform: translate(-50%, -8px) scale(1);
          filter: blur(0);
        }
        100%{
          opacity: 0;
          transform: translate(calc(-50% + var(--drift, 0px)), -84px) scale(1.08);
          filter: blur(.2px);
        }
      }
    `;
    document.head.appendChild(style);
  }

  /**
   * 创建粒子效果（可用于金币爆散、点击反馈、升级特效）
   * @param {HTMLElement} container 粒子容器
   * @param {Object} options 粒子配置项
   * @returns {HTMLElement} 创建出的粒子元素
   */
  function createParticle