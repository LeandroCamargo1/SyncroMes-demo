"""
Preditor de Manutenção de Moldes — Regras + ML.
Combina heurísticas baseadas em ciclos com aprendizado de padrões de manutenção.
"""
import numpy as np
import pandas as pd
import joblib
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor

from app.config import ML_MODELS_DIR

MODEL_PATH = ML_MODELS_DIR / "maintenance_predictor.joblib"


class MaintenancePredictor:
    """Prevê dias restantes até manutenção necessária para cada molde."""

    def __init__(self):
        self.model: RandomForestRegressor | None = None
        self.is_trained = False
        self.last_trained: datetime | None = None
        self.samples_used = 0
        self.metrics: dict = {}
        self._load()

    # ── Training ──────────────────────────────────────────────

    def train(self, molds_df: pd.DataFrame, maintenances_df: pd.DataFrame) -> dict:
        """Treina modelo de predição de intervalo entre manutenções."""
        if maintenances_df.empty or len(maintenances_df) < 5:
            return {"status": "insufficient_data", "samples": len(maintenances_df)}

        # Calcular intervalo entre manutenções por molde
        maint = maintenances_df.copy()
        maint["start_time"] = pd.to_datetime(maint["start_time"])
        maint = maint.sort_values(["mold_code", "start_time"])

        training_data = []
        for mold_code, group in maint.groupby("mold_code"):
            if len(group) < 2:
                continue
            group = group.reset_index(drop=True)
            for i in range(1, len(group)):
                interval_days = (group.loc[i, "start_time"] - group.loc[i - 1, "start_time"]).days
                if interval_days <= 0:
                    continue

                mold_info = molds_df[molds_df["code"] == mold_code]
                cavities = int(mold_info["cavities"].iloc[0]) if not mold_info.empty else 1
                max_cycles = int(mold_info["max_cycles"].iloc[0]) if not mold_info.empty and pd.notna(mold_info["max_cycles"].iloc[0]) else 50000

                duration = float(group.loc[i - 1, "duration_hours"]) if pd.notna(group.loc[i - 1, "duration_hours"]) else 2.0
                maint_type_enc = {"preventiva": 0, "corretiva": 1, "limpeza": 2}.get(
                    group.loc[i - 1, "maintenance_type"], 0
                )

                training_data.append({
                    "cavities": cavities,
                    "max_cycles": max_cycles,
                    "prev_duration_hours": duration,
                    "prev_type": maint_type_enc,
                    "interval_days": interval_days,
                })

        if len(training_data) < 5:
            return {"status": "insufficient_data", "samples": len(training_data)}

        train_df = pd.DataFrame(training_data)
        feature_cols = ["cavities", "max_cycles", "prev_duration_hours", "prev_type"]
        X = train_df[feature_cols].values
        y = train_df["interval_days"].values

        self.model = RandomForestRegressor(
            n_estimators=50, max_depth=5, random_state=42,
        )
        self.model.fit(X, y)

        self.is_trained = True
        self.last_trained = datetime.now()
        self.samples_used = len(training_data)
        self.metrics = {"samples": len(training_data)}
        self._save()

        return {
            "status": "trained",
            "samples": self.samples_used,
            "metrics": self.metrics,
        }

    # ── Prediction ────────────────────────────────────────────

    def predict(self, molds_df: pd.DataFrame, maintenances_df: pd.DataFrame) -> list[dict]:
        """Gera relatório de saúde e previsão de manutenção para cada molde."""
        now = datetime.now()
        reports = []

        for _, mold in molds_df.iterrows():
            code = mold["code"]
            name = mold["name"]
            current_cycles = int(mold.get("total_cycles", 0) or 0)
            max_cycles = int(mold["max_cycles"]) if pd.notna(mold.get("max_cycles")) else None
            last_maint = pd.to_datetime(mold["last_maintenance"]) if pd.notna(mold.get("last_maintenance")) else None

            # Uso de ciclos
            cycle_usage_pct = None
            if max_cycles and max_cycles > 0:
                cycle_usage_pct = round(current_cycles / max_cycles * 100, 1)

            # Dias desde última manutenção
            days_since = None
            if last_maint:
                days_since = (now - last_maint).days

            # ── Predição ML do intervalo ──────────────────────
            predicted_days = None
            if self.is_trained and self.model is not None:
                mold_maint = maintenances_df[maintenances_df["mold_code"] == code]
                if not mold_maint.empty:
                    last_entry = mold_maint.sort_values("start_time").iloc[-1]
                    dur = float(last_entry["duration_hours"]) if pd.notna(last_entry.get("duration_hours")) else 2.0
                    m_type = {"preventiva": 0, "corretiva": 1, "limpeza": 2}.get(
                        last_entry.get("maintenance_type", "preventiva"), 0
                    )
                    cavities = int(mold.get("cavities", 1) or 1)
                    mc = max_cycles or 50000

                    X = np.array([[cavities, mc, dur, m_type]])
                    pred = float(self.model.predict(X)[0])
                    remaining = max(0, int(pred) - (days_since or 0))
                    predicted_days = remaining

            # ── Health Score (heurístico + ML) ────────────────
            health = 100.0
            if cycle_usage_pct is not None:
                health -= cycle_usage_pct * 0.5  # Penaliza uso de ciclos
            if days_since is not None and days_since > 30:
                health -= min(30, (days_since - 30) * 0.5)  # Penaliza tempo sem manutenção
            if predicted_days is not None and predicted_days < 7:
                health -= (7 - predicted_days) * 3
            health = max(0, min(100, round(health, 1)))

            # Risk level
            if health < 30:
                risk = "critical"
                rec = "Manutenção urgente recomendada"
            elif health < 50:
                risk = "high"
                rec = "Agendar manutenção preventiva em breve"
            elif health < 70:
                risk = "medium"
                rec = "Monitorar condição do molde"
            else:
                risk = "low"
                rec = "Operação normal"

            reports.append({
                "mold_code": code,
                "mold_name": name,
                "current_cycles": current_cycles,
                "max_cycles": max_cycles,
                "cycle_usage_pct": cycle_usage_pct,
                "days_since_last_maintenance": days_since,
                "predicted_days_to_maintenance": predicted_days,
                "health_score": health,
                "risk_level": risk,
                "recommendation": rec,
            })

        reports.sort(key=lambda r: r["health_score"])
        return reports

    # ── Persistence ───────────────────────────────────────────

    def _save(self):
        ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "last_trained": self.last_trained,
            "samples_used": self.samples_used,
            "metrics": self.metrics,
        }, MODEL_PATH)

    def _load(self):
        if MODEL_PATH.exists():
            data = joblib.load(MODEL_PATH)
            self.model = data["model"]
            self.last_trained = data["last_trained"]
            self.samples_used = data["samples_used"]
            self.metrics = data.get("metrics", {})
            self.is_trained = True
