---
name: lab-inventory-predictor
description: Predict depletion time of critical lab reagents based on experimental usage frequency and automatically generate purchase alerts for laboratory inventory management.
---

# Lab Inventory Predictor

## Function Overview

This skill is used for laboratory inventory management, predicting reagent depletion time by analyzing historical usage frequency, and automatically generating reminders when purchases are needed.

## Core Capabilities

1. **Inventory Tracking** - Record current reagent stock levels
2. **Usage Frequency Analysis** - Calculate consumption rate based on experiment records
3. **Depletion Prediction** - Predict reagent depletion date based on consumption rate
4. **Purchase Alerts** - Generate alerts before reagents are about to deplete
5. **Safety Stock Alerts** - Alert when inventory falls below safety threshold

## Usage

### Command Line Call

```bash
# View all reagent status
openclaw skill lab-inventory-predictor --action status

# Add or update reagent information
openclaw skill lab-inventory-predictor --action add-reagent \
  --name "PBS Buffer" \
  --current-stock 500 \
  --unit "ml" \
  --safety-days 7

# Record experiment consumption
openclaw skill lab-inventory-predictor --action record-usage \
  --name "PBS Buffer" \
  --amount 50 \
  --experiment "Cell Culture Experiment #2024-001"

# Get purchase alerts
openclaw skill lab-inventory-predictor --action alerts

# Generate prediction report
openclaw skill lab-inventory-predictor --action report
```

### Python API

```python
from skills.lab_inventory_predictor import InventoryPredictor

# Initialize
predictor = InventoryPredictor("/path/to/inventory.json")

# Add reagent
predictor.add_reagent(
    name="PBS Buffer",
    current_stock=500,
    unit="ml",
    safety_days=7,
    lead_time_days=3
)

# Record usage
predictor.record_usage("PBS Buffer", 50, "Experiment #001")

# Get prediction
prediction = predictor.predict_depletion("PBS Buffer")
print(f"Predicted depletion time: {prediction['depletion_date']}")

# Get purchase alerts
alerts = predictor.get_alerts()
```

## Data Structure

### Reagent Record

```json
{
  "name": "PBS Buffer",
  "current_stock": 500,
  "unit": "ml",
  "safety_stock": 100,
  "safety_days": 7,
  "lead_time_days": 3,
  "usage_history": [
    {
      "date": "2024-01-15",
      "amount": 50,
      "experiment": "Cell Culture #001"
    }
  ],
  "daily_consumption_rate": 10.5,
  "predicted_depletion_date": "2024-02-01",
  "last_updated": "2024-01-15T10:30:00"
}
```

## Prediction Algorithm

### Consumption Rate Calculation

```
daily_consumption = Σ(usage_amount) / days_span
```

### Depletion Date Prediction

```
days_until_depletion = current_stock / daily_consumption
depletion_date = today + days_until_depletion
```

### Purchase Alert Trigger Conditions

1. **Based on depletion time**: When `days_until_depletion <= safety_days + lead_time_days`
2. **Based on safety stock**: When `current_stock <= safety_stock`

## Configuration File

Default data storage location: `~/.openclaw/workspace/data/lab-inventory.json`

Configuration example:

```json
{
  "settings": {
    "default_safety_days": 7,
    "default_lead_time_days": 3,
    "prediction_lookback_days": 30
  },
  "reagents": []
}
```

## Dependencies

- Python >= 3.8
- No external dependencies (uses only standard library)

## Version History

- v1.0.0 (2024-02) - Initial version, supports basic prediction and alert functions

---

**Author**: OpenClaw Skill Framework  
**License**: MIT
