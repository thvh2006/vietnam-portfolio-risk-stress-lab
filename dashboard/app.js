(() => {
  const BASE = {
    currentBeta: 0.9900370574008408,
    portfolioVol: 0.20222787289913338,
    benchmarkVol: 0.20289094837734828,
    covariance: 0.04075461502228227,
    multiplier: 100000,
    baseExitDays: 0.4024332767,
    z99: 2.326347874
  };

  const $ = (id) => document.getElementById(id);
  const fields = ["nav", "target-beta", "index-level", "margin-rate", "margin-stress", "participation"];
  const money = (value) => `VND ${(value / 1e9).toFixed(2)}bn`;

  function recalculate() {
    const navBn = Number($("nav").value);
    const nav = navBn * 1e9;
    const targetBeta = Number($("target-beta").value);
    const level = Math.max(Number($("index-level").value), 1);
    const marginRate = Math.max(Number($("margin-rate").value), 0) / 100;
    const stress = Math.max(Number($("margin-stress").value), 1);
    const participation = Math.max(Number($("participation").value), 1) / 100;
    const notional = level * BASE.multiplier;
    const contracts = Math.round(Math.max(0, (BASE.currentBeta - targetBeta) * nav / notional));
    const hedgeRatio = contracts * notional / nav;
    const residualBeta = BASE.currentBeta - hedgeRatio;
    const initialMargin = contracts * notional * marginRate;
    const hedgedVariance = Math.max(0, BASE.portfolioVol ** 2 + hedgeRatio ** 2 * BASE.benchmarkVol ** 2 - 2 * hedgeRatio * BASE.covariance);
    const approxVar = BASE.z99 * Math.sqrt(hedgedVariance) / Math.sqrt(252);
    const exitDays = BASE.baseExitDays * (navBn / 100) * (0.20 / participation);

    $("nav-label").textContent = `VND ${navBn}bn`;
    $("beta-label").textContent = targetBeta.toFixed(2);
    $("contracts").textContent = contracts.toLocaleString("en-US");
    $("residual-beta").textContent = `Residual beta ${residualBeta.toFixed(3)}`;
    $("initial-margin").textContent = money(initialMargin);
    $("stressed-margin").textContent = money(initialMargin * stress);
    $("approx-var").textContent = `${(approxVar * 100).toFixed(2)}%`;
    $("exit-days").textContent = `${exitDays.toFixed(2)} days`;
  }

  fields.forEach((id) => $(id).addEventListener("input", recalculate));
  recalculate();
})();
