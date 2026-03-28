/**
 * 沸腾掌柜：火锅店经营MVP - 工具函数
 * ═══════════════════════════════════════
 */

/**
 * 格式化数字
 */
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return Math.floor(num).toString();
}

/**
 * 随机整数
 */
function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * 随机选择
 */
function randomChoice(array) {
    return array[Math.floor(Math.random() * array.length)];
}

/**
 * 延迟执行
 */
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 深拷贝
 */
function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

/**
 * 限制数值范围
 */
function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
}

/**
 * 线性插值
 */
function lerp(start, end, t) {
    return start + (end - start) * t;
}
