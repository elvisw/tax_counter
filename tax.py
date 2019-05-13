import xlwings as xw
from individual_income_cn_2019 import min_tax_2019


@xw.func
def bonus_min(year_salary,monthly_deduction):
    result = min_tax_2019(year_salary,monthly_deduction)
    return result[2]

@xw.func
def tax_result_min(year_salary,monthly_deduction):
    result = min_tax_2019(year_salary,monthly_deduction)
    return result[0]

if __name__ == '__main__':
    xw.serve()
