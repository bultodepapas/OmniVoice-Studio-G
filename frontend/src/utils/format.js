export function formatTime(s) {
  const m = Math.floor(s / 60);
  const sec = (s % 60).toFixed(1);
  return `${m}:${sec.padStart(4, '0')}`;
}

export async function probeAudioDuration(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const a = new Audio();
    const cleanup = () => URL.revokeObjectURL(url);
    const timeout = setTimeout(() => {
      cleanup();
      reject(new Error('probeAudioDuration timeout'));
    }, 10000);
    a.addEventListener('loadedmetadata', () => {
      clearTimeout(timeout);
      cleanup();
      resolve(isFinite(a.duration) ? a.duration : null);
    }, { once: true });
    a.addEventListener('error', () => {
      clearTimeout(timeout);
      cleanup();
      reject(new Error('probeAudioDuration failed to load'));
    }, { once: true });
    a.src = url;
  });
}
