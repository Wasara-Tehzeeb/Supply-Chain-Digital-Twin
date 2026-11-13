
from src.ml.predict_supplier_delay import predict_supplier_delay
from src.digital_twin.load_network_data import load_supply_chain_data


def get_ml_supplier_lead_time(
    product_id=1,
    distance_km=600,
    order_quantity=500,
    weather_severity=2,
    traffic_level=2,
):
    data = load_supply_chain_data(product_id)

    supplier = data["supplier"]

    prediction = predict_supplier_delay(
        supplier_id=supplier["id"],
        supplier_reliability=supplier["reliability"],
        expected_lead_time=supplier["lead_time"],
        distance_km=distance_km,
        order_quantity=order_quantity,
        weather_severity=weather_severity,
        traffic_level=traffic_level,
    )

    base_lead_time = supplier["lead_time"]

    # Assumption: a predicted delay adds three days.
    # The classifier predicts delay likelihood, not duration.
    additional_delay = (
        3 if prediction["predicted_delayed"] else 0
    )

    adjusted_lead_time = (
        base_lead_time + additional_delay
    )

    return {
        "supplier_id": supplier["id"],
        "supplier_name": supplier["name"],
        "base_lead_time": base_lead_time,
        "delay_probability": prediction["delay_probability"],
        "risk_level": prediction["risk_level"],
        "predicted_delayed": prediction["predicted_delayed"],
        "additional_delay": additional_delay,
        "adjusted_lead_time": adjusted_lead_time,
    }


if __name__ == "__main__":
    result = get_ml_supplier_lead_time(product_id=1)

    print("\nML-BASED SUPPLIER LEAD TIME")
    print("-" * 60)

    for key, value in result.items():
        print(f"{key}: {value}")
