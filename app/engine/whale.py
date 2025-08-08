
# Stub: Hier könntest du Whale-Alerts verarbeiten.
# Idee: Wenn große Zuflüsse zur Börse, negatives Signal; große Abflüsse, positives Signal.
# Dieses Modul liefert einen Score in [-0.2, 0.2], der zum Gesamtscore addiert wird.

import pandas as pd

def whale_score(index_like, enabled: bool=False) -> pd.Series:
    if not enabled:
        return pd.Series(0, index=index_like, name='whale')
    # Platzhalter: zufällig 0 -> in Produktion durch echte Daten ersetzen
    return pd.Series(0, index=index_like, name='whale')
