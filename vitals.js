let vitals = { LCP: 0, FID: 0, CLS: 0 };

new PerformanceObserver((entryList) => {
  for (const entry of entryList.getEntries()) {
    vitals.LCP = entry.renderTime || entry.loadTime;
  }
}).observe({ type: "largest-contentful-paint", buffered: true });

new PerformanceObserver((entryList) => {
  vitals.CLS += entryList.getEntries()[0].value;
}).observe({ type: "layout-shift", buffered: true });

window.addEventListener("click", (event) => {
  const delay = performance.now() - event.timeStamp;
  vitals.FID = Math.max(vitals.FID, delay);
});

window.getVitals = () => vitals;
