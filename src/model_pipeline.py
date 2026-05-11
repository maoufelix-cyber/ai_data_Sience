import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from sklearn.pipeline import Pipeline

from src.data_pipeline import build_preprocessing_pipeline


def build_pipeline(numeric_features, categorical_features, model_type="random_forest") -> Pipeline:
    if model_type == "logistic_regression":
        estimator = LogisticRegression(max_iter=1000, random_state=42)
    else:
        estimator = RandomForestClassifier(n_estimators=200, random_state=42)

    preprocessor = build_preprocessing_pipeline(numeric_features, categorical_features)
    pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", estimator)])
    return pipeline


def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    pred = model.predict(X_test)
    proba = model.predict_proba(X_test)[:, 1]
    report = classification_report(y_test, pred, output_dict=True)
    auc = roc_auc_score(y_test, proba)
    matrix = confusion_matrix(y_test, pred)

    metrics = {
        "roc_auc": auc,
        "confusion_matrix": matrix.tolist(),
        "classification_report": report,
    }
    return metrics


def save_model(model, path: str):
    joblib.dump(model, path)


def load_model(path: str):
    return joblib.load(path)
