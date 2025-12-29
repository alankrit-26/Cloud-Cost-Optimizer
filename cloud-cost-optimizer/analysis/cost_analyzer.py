from collections import defaultdict

def analyze_costs(billing_records: list, budget: float) -> dict:
    total_cost = sum(item["cost_inr"] for item in billing_records)

    service_costs = defaultdict(float)
    for item in billing_records:
        service_costs[item["service"]] += item["cost_inr"]

    high_cost_services = {
        service: cost
        for service, cost in service_costs.items()
        if cost == max(service_costs.values())
    }

    return {
        "total_monthly_cost": round(total_cost, 2),
        "budget": budget,
        "budget_variance": round(total_cost - budget, 2),
        "service_costs": {
            service: round(cost, 2)
            for service, cost in service_costs.items()
        },
        "high_cost_services": {
            service: round(cost, 2)
            for service, cost in high_cost_services.items()
        },
        "is_over_budget": total_cost > budget
    }
