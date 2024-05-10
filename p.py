from time import time
from random import uniform
from decimal import Decimal
import logging


def main():
    """ Функция main():
        Назначение.
            Сравнить время работы float и Decimal
    :return: None
    """
    file_log = logging.FileHandler('time.log')
    console_log = logging.StreamHandler()

    logging.basicConfig(level=logging.INFO, handlers=(file_log, console_log),
                        format='%(asctime)s %(message)s')

    logging.info('     Вычис     float   decimal  больше')
    logging.info('     лений    секунд    секунд  в раз\n')
    number_of_arithmetic_operations = [10, 1_000, 10_000, 100_000, 1_000_000, 10_000_000]
    for n in number_of_arithmetic_operations:
        float_series1 = get_float_series(n, -5, 15)
        float_series2 = get_float_series(n, -5, 15)
        decimal_series1 = get_decimal_series(n, 2, -5, 15)
        decimal_series2 = get_decimal_series(n, 2, -5, 15)

        time_of_float = calculate_float(float_series1, float_series2)
        time_of_decimal = calculate_decimal(decimal_series1, decimal_series2)
        logging.info(f'{n:10_.0f}{time_of_float:10f}{time_of_decimal:10f}'
                     f'{1 if time_of_float == 0 else time_of_decimal/time_of_float:6.2f}')


def time_running(func):
    def wrapper(*args, **kwargs):
        time_begin = time()
        func(*args, **kwargs)
        time_end = time()
        return time_end - time_begin

    return wrapper


def get_float_series(n: int, a: float, b: float) -> list:
    result = []
    for i in range(n):
        result.append(uniform(a, b))
    return result


def get_decimal_series(n: int, digits: int, a: float, b: float) -> list:
    result = []
    for i in range(n):
        number = uniform(a, b)
        d = Decimal(f'{number:.{digits}f}')
        result.append(d)
    return result


@time_running
def calculate_float(series1: list, series2: list) -> int:
    check_len_series(series1, series2)
    result = 0.0
    for i in range(len(series1)):
        result += series1[i] * series2[i]
    return 0


@time_running
def calculate_decimal(series1: list, series2: list) -> int:
    check_len_series(series1, series2)
    result = Decimal('0.00')
    for i in range(len(series1)):
        result += series1[i] * series2[i]
    return 0


def check_len_series(series1, series2):
    if len(series1) != len(series2):
        raise ValueError(f'Длины последовательностей для вычислений ({len(series1)}) и ({len(series2)}) не равны\n'
                         f'Внутрення ошибка программы.')


if __name__ == '__main__':
    main()
