def get_financials(capex, pv_lifetime, annual_electricity_bill, electricity_bill_base, discount_rate,):
    # Complete investment lumped in year 0
    Net_present_value = -capex
    yearly_gain = electricity_bill_base - annual_electricity_bill
    for y in range(0, pv_lifetime):  # Adjusted the range for zero-based indexing
        Net_present_value += yearly_gain / ((1 + discount_rate) **(y+1))

    payback_period = capex/yearly_gain
    return_on_investment = yearly_gain*pv_lifetime/capex

    return Net_present_value, payback_period, return_on_investment

#capex is not only the cost of components but also installation cost and other one time costs

results = get_financials(capex=10000, pv_lifetime=25, annual_electricity_bill=500,
                               electricity_bill_base=1900, discount_rate=0.05)
print(results)
