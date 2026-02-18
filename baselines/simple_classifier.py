"""
simple_classifier.py — TF-IDF + Logistic Regression baseline for
cryptographic misuse detection.

Usage:
    from baselines.simple_classifier import SimpleClassifier

    clf = SimpleClassifier(max_features=5000)
    clf.train(train_codes, train_labels)
    predictions = clf.predict(test_codes)
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from typing import List


class SimpleClassifier:
    """
    TF-IDF + Logistic Regression classifier for code snippets.

    Treats each code snippet as a bag-of-words document, extracts TF-IDF
    features, and trains a logistic regression model to predict
    'secure' vs 'insecure'.
    """

    def __init__(self, max_features: int = 5000, random_seed: int = 42):
        """
        Args:
            max_features: Maximum number of TF-IDF features.
            random_seed:  Random seed for reproducibility.
        """
        self.max_features = max_features
        self.random_seed = random_seed

        self._pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                max_features=max_features,
                token_pattern=r"(?u)\b\w[\w.]*\b",  # keep dots for API names
                ngram_range=(1, 2),
                sublinear_tf=True,
            )),
            ("clf", LogisticRegression(
                random_state=random_seed,
                max_iter=1000,
                solver="lbfgs",
            )),
        ])
        self._is_trained = False

    def train(self, codes: List[str], labels: List[str]) -> None:
        """
        Train the classifier.

        Args:
            codes:  List of Java source code strings.
            labels: Corresponding list of 'secure' / 'insecure' labels.
        """
        if len(codes) != len(labels):
            raise ValueError(
                f"codes ({len(codes)}) and labels ({len(labels)}) must have "
                f"the same length."
            )
        self._pipeline.fit(codes, labels)
        self._is_trained = True

    def predict(self, codes: List[str]) -> List[str]:
        """
        Predict labels for a list of code snippets.

        Args:
            codes: List of Java source code strings.

        Returns:
            List of predicted labels ('secure' or 'insecure').
        """
        if not self._is_trained:
            raise RuntimeError("Classifier has not been trained yet. Call train() first.")
        return self._pipeline.predict(codes).tolist()

    def predict_proba(self, codes: List[str]) -> List[dict]:
        """
        Predict class probabilities.

        Returns:
            List of dicts with 'secure' and 'insecure' probability keys.
        """
        if not self._is_trained:
            raise RuntimeError("Classifier has not been trained yet. Call train() first.")
        probas = self._pipeline.predict_proba(codes)
        classes = self._pipeline.classes_
        return [
            {cls: float(prob) for cls, prob in zip(classes, row)}
            for row in probas
        ]
