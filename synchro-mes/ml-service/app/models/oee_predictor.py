"""
Preditor de OEE — Gradient Boosting + LSTM para séries temporais.
Prevê OEE, Availability, Performance e Quality para os próximos N dias.
"""
import numpy as np
import pandas as pd
import joblib
from datetime import date, datetime, timedelta
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder

from app.config import ML_MODELS_DIR

MODEL_PATH = ML_MODELS_DIR / "oee_predictor.joblib"

# Features derivadas de data
_DAY_OF_WEEK = "day_of_week"
_DAY_OF_MONTH = "day_of_month"
_MONTH = "month"
_SHIFT_ENC = "shift_enc"

# Targets
TARGETS = ["oee", "availability", "performance", "quality_rate"]


class OeePredictor:
    """Treina e prevê OEE por máquina usando Gradient Boosting."""

    def __init__(self):
        self.models: dict[str, GradientBoostingRegressor] = {}
        self.shift_encoder = LabelEncoder()
        self.is_trained = False
        self.last_trained: datetime | None = None
        self.samples_used = 0
        self.metrics: dict = {}
        self._load()

    # ── Feature Engineering ───────────────────────────────────

    @staticmethod
    def _build_features(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df[_DAY_OF_WEEK] = df["date"].dt.dayofweek
        df[_DAY_OF_MONTH] = df["date"].dt.day
        df[_MONTH] = df["date"].dt.month

        # Médias móveis (últimos 7 e 14 registros)
        for target in TARGETS:
            df[f"{target}_ma7"] = df[target].rolling(7, min_periods=1).mean()
            df[f"{target}_ma14"] = df[target].rolling(14, min_periods=1).mean()

        # Lag features
        for target in TARGETS:
            df[f"{target}_lag1"] = df[target].shift(1)
            df[f"{target}_lag7"] = df[target].shift(7)

        df.fillna(method="bfill", inplace=True)
        df.fillna(0, inplace=True)
        return df

    def _get_feature_cols(self) -> list[str]:
        base = [_DAY_OF_WEEK, _DAY_OF_MONTH, _MONTH, _SHIFT_ENC,
                "planned_time_minutes", "downtime_minutes", "total_produced",
                "good_produced", "rejected"]
        for t in TARGETS:
            base += [f"{t}_ma7", f"{t}_ma14", f"{t}_lag1", f"{t}_lag7"]
        return base

    # ── Training ──────────────────────────────────────────────

    def train(self, df: pd.DataFrame) -> dict:
        if df.empty or len(df) < 10:
            return {"status": "insufficient_data", "samples": len(df)}

        df = df.sort_values("date").reset_index(drop=True)

        # Encode shift
        df["shift"] = df["shift"].fillna("A")
        self.shift_encoder.fit(df["shift"])
        df[_SHIFT_ENC] = self.shift_encoder.transform(df["shift"])

        df = self._build_features(df)
        feature_cols = self._get_feature_cols()
        X = df[feature_cols].values

        self.metrics = {}
        for target in TARGETS:
            y = df[target].values
            model = GradientBoostingRegressor(
                n_estimators=100, max_depth=4, learning_rate=0.1,
                subsample=0.8, random_state=42,
            )
            scores = cross_val_score(model, X, y, cv=min(5, len(df) // 5 or 2), scoring="r2")
            model.fit(X, y)
            self.models[target] = model
            self.metrics[target] = {"r2": round(float(np.mean(scores)), 4)}

        self.is_trained = True
        self.last_trained = datetime.now()
        self.samples_used = len(df)
        self._save()

        return {
            "status": "trained",
            "samples": self.samples_used,
            "metrics": self.metrics,
        }

    # ── Prediction ────────────────────────────────────────────

    def predict(self, df: pd.DataFrame, horizon_days: int = 7) -> list[dict]:
        if not self.is_trained:
            return []

        df = df.sort_values("date").reset_index(drop=True)
        df["shift"] = df["shift"].fillna("A")
        df[_SHIFT_ENC] = self.shift_encoder.transform(df["shift"])
        df = self._build_features(df)
        feature_cols = self._get_feature_cols()

        forecasts = []
        last_row = df.iloc[-1].copy()
        last_date = pd.to_datetime(last_row["date"])

        for i in range(1, horizon_days + 1):
            future_date = last_date + timedelta(days=i)
            row = last_row.copy()
            row["date"] = future_date
            row[_DAY_OF_WEEK] = future_date.dayofweek
            row[_DAY_OF_MONTH] = future_date.day
            row[_MONTH] = future_date.month

            preds = {}
            for target in TARGETS:
                X = row[feature_cols].values.reshape(1, -1).astype(float)
                pred = float(self.models[target].predict(X)[0])
                pred = max(0, min(100, pred))
                preds[target] = round(pred, 1)
                # Atualizar lags para próxima iteração
                row[f"{target}_lag1"] = pred

            # Confidence decai com horizonte
            confidence = max(0.3, 1.0 - (i * 0.08))

            forecasts.append({
                "date": future_date.date(),
                "oee": preds["oee"],
                "availability": preds["availability"],
                "performance": preds["performance"],
                "quality_rate": preds["quality_rate"],
                "confidence": round(confidence, 2),
            })

            # Atualizar médias móveis simplificado
            for t in TARGETS:
                row[f"{t}_ma7"] = (row[f"{t}_ma7"] * 6 + preds[t]) / 7

        return forecasts

    def get_trend(self, forecasts: list[dict]) -> str:
        if len(forecasts) < 2:
            return "stable"
        first = forecasts[0]["oee"]
        last = forecasts[-1]["oee"]
        diff = last - first
        if diff > 2:
            return "up"
        if diff < -2:
            return "down"
        return "stable"

    # ── Persistence ───────────────────────────────────────────

    def _save(self):
        ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "models": self.models,
            "shift_encoder": self.shift_encoder,
            "last_trained": self.last_trained,
            "samples_used": self.samples_used,
            "metrics": self.metrics,
        }, MODEL_PATH)

    def _load(self):
        if MODEL_PATH.exists():
            data = joblib.load(MODEL_PATH)
            self.models = data["models"]
            self.shift_encoder = data["shift_encoder"]
            self.last_trained = data["last_trained"]
            self.samples_used = data["samples_used"]
            self.metrics = data.get("metrics", {})
            self.is_trained = True
