from datetime import date
from packages.decision.schemas import BaselineForecast, PlannedActivity, ScheduledItem, CashEvent
from packages.decision.scheduler import build_activity_schedule
from packages.decision.feasibility import analyze_feasibility

def test_activity_scheduler_signs():
    activity = PlannedActivity(
        activity_id="PROJ-01",
        name="Website Revamp",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 31),
        costs=[ScheduledItem(item_id="C1", date=date(2026, 12, 5), amount_pkr=50000)],
        receipts=[ScheduledItem(item_id="R1", date=date(2026, 12, 25), amount_pkr=120000)],
    )
    events = build_activity_schedule(activity)
    assert len(events) == 2
    assert events[0].amount_pkr == -50000
    assert events[1].amount_pkr == 120000

def test_guide_example_funding_gap():
    # Document example: PKR 200,000 available, 100,000/month spend, first receipt in month 5
    forecast = BaselineForecast(
        business_id="BIZ-01",
        as_of_date=date(2026, 12, 1),
        opening_balance_pkr=200000,
        minimum_reserve_pkr=50000,
        events=[],
    )
    costs = [
        ScheduledItem(item_id=f"M{i}", date=date(2026 + (11 + i) // 12, (11 + i) % 12 + 1, 1), amount_pkr=100000)
        for i in range(5)
    ]
    receipts = [
        ScheduledItem(item_id="REC-1", date=date(2027, 4, 15), amount_pkr=600000)
    ]
    activity = PlannedActivity(
        activity_id="PROJ-10M",
        name="10 Month Project",
        start_date=date(2026, 12, 1),
        end_date=date(2027, 5, 1),
        costs=costs,
        receipts=receipts,
    )

    result = analyze_feasibility(forecast, activity)
    assert result.is_feasible is False
    # Dec 1: 200k - 100k = 100k (ok)
    # Jan 1: 100k - 100k = 0 (< 50k reserve -> first breach!)
    assert result.first_breach_date == date(2027, 1, 1)
    # Lowest balance on Apr 1 before receipt: 200k - 500k = -300k. Gap to 50k reserve = 350k
    assert result.minimum_balance_pkr == -300000
    assert result.max_funding_gap_pkr == 350000

def test_feasible_project_with_baseline_inflows():
    forecast = BaselineForecast(
        business_id="BIZ-01",
        as_of_date=date(2026, 12, 1),
        opening_balance_pkr=200000,
        minimum_reserve_pkr=50000,
        events=[
            CashEvent(
                event_id="EVT-BASE-1",
                date=date(2026, 12, 10),
                amount_pkr=150000,
                source_type="receivable",
                source_id="INV-01",
            )
        ],
    )
    activity = PlannedActivity(
        activity_id="PROJ-SAFE",
        name="Small Consulting",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 30),
        costs=[ScheduledItem(item_id="C1", date=date(2026, 12, 15), amount_pkr=150000)],
        receipts=[ScheduledItem(item_id="R1", date=date(2026, 12, 28), amount_pkr=250000)],
    )

    result = analyze_feasibility(forecast, activity)
    assert result.is_feasible is True
    assert result.first_breach_date is None
    assert result.max_funding_gap_pkr == 0