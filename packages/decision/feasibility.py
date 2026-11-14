from collections import defaultdict
from datetime import timedelta
from typing import Optional
from .schemas import BaselineForecast, PlannedActivity, FeasibilityResult, DailyBalance
from .scheduler import build_activity_schedule

def analyze_feasibility(forecast: BaselineForecast, activity: PlannedActivity) -> FeasibilityResult:
    """Merges planned activity events with baseline forecast and computes funding gaps."""
    project_events = build_activity_schedule(activity)
    all_events = forecast.events + project_events

    if not all_events:
        is_feasible = forecast.opening_balance_pkr >= forecast.minimum_reserve_pkr
        gap = max(0, forecast.minimum_reserve_pkr - forecast.opening_balance_pkr)
        return FeasibilityResult(
            activity_id=activity.activity_id,
            is_feasible=is_feasible,
            minimum_balance_pkr=forecast.opening_balance_pkr,
            first_breach_date=forecast.as_of_date if not is_feasible else None,
            max_funding_gap_pkr=gap,
            project_events=project_events,
            timeline=[],
        )

    # Group net cash flow by date
    daily_net = defaultdict(int)
    for event in all_events:
        if event.date >= forecast.as_of_date:
            daily_net[event.date] += event.amount_pkr

    start_date = forecast.as_of_date
    end_date = max(max(daily_net.keys()), activity.end_date)

    current_balance = forecast.opening_balance_pkr
    min_balance = current_balance
    first_breach_date: Optional[date] = None
    max_gap = 0
    timeline = []

    curr_date = start_date
    while curr_date <= end_date:
        net_change = daily_net[curr_date]
        current_balance += net_change

        is_breach = current_balance < forecast.minimum_reserve_pkr
        if is_breach:
            if first_breach_date is None:
                first_breach_date = curr_date
            gap = forecast.minimum_reserve_pkr - current_balance
            if gap > max_gap:
                max_gap = gap

        if current_balance < min_balance:
            min_balance = current_balance

        timeline.append(
            DailyBalance(
                date=curr_date,
                closing_balance_pkr=current_balance,
                net_change_pkr=net_change,
                is_breach=is_breach,
            )
        )
        curr_date += timedelta(days=1)

    return FeasibilityResult(
        activity_id=activity.activity_id,
        is_feasible=(first_breach_date is None),
        minimum_balance_pkr=min_balance,
        first_breach_date=first_breach_date,
        max_funding_gap_pkr=max_gap,
        project_events=project_events,
        timeline=timeline,
    )