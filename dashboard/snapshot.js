window.RISK_SNAPSHOT = {
  "asOf": "2026-09-30",
  "backtest": {
    "conditionalCoveragePValue": 0.9320096436687839,
    "covariancePsd": true,
    "exceptions": 2,
    "independencePValue": 0.8571765193042811,
    "kupiecPValue": 0.7419327009526282,
    "observations": 250,
    "zone": "green"
  },
  "drivers": [
    {
      "share": 0.13539514129893115,
      "ticker": "VIC"
    },
    {
      "share": 0.08341109618068414,
      "ticker": "HPG"
    },
    {
      "share": 0.08290082913558199,
      "ticker": "MWG"
    },
    {
      "share": 0.07854214909790204,
      "ticker": "FPT"
    },
    {
      "share": 0.05869955273033037,
      "ticker": "VHM"
    },
    {
      "share": 0.05629388608715029,
      "ticker": "VPB"
    },
    {
      "share": 0.05281374098163985,
      "ticker": "TCB"
    },
    {
      "share": 0.05065928570043559,
      "ticker": "MSN"
    }
  ],
  "hedge": {
    "contractMultiplier": 100000,
    "contracts": 152,
    "hedgedHistoricalVar99": 0.024624668544098234,
    "hedgedTrackingError": 0.06517187911830113,
    "indexLevel": 1906.81,
    "initialMarginRate": 0.17,
    "initialMarginVnd": 4927197040.0,
    "residualBeta": 0.7002019374008408,
    "stressMarginMultiplier": 1.5,
    "stressedMarginVnd": 7390795560.0,
    "targetBeta": 0.7
  },
  "limits": [
    {
      "actual": 0.10617876424715053,
      "format": "percent",
      "key": "single_name",
      "label": "Single-name weight",
      "limit": 0.11,
      "status": "PASS"
    },
    {
      "actual": 0.39832033593281335,
      "format": "percent",
      "key": "sector",
      "label": "Sector weight",
      "limit": 0.4,
      "status": "PASS"
    },
    {
      "actual": 0.39952009598080374,
      "format": "percent",
      "key": "top_five",
      "label": "Top-five weight",
      "limit": 0.45,
      "status": "PASS"
    },
    {
      "actual": 0.03398851873999015,
      "format": "percent",
      "key": "one_day_var_99",
      "label": "1-day VaR 99%",
      "limit": 0.035,
      "status": "PASS"
    },
    {
      "actual": 0.09298277008109858,
      "format": "percent",
      "key": "ten_day_es_975",
      "label": "Direct 10-day ES 97.5%",
      "limit": 0.12,
      "status": "PASS"
    },
    {
      "actual": 0.40243327671850065,
      "format": "days",
      "key": "liquidity_days_to_exit",
      "label": "Liquidity exit time",
      "limit": 5.0,
      "status": "PASS"
    },
    {
      "actual": 2,
      "format": "count",
      "key": "backtest_green_zone",
      "label": "Backtest exceptions",
      "limit": 4.0,
      "status": "PASS"
    }
  ],
  "liquidity": {
    "baseParticipation": 0.2,
    "maximumBaseDaysToExit": 0.40243327671850065
  },
  "risk": {
    "annualisedVolatility": 0.20222787289913338,
    "benchmarkVolatility": 0.20289094837734828,
    "beta": 0.9900370574008408,
    "directTenDayEs975": 0.09298277008109858,
    "historicalVar99": 0.03398851873999015,
    "portfolioBenchmarkCovariance": 0.04075461502228227,
    "sqrtTimeTenDayEs975": 0.12300706113288942,
    "worstTwentyDay": 0.2849540169524186
  },
  "shadowNavVnd": 100000000000,
  "version": "v1.1.1"
};
