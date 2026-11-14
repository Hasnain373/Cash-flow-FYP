from typing import List
from .schemas import PlannedActivity, CashEvent

def build_activity_schedule(activity: PlannedActivity, scenario_id: str = "planned") -> List[CashEvent]:
    """Converts planned project costs and milestone receipts into dated CashEvents."""
    events: List[CashEvent] = []

    # Outflows (Costs are negative)
    for cost in activity.costs:
        events.append(
            CashEvent(
                event_id=f"EVT-{activity.activity_id}-{cost.item_id}",
                date=cost.date,
                amount_pkr=-abs(cost.amount_pkr),
                source_type="planned_activity",
                source_id=f"{activity.activity_id}:{cost.item_id}",
                is_estimated=True,
                scenario_id=scenario_id,
            )
        )

    # Inflows (Receipts are positive)
    for receipt in activity.receipts:
        events.append(
            CashEvent(
                event_id=f"EVT-{activity.activity_id}-{receipt.item_id}",
                date=receipt.date,
                amount_pkr=abs(receipt.amount_pkr),
                source_type="planned_activity",
                source_id=f"{activity.activity_id}:{receipt.item_id}",
                is_estimated=True,
                scenario_id=scenario_id,
            )
        )

    events.sort(key=lambda e: e.date)
    return events