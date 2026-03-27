window.dnotifyTimer = null; window.dnotifyEl = document.body.appendChild(Object.assign(document.createElement('div'), { 
  id: 'dnotify', style: `display:none; min-width: 260px;max-width: 40%; padding: 10px; box-sizing: border-box; border: 1px solid #ebeef5; text-align: center; color:#333;
    position: fixed; background-color: #fff; top:16px;left:50%;transform: translateX(-50%);z-index: 2147483647; font-size: 14px;line-height: 1.4; border-radius: 8px; box-shadow: 0 2px 12px 0 rgba(0,0,0,.1); `
}));
function dnotify(txt, type, time) {
  dnotifyEl.style.display = 'block';
  dnotifyEl.style.color = ['#333', '#67C23A', '#F56C6C', '#E6A23C'][type] // info, success, error, warning
  dnotifyEl.style.backgroundColor = ['#fff', '#f0f9eb', '#fef0f0', '#fdf6ec'][type]
  dnotifyEl.innerHTML = txt;
  clearTimeout(dnotifyTimer);
  dnotifyTimer = setTimeout(() => dnotifyEl.style.display = 'none', (time || 2) * 1000);
}

function formatSize(size) {
  if (!size) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  const i = Math.floor(Math.log(size) / Math.log(k));
  return (size / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i];
}