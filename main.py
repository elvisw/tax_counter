from individual_income_cn_2019 import count_tax_2019, min_tax_2019
import argparse

def bonus_min(args):
    result = min_tax_2019(args.s,args.d)
    print(f'全年需要缴纳的个人所得税：{result[0]}')
    print(f'月薪：{result[1]}')
    print(f'年终奖：{result[2]}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='个人所得税计算工具')

    subparsers = parser.add_subparsers()

    parser_min = subparsers.add_parser('bonus_min')
    parser_min.add_argument(
        's', help='年薪', type=float)
    parser_min.add_argument(
        '-d', help='月度专项扣除', type=float, default=0.0)
    parser_min.set_defaults(func=bonus_min)

    args = parser.parse_args('bonus_min 200000'.split())
    args.func(args)    
    parser.parse_args(['-h'])

