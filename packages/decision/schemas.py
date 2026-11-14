from datetime import date
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class CashEvent(BaseModel):
    event_id: str
    date: date
    amount_pkr: int  # Inflows positive (+), Outflows negative (-)
    source_type: Literal["receivable", "payable", "recurring", "planned_activity", "other"]
    source_id: str
    is_estimated: bool = False
    scenario_id: str = "baseline"

class ScheduledItem(BaseModel):
    item_id: str
    date: date
    amount_pkr: int  # Always positive here; scheduler assigns +/- sign
    description: Optional[str] = None

class PlannedActivity(BaseModel):
    activity_id: str
    name: str
    start_date: date
    end_date: date
    costs: List[ScheduledItem] = Field(default_factory=list)
    receipts: List[ScheduledItem] = Field(default_factory=list)

class BaselineForecast(BaseModel):
    business_id: str
    as_of_date: date
    opening_balance_pkr: int
    minimum_reserve_pkr: int
    events: List[CashEvent] = Field(default_factory=list)

class DailyBalance(BaseModel):
    date: date
    closing_balance_pkr: int
    net_change_pkr: int
    is_breach: bool

class FeasibilityResult(BaseModel):
    activity_id: str
    is_feasible: bool
    minimum_balance_pkr: int
    first_breach_date: Optional[date] = None
    max_funding_gap_pkr: int  # Bridge amount needed to stay >= minimum_reserve
    project_events: List[CashEvent]
    timeline: List[DailyBalance]