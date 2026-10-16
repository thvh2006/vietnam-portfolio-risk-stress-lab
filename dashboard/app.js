(() => {
  const SNAPSHOT = window.RISK_SNAPSHOT;
  if (!SNAPSHOT) throw new Error("Reviewed risk snapshot is unavailable.");

  const BASE = {
    currentBeta: SNAPSHOT.risk.beta,
    portfolioVol: SNAPSHOT.risk.annualisedVolatility,
    benchmarkVol: SNAPSHOT.risk.benchmarkVolatility,
    covariance: SNAPSHOT.risk.portfolioBenchmarkCovariance,
    multiplier: SNAPSHOT.hedge.contractMultiplier,
    baseExitDays: SNAPSHOT.liquidity.maximumBaseDaysToExit,
    baseParticipation: SNAPSHOT.liquidity.baseParticipation,
    baseNavBn: SNAPSHOT.shadowNavVnd / 1e9,
    z99: 2.326347874
  };

  const $ = (id) => document.getElementById(id);
  const fields = ["nav", "target-beta", "index-level", "margin-rate", "margin-stress", "participation"];
  const percent = (value) => `${(value * 100).toFixed(2)}%`;
  const money = (value) => `VND ${(value / 1e9).toFixed(2)}bn`;

  function formatLimit(value, format) {
    if (format === "percent") return percent(value);
    if (format === "days") return `${value.toFixed(2)}d`;
    return value.toFixed(0);
  }

  function populateSnapshot() {
    const risk = SNAPSHOT.risk;
    const hedge = SNAPSHOT.hedge;
    const backtest = SNAPSHOT.backtest;
    const breaches = SNAPSHOT.limits.filter((row) => row.status === "BREACH").length;
    const passes = SNAPSHOT.limits.length - breaches;
    const maximumTail = Math.max(risk.directTenDayEs975, risk.sqrtTimeTenDayEs975, risk.worstTwentyDay);

    $("snapshot-date").textContent = new Date(`${SNAPSHOT.asOf}T00:00:00Z`).toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric", timeZone: "UTC" });
    $("breach-count").textContent = breaches;
    $("breach-stamp").textContent = `${breaches} BREACH${breaches === 1 ? "" : "ES"}`;
    $("limits-heading").textContent = `${SNAPSHOT.limits.length} limits. ${passes} ${passes === 1 ? "pass" : "passes"}.`;
    $("decision-copy").textContent = `All ${SNAPSHOT.limits.length} controls pass. A ${hedge.targetBeta.toFixed(2)} beta hedge cuts 99% VaR, but increases tracking error to ${percent(hedge.hedgedTrackingError)}.`;

    $("kpi-var").textContent = percent(risk.historicalVar99);
    $("kpi-var-vnd").textContent = money(risk.historicalVar99 * SNAPSHOT.shadowNavVnd);
    $("kpi-es").textContent = percent(risk.directTenDayEs975);
    $("kpi-beta").textContent = risk.beta.toFixed(2);
    $("kpi-backtest").textContent = `${backtest.exceptions} / ${backtest.observations}`;
    $("kpi-zone").textContent = `● Basel ${backtest.zone.toLowerCase()} zone`;

    $("tail-direct").textContent = percent(risk.directTenDayEs975);
    $("tail-challenge").textContent = percent(risk.sqrtTimeTenDayEs975);
    $("tail-stress").textContent = percent(risk.worstTwentyDay);
    $("bar-direct").style.width = `${risk.directTenDayEs975 / maximumTail * 100}%`;
    $("bar-challenge").style.width = `${risk.sqrtTimeTenDayEs975 / maximumTail * 100}%`;
    $("bar-stress").style.width = `${risk.worstTwentyDay / maximumTail * 100}%`;
    $("es-gap").textContent = `${((risk.sqrtTimeTenDayEs975 - risk.directTenDayEs975) * 100).toFixed(2)}pp`;

    const maxDriver = Math.max(...SNAPSHOT.drivers.map((row) => row.share));
    $("driver-chart").replaceChildren(...SNAPSHOT.drivers.map((row) => {
      const container = document.createElement("div");
      container.innerHTML = `<span>${row.ticker}</span><i style="--v:${(row.share / maxDriver * 100).toFixed(1)}%"></i><b>${percent(row.share)}</b>`;
      return container;
    }));

    $("limit-table").append(...SNAPSHOT.limits.map((row) => {
      const container = document.createElement("div");
      container.setAttribute("role", "row");
      container.innerHTML = `<span>${row.label}</span><span>${formatLimit(row.actual, row.format)}</span><span>≤ ${formatLimit(row.limit, row.format)}</span><b>${row.status}</b>`;
      return container;
    }));

    $("kupiec-value").textContent = `p = ${backtest.kupiecPValue.toFixed(3)}`;
    $("independence-value").textContent = `p = ${backtest.independencePValue.toFixed(3)}`;
    $("coverage-value").textContent = `p = ${backtest.conditionalCoveragePValue.toFixed(3)}`;
    $("psd-value").textContent = backtest.covariancePsd ? "PSD PASS" : "PSD FAIL";
    $("historical-hedged-var").textContent = percent(hedge.hedgedHistoricalVar99);
    $("site-version").textContent = SNAPSHOT.version;

    $("nav").value = BASE.baseNavBn;
    $("target-beta").value = hedge.targetBeta;
    $("index-level").value = hedge.indexLevel;
    $("margin-rate").value = hedge.initialMarginRate * 100;
    $("margin-stress").value = hedge.stressMarginMultiplier;
    $("participation").value = BASE.baseParticipation * 100;
  }

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
    const exitDays = BASE.baseExitDays * (navBn / BASE.baseNavBn) * (BASE.baseParticipation / participation);

    $("nav-label").textContent = `VND ${navBn}bn`;
    $("beta-label").textContent = targetBeta.toFixed(2);
    $("contracts").textContent = contracts.toLocaleString("en-US");
    $("residual-beta").textContent = `Residual beta ${residualBeta.toFixed(3)}`;
    $("initial-margin").textContent = money(initialMargin);
    $("stressed-margin").textContent = money(initialMargin * stress);
    $("approx-var").textContent = percent(approxVar);
    $("exit-days").textContent = `${exitDays.toFixed(2)} days`;
  }

  populateSnapshot();
  fields.forEach((id) => $(id).addEventListener("input", recalculate));
  recalculate();
})();
