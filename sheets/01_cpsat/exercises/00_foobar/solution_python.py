from data_schema import Instance, Solution


def solve(instance: Instance) -> Solution:
    """
    Implement your solver for the problem here!
    """

    numbers = instance.numbers

    numbers.sort()  #smallest element is first, biggest element is last

    return Solution(
        number_a=numbers[0],
        number_b=numbers[-1], #access last element
        distance=abs(numbers[0] - numbers[-1]),
    )
