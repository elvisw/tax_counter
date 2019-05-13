from dataclasses import dataclass
from typing import Optional, List

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from mpl_toolkits.mplot3d import Axes3D

# 中华人民共和国个人所得税法: http://www.chinatax.gov.cn/n810341/n810755/c3967308/content.html
# 关于个人所得税法修改后有关优惠政策衔接问题的通知:
# http://www.chinatax.gov.cn/n810341/n810755/c3978994/content.html

# 数据类：https://docs.python.org/zh-cn/3.7/library/dataclasses.html#module-dataclasses
@dataclass
class TaxRate:
    """
    综合所得税率表
    start: 全月应纳税所得额范围起始
    end: 全月应纳税所得额范围起始
    rate: 税率
    deduction: 速算扣除数
    """
    start: Optional[float]  # Optional：可选类型
    end: Optional[float]
    rate: float
    deduction: float


def count_social_insurance(monthly_salary): 
    """
    社保计算
    """
    return 0


def check_tax_rate(tax_rates):
    pass


# 类型标注支持： https://docs.python.org/zh-cn/3/library/typing.html
def find_tax_rate(tax_rates: List[TaxRate], salary: float) -> Optional[TaxRate]:
    """
    根据月薪匹配税率
    :param tax_rates: 税率表
    :param salary: 月薪
    :return: 税率
    """
    for r in tax_rates:
        if ((r.start is None or r.start < salary)
                and (r.end is None or r.end >= salary)):
            return r
    raise Exception("Cannot find tax rate")


def count_tax(
        start_point: float,  # 月薪起征点
        tax_rates: List[TaxRate],  # 税率表
        monthly_salary: float,  # 月薪
        bonus: float,  # 年终奖
        deduction: float,  # 专项扣除
) -> float:
    """
    所得税计算
    :param start_point: float,  月薪起征点
    :param tax_rates: List[TaxRate],  税率表
    :param monthly_salary: float,  月薪
    :param bonus: float,  年终奖
    :param deduction: float,  专项扣除
    :return: float 应缴所得税
    """
    #每月应纳税所得额
    monthly_need_tax = monthly_salary - count_social_insurance(monthly_salary) - start_point - deduction
    if monthly_need_tax < 0:
        monthly_need_tax = 0
    monthly_tax_rate = find_tax_rate(tax_rates, monthly_need_tax)
    monthly_tax = monthly_need_tax * monthly_tax_rate.rate - monthly_tax_rate.deduction
    # 年终奖税率
    bonus_tax_rate = find_tax_rate(tax_rates, bonus / 12.0)
    # The bonus tax result is not the accumulated tax, it is what the law says, not a bug
    # 根据相关政策，年终奖税的结果不是累计税，这不是bug
    bonus_tax = bonus * bonus_tax_rate.rate - bonus_tax_rate.deduction
    return 12 * monthly_tax + bonus_tax


def min_tax(
        start_point: float,  # 月薪起征点
        tax_rates: List[TaxRate],  # 税率表
        all_salary: float,
        deduction: float,  # 专项扣除
) -> (float, float, float):
    """
    计算最优的年终奖方案
    :param start_point: float,   月薪起征点
    :param tax_rates: List[TaxRate],   税率表
    :param all_salary: float, 年薪
    :param deduction: float,   专项扣除
    :return: (全年需要缴纳的个人所得税, 月薪, 年终奖)
    """
    points = [r.start for r in tax_rates if r.start is not None]  # 将各个税率的非空的“全月应纳税所得额范围起始值”放入一个列表
    points.append(0)
    count_points = []

    for p in points:
        monthly_salary = start_point + deduction + p  # 月薪 = 月薪起征点 + 专项扣除 + 全月应纳税所得额范围起始值
        bonus = all_salary - 12 * monthly_salary  # 年终奖 = 年薪（函数参数） - 12 × 月薪
        if bonus < 0:
            break
        count_points.append((monthly_salary, bonus))
    count_points.append((all_salary/12.0, 0))

    for p in points:
        bonus = 12 * p  # 年终奖 = 12 × 全月应纳税所得额范围起始值
        monthly_salary = (all_salary - bonus) / 12.0  # 月薪 = (年薪（函数参数） - 年终奖） / 12
        if monthly_salary < 0:
            break
        count_points.append((monthly_salary, bonus))
    count_points.append((0, all_salary))

    # count_points列表里被加入了元组：不同税率的(全月应纳税所得额范围起始值, 对应的年终奖)，(年终奖为0时的月薪, 0)，(0, 年薪（全发年终奖）)

    min_tax_result = all_salary + 1
    min_monthly_salary = None
    min_bonus = None

    # 求tax的最小值，和tan为最小值时对应的monthly_salary和bonus
    for (monthly_salary, bonus) in count_points:
        if monthly_salary < 0 or bonus < 0:
            continue
        tax = count_tax(start_point, tax_rates, monthly_salary, bonus, deduction)
        # print("M: %f\tB:%f\tT:%f\t" % (monthly_salary, bonus, tax))
        if min_tax_result > tax:
            min_tax_result = tax
            min_monthly_salary = monthly_salary
            min_bonus = bonus
    # :return: 筹划计算的最优结果：(全年需要缴纳的个人所得税, 月薪, 年终奖)
    return min_tax_result, min_monthly_salary, min_bonus


tax_rates_2019 = [
    TaxRate(None, 3000, 0.03, 0),
    TaxRate(3000, 12000, 0.1, 210),
    TaxRate(12000, 25000, 0.2, 1410),
    TaxRate(25000, 35000, 0.25, 2660),
    TaxRate(35000, 55000, 0.3, 4410),
    TaxRate(55000, 80000, 0.35, 7160),
    TaxRate(80000, None, 0.45, 15160),
]

monthly_start_point_2019 = 60000 / 12.0


def count_tax_2019(monthly_salary, bonus, deduction):
    """
    计算个人所得税
    :param monthly_salary: 月薪
    :param bonus: 年终奖
    :param deduction: 每月专项扣除
    :return: 全年需要缴纳的个人所得税
    """
    return count_tax(monthly_start_point_2019, tax_rates_2019, monthly_salary,
                     bonus, deduction)


def min_tax_2019(year_salary, monthly_deduction):
    """
    计算最优的年终奖方案
    :param year_salary: 年薪
    :param monthly_deduction: 每月专项扣除
    :return: (全年需要缴纳的个人所得税, 月薪, 年终奖)
    """
    return min_tax(monthly_start_point_2019, tax_rates_2019, year_salary, monthly_deduction)


def draw_tax_2019():
    x = []
    y = []
    z = []
    for monthly_salary in range(0, 200000, 2000):
        for bonus in range(0, 2000000, 20000):
            salary = 12 * monthly_salary + bonus
            tax = count_tax_2019(monthly_salary, bonus, 0)
            after_tax = salary - tax
            x.append(monthly_salary)
            y.append(bonus)
            z.append(after_tax)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_trisurf(np.array(x), np.array(y), np.array(z))
    plt.show()


def draw_min_tax_2019():
    min_taxes = []
    all_salaries = []
    after_taxes = []
    avoid_taxes = []
    bonuses = []
    for all_salary in range(0, 3000000, 12000):
        tax, monthly_salary, bonus = min_tax_2019(all_salary, 0)
        raw_tax = count_tax_2019(all_salary / 12.0, 0, 0)
        print("All: %f\ttax: %f\tmonthly: %f\tbonus: %f" % (all_salary, tax, monthly_salary, bonus))
        all_salaries.append(all_salary)
        min_taxes.append(tax)
        after_taxes.append(all_salary-tax)
        avoid_taxes.append(raw_tax - tax)
        bonuses.append(bonus)
    plt.plot(all_salaries, all_salaries, label="Salary per year")
    plt.plot(all_salaries, min_taxes, label="Minimal tax")
    plt.plot(all_salaries, after_taxes, label="Salary after tax")
    plt.plot(all_salaries, avoid_taxes, label="Avoided tax")
    plt.plot(all_salaries, bonuses, label="Best bones divid")
    plt.xlabel('Salary per year')
    plt.ylabel('Money')
    plt.title("Tax Counter")
    plt.legend()
    plt.show()


# draw_tax_2019()
# draw_min_tax_2019()
