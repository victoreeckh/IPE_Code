def get_financials(Battery_case, cost_panels, pv_lifetime, cost_invertor,\
        invertor_lifetime, cost_battery, lifetime_battery, installation_cost,\
            annual_electricity_bill, electricity_bill_base, discount_rate):
    # Complete investment lumped in year 0
    #installation cost should only be different for the different configurations
    # e.g. gabble vs roof or if different amount of panels is installed
    if Battery_case == False:
        cost_battery = 0

    capex = cost_panels + cost_invertor/(invertor_lifetime/pv_lifetime) +\
                cost_battery/(lifetime_battery/pv_lifetime) +installation_cost
    Net_present_value = -capex
    yearly_gain = electricity_bill_base - annual_electricity_bill
    for y in range(0, pv_lifetime):  # Adjusted the range for zero-based indexing
        Net_present_value += yearly_gain / ((1 + discount_rate) **(y+1))

    payback_period = capex/yearly_gain
    return_on_investment = yearly_gain*pv_lifetime/capex

    return Net_present_value, payback_period, return_on_investment, capex

#capex is not only the cost of components but also installation cost and other one time costs
