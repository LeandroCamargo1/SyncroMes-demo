"""
Preditor de Paradas (Downtime) — Random Forest Classifier.
Prevê probabilidade de parada por categoria nas próximas 24h.
"""
import numpy as np
import pandas as pd
import joblib
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder

from app.config import ML_MODELS_DIR

MODEL_PATH = ML_MODELS_DIR / "downtime_predictor.joblib"

CATEGORIES = ["mecanica", "eletrica", "setup", "processo", "qualidade", "falta_material", "programada"]


class DowntimePredictor:
    """Prevê risco de parada por categoria usando Random Forest."""

    def __init__(self):
        self.model: RandomForestClassifier | None = None
        self.shift_encoder = LabelEncoder()
        self.category_encoder = LabelEncoder()
        self.is_trained = False
        self.last_trained: datetime | None = None
        self.samples_used = 0
        self.metrics: dict = {}
        self._load()

    # ── Feature Engineering ───────────────────────────────────

    @staticmethod
    def _build_features(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["start_time"] = pd.to_datetime(df["start_time"])
        df["hour"] = df["start_time"].dt.hour
        df["day_of_week"] = df["start_time"].dt.dayofweek
        df["month"] = df["start_time"].dt.month
        df["is_night"] = df["hour"].apply(lambda h: 1 if h < 6 or h >= 22 else 0)

        # Frequência por máquina (quantas paradas nos últimos registros)
        df["machine_freq"] = df.groupby("machine_code")["machine_code"].transform("count")

        # Duração média por máquina
        df["machine_avg_dur"] = df.groupby("machine_code")["duration_minutes"].transform("mean")

        return df

    # ── Training ──────────────────────────────────────────────

    def train(self, df: pd.DataFrame) -> dict:
        if df.empty or len(df) < 20:
            return {"status": "insufficient_data", "samples": len(df)}

        df = self._build_features(df)

        # Encode categoricals
        df["shift"] = df["shift"].fillna("A")
        self.shift_encoder.fit(df["shift"])
        df["shift_enc"] = self.shift_encoder.transform(df["shift"])

        self.category_encoder.fit(CATEGORIES)
        # Filtrar só categorias conhecidas
        df = df[df["category"].isin(CATEGORIES)].copy()
        if df.empty:
            return {"status": "no_valid_categories", "samples": 0}
        df["category_enc"] = self.category_encoder.transform(df["category"])

        feature_cols = ["hour", "day_of_week", "month", "is_night",
                        "shift_enc", "machine_freq", "machine_avg_dur",
                        "duration_minutes"]
        X = df[feature_cols].values
        y = df["category_enc"].values

        self.model = RandomForestClassifier(
            n_estimators=100, max_depth=8, random_state=42, class_weight="balanced",
        )
        cv_folds = min(5, max(2, len(df) // 10))
        scores = cross_val_score(self.model, X, y, cv=cv_folds, scoring="accuracy")
        self.model.fit(X, y)

        self.is_trained = True
        self.last_trained = datetime.now()
        self.samples_used = len(df)
        self.metrics = {"accuracy": round(float(np.mean(scores)), 4)}
        self._save()

        return {
            "status": "trained",
            "samples": self.samples_used,
            "metrics": self.metrics,
        }

    # ── Prediction ────────────────────────────────────────────

    def predict(self, df_history: pd.DataFrame, machine_code: str) -> dict:
        """Retorna risco de parada por categoria para uma máquina."""
        if not self.is_trained or self.model is None:
            return {"overall_risk": 0, "risks": [], "actions": []}

        machine_data = df_history[df_history["machine_code"] == machine_code]

        # Construir feature para "agora"
        now = datetime.now()
        freq = len(machine_data)
        avg_dur = float(machine_data["duration_minutes"].mean()) if not machine_data.empty else 0

        feature_vec = np.array([[
            now.hour, now.weekday(), now.month,
            1 if now.hour < 6 or now.hour >= 22 else 0,
            0,  # shift_enc default
            freq, avg_dur, avg_dur,
        ]])

        # Probabilidades por classe
        proba = self.model.predict_proba(feature_vec)[0]
        classes = self.category_encoder.inverse_transform(self.model.classes_)

        risks = []
        for i, cat in enumerate(classes):
            cat_data = machine_data[machine_data["category"] == cat]
            top_reason = ""
            if not cat_data.empty:
                top_reason = cat_data["reason"].mode().iloc[0] if not cat_data["reason"].mode().empty else ""
            risks.append({
                "category": cat,
                "probability": round(float(proba[i]), 3),
                "avg_duration_minutes": round(float(cat_data["duration_minutes"].mean()), 1) if not cat_data.empty else 0,
                "top_reason": top_reason,
            })

        risks.sort(key=lambda r: r["probability"], reverse=True)
        overall_risk = float(max(proba))

        # Ações recomendadas
        actions = []
        if overall_risk > 0.6:
            actions.append(f"Atenção: risco alto de parada por {risks[0]['category']}")
        if any(r["category"] == "mecanica" and r["probability"] > 0.3 for r in risks):
            actions.append("Verificar manutenção preventiva da máquina")
        if any(r["category"] == "falta_material" and r["probability"] > 0.3 for r in risks):
            actions.append("Confirmar estoque de materiais para próximo turno")

        risk_level = "low"
        if overall_risk > 0.7:
            risk_level = "critical"
        elif overall_risk > 0.5:
            risk_level = "high"
        elif overall_risk > 0.3:
            risk_level = "medium"

        return {
            "overall_risk": round(overall_risk, 3),
            "risk_level": risk_level,
            "risks": risks,
            "actions": actions,
        }

    # ── Persistence ───────────────────────────────────────────

    def _save(self):
        ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "shift_encoder": self.shift_encoder,
            "category_encoder": self.category_encoder,
            "last_trained": self.last_trained,
            "samples_used": self.samples_used,
            "metrics": self.metrics,
        }, MODEL_PATH)

    def _load(self):
        if MODEL_PATH.exists():
            data = joblib.load(MODEL_PATH)
            self.model = data["model"]
            self.shift_encoder = data["shift_encoder"]
            self.category_encoder = data["category_encoder"]
            self.last_trained = data["last_trained"]
            self.samples_used = data["samples_used"]
            self.metrics = data.get("metrics", {})
            self.is_trained = True
