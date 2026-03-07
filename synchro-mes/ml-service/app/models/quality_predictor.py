"""
Preditor de Qualidade — Gradient Boosting.
Prevê taxa de refugo e probabilidade de defeitos por tipo.
"""
import numpy as np
import pandas as pd
import joblib
from datetime import datetime
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score

from app.config import ML_MODELS_DIR

MODEL_PATH = ML_MODELS_DIR / "quality_predictor.joblib"

DEFECT_TYPES = ["rebarba", "bolha", "mancha", "dimensional"]


class QualityPredictor:
    """Prevê taxa de refugo e tipos de defeito mais prováveis."""

    def __init__(self):
        self.scrap_model: GradientBoostingRegressor | None = None
        self.defect_model: GradientBoostingClassifier | None = None
        self.is_trained = False
        self.last_trained: datetime | None = None
        self.samples_used = 0
        self.metrics: dict = {}
        self._load()

    # ── Training ──────────────────────────────────────────────

    def train(self, quality_df: pd.DataFrame, loss_df: pd.DataFrame, production_df: pd.DataFrame) -> dict:
        """Treina modelos de qualidade usando dados de medições, perdas e produção."""
        total_samples = len(quality_df) + len(loss_df)
        if total_samples < 15:
            return {"status": "insufficient_data", "samples": total_samples}

        self.metrics = {}

        # ── Modelo 1: Predição de taxa de refugo (por máquina/produto)
        if not production_df.empty and len(production_df) >= 10:
            prod = production_df.copy()
            prod["timestamp"] = pd.to_datetime(prod["timestamp"])
            prod["hour"] = prod["timestamp"].dt.hour
            prod["day_of_week"] = prod["timestamp"].dt.dayofweek
            prod["total"] = prod["quantity_good"] + prod["quantity_rejected"]
            prod = prod[prod["total"] > 0].copy()
            prod["scrap_rate"] = prod["quantity_rejected"] / prod["total"] * 100

            if len(prod) >= 10:
                feature_cols = ["hour", "day_of_week", "quantity_good",
                                "quantity_rejected", "cavities"]
                for col in feature_cols:
                    prod[col] = pd.to_numeric(prod[col], errors="coerce").fillna(0)

                X = prod[feature_cols].values
                y = prod["scrap_rate"].values

                self.scrap_model = GradientBoostingRegressor(
                    n_estimators=80, max_depth=3, learning_rate=0.1, random_state=42,
                )
                cv = min(5, max(2, len(prod) // 5))
                scores = cross_val_score(self.scrap_model, X, y, cv=cv, scoring="r2")
                self.scrap_model.fit(X, y)
                self.metrics["scrap_r2"] = round(float(np.mean(scores)), 4)

        # ── Modelo 2: Predição de tipo de defeito
        if not quality_df.empty and len(quality_df) >= 10:
            qdf = quality_df.copy()
            qdf = qdf[qdf["defect_type"].notna() & qdf["defect_type"].isin(DEFECT_TYPES)].copy()

            if len(qdf) >= 10:
                qdf["timestamp"] = pd.to_datetime(qdf["timestamp"])
                qdf["hour"] = qdf["timestamp"].dt.hour
                qdf["day_of_week"] = qdf["timestamp"].dt.dayofweek

                qdf["deviation"] = (qdf["measured_value"].fillna(0) - qdf["nominal_value"].fillna(0)).abs()

                feature_cols = ["hour", "day_of_week", "deviation",
                                "nominal_value", "tolerance_upper", "tolerance_lower"]
                for col in feature_cols:
                    qdf[col] = pd.to_numeric(qdf[col], errors="coerce").fillna(0)

                X = qdf[feature_cols].values
                y_labels = qdf["defect_type"].values

                self.defect_model = GradientBoostingClassifier(
                    n_estimators=80, max_depth=4, learning_rate=0.1, random_state=42,
                )
                cv = min(5, max(2, len(qdf) // 5))
                scores = cross_val_score(self.defect_model, X, y_labels, cv=cv, scoring="accuracy")
                self.defect_model.fit(X, y_labels)
                self.metrics["defect_accuracy"] = round(float(np.mean(scores)), 4)

        self.is_trained = self.scrap_model is not None or self.defect_model is not None
        self.last_trained = datetime.now()
        self.samples_used = total_samples
        self._save()

        return {
            "status": "trained",
            "samples": self.samples_used,
            "metrics": self.metrics,
        }

    # ── Prediction ────────────────────────────────────────────

    def predict(self, production_df: pd.DataFrame, spc_df: pd.DataFrame, machine_code: str, product_code: str | None = None) -> dict:
        if not self.is_trained:
            return {"scrap_rate": 0, "risk_level": "unknown", "defects": [], "spc_alerts": []}

        # Predição de refugo
        predicted_scrap = 0.0
        if self.scrap_model is not None and not production_df.empty:
            recent = production_df[production_df["machine_code"] == machine_code].head(10)
            if not recent.empty:
                row = recent.iloc[0]
                hour = pd.to_datetime(row.get("timestamp", datetime.now())).hour if pd.notna(row.get("timestamp")) else datetime.now().hour
                X = np.array([[hour, datetime.now().weekday(),
                               float(row.get("quantity_good", 0)),
                               float(row.get("quantity_rejected", 0)),
                               float(row.get("cavities", 1))]])
                predicted_scrap = max(0, float(self.scrap_model.predict(X)[0]))

        # Predição de defeitos
        defects = []
        if self.defect_model is not None:
            now = datetime.now()
            X = np.array([[now.hour, now.weekday(), 0.1, 50.0, 50.5, 49.5]])
            proba = self.defect_model.predict_proba(X)[0]
            classes = self.defect_model.classes_
            for i, dt in enumerate(classes):
                defects.append({
                    "defect_type": dt,
                    "probability": round(float(proba[i]), 3),
                    "expected_rate_pct": round(float(proba[i]) * predicted_scrap, 2),
                })
            defects.sort(key=lambda d: d["probability"], reverse=True)

        # Alertas SPC
        spc_alerts = []
        if not spc_df.empty:
            machine_spc = spc_df[spc_df["machine_code"] == machine_code]
            ooc = machine_spc[machine_spc["is_out_of_control"] == True]
            if len(ooc) > 0:
                for param in ooc["parameter_name"].unique():
                    count = len(ooc[ooc["parameter_name"] == param])
                    spc_alerts.append(f"Parâmetro '{param}': {count} pontos fora de controle")

        risk_level = "low"
        if predicted_scrap > 5:
            risk_level = "critical"
        elif predicted_scrap > 3:
            risk_level = "high"
        elif predicted_scrap > 1:
            risk_level = "medium"

        return {
            "predicted_scrap_rate": round(predicted_scrap, 2),
            "risk_level": risk_level,
            "defects": defects,
            "spc_alerts": spc_alerts,
        }

    # ── Persistence ───────────────────────────────────────────

    def _save(self):
        ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "scrap_model": self.scrap_model,
            "defect_model": self.defect_model,
            "last_trained": self.last_trained,
            "samples_used": self.samples_used,
            "metrics": self.metrics,
        }, MODEL_PATH)

    def _load(self):
        if MODEL_PATH.exists():
            data = joblib.load(MODEL_PATH)
            self.scrap_model = data["scrap_model"]
            self.defect_model = data["defect_model"]
            self.last_trained = data["last_trained"]
            self.samples_used = data["samples_used"]
            self.metrics = data.get("metrics", {})
            self.is_trained = True
