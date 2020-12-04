from functools import reduce

__author__ = 'hareesh'


class ImmutableList:
    """
    An unmodifiable List class which uses a closure to wrap the original list.
    Since nothing is truly private in python, even closures can be accessed and
    modified using the __closure__ member of a function. As, long as this is
    not done by the client, this can be considered as an unmodifiable list.

    This is a wrapper around the python list class
    which is passed in the constructor while creating an instance of this class.
    The second optional argument to the constructor 'copy_input_list' specifies
    whether to make a copy of the input list and use it to create the immutable
    list. To make the list truly immutable, this has to be set to True. The
    default value is False, which makes this a mere wrapper around the input
    list. In scenarios where the input list handle is not available to other
    pieces of code, for modification, this approach is fine. (E.g., scenarios
    where the input list is created as a local variable within a function OR
    it is a part of a library for which there is no public API to get a handle
    to the list).

    The instance of this class can be used in almost all scenarios where a
    normal python list can be used. For eg:
    01. It can be used in a for loop
    02. It can be used to access elements by index i.e. immList[i]
    03. It can be clubbed with other python lists and immutable lists. If
        lst is a python list and imm is an immutable list, the following can be
        performed to get a clubbed list:
        ret_list = lst + imm
        ret_list = imm + lst
        ret_list = imm + imm
    04. It can be multiplied by an integer to increase the size
        (imm * 4 or 4 * imm)
    05. It can be used in the slicing operator to extract sub lists (imm[3:4] or
        imm[:3] or imm[4:])
    06. The len method can be used to get the length of the immutable list.
    07. It can be compared with other immutable and python lists using the
        >, <, ==, <=, >= and != operators.
    08. Existence of an element can be checked with 'in' clause as in the case
        of normal python lists. (e.g. '2' in imm)
    09. The copy, count and index methods behave in the same manner as python
        lists.
    10. The str() method can be used to print a string representation of the
        list similar to the python list.
    """

    @staticmethod
    def _list_append(lst, val):
        """
        Private utility method used to append a value to an existing list and
        return the list itself (so that it can be used in funcutils.reduce
        method for chained invocations.

        @param lst: List to which value is to be appended
        @param val: The value to append to the list
        @return: The input list with an extra element added at the end.

        """
        lst.append(val)
        return lst

    @staticmethod
    def _methods_impl(lst, func_id, *args):
        """
        This static private method is where all the delegate methods are
        implemented. This function should be invoked with reference to the
        input list, the function id and other arguments required to
        invoke the function

        @param list: The list that the Immutable list wraps.

        @param func_id: should be the key of one of the functions listed in the
            'functions' dictionary, within the method.
        @param args: Arguments required to execute the function. Can be empty

        @return: The execution result of the function specified by the func_id
        """

        # returns iterator of the wrapped list, so that for loop and other
        # functions relying on the iterable interface can work.
        _il_iter = lambda: lst.__iter__()
        _il_get_item = lambda: lst[args[0]]  # index access method.
        _il_len = lambda: len(lst)  # length of the list
        _il_str = lambda: lst.__str__()  # string function
        # Following represent the >, < , >=, <=, ==, != operators.
        _il_gt = lambda: lst.__gt__(args[0])
        _il_lt = lambda: lst.__lt__(args[0])
        _il_ge = lambda: lst.__ge__(args[0])
        _il_le = lambda: lst.__le__(args[0])
        _il_eq = lambda: lst.__eq__(args[0])
        _il_ne = lambda: lst.__ne__(args[0])
        # The following is to check for existence of an element with the
        # in clause.
        _il_contains = lambda: lst.__contains__(args[0])
        # * operator with an integer to multiply the list size.
        _il_mul = lambda: lst.__mul__(args[0])
        # + operator to merge with another list and return a new merged
        # python list.
        _il_add = lambda: reduce(
            lambda x, y: ImmutableList._list_append(x, y), args[0], list(lst))
        # Reverse + operator, to have python list as the first operand of the
        # + operator.
        _il_radd = lambda: reduce(
            lambda x, y: ImmutableList._list_append(x, y), lst, list(args[0]))
        # Reverse * operator. (same as the * operator)
        _il_rmul = lambda: lst.__mul__(args[0])
        # Copy, count and index methods.
        _il_copy = lambda: lst.copy()
        _il_count = lambda: lst.count(args[0])
        _il_index = lambda: lst.index(
            args[0], args[1], args[2] if args[2] else len(lst))

        functions = {0: _il_iter, 1: _il_get_item, 2: _il_len, 3: _il_str,
                     4: _il_gt, 5: _il_lt, 6: _il_ge, 7: _il_le, 8: _il_eq,
                     9: _il_ne, 10: _il_contains, 11: _il_add, 12: _il_mul,
                     13: _il_radd, 14: _il_rmul, 15: _il_copy, 16: _il_count,
                     17: _il_index}

        return functions[func_id]()

    def __init__(self, input_lst, copy_input_list=False):
        """
        Constructor of the Immutable list. Creates a dynamic function/closure
        that wraps the input list, which can be later passed to the
        _methods_impl static method defined above. This is
        required to avoid maintaining the input list as a data member, to
        prevent the caller from accessing and modifying it.

        @param input_lst: The input list to be wrapped by the Immutable list.
        @param copy_input_list: specifies whether to clone the input list and
            use the clone in the instance. See class documentation for more
            details.
        @return:
        """

        assert(isinstance(input_lst, list))
        lst = list(input_lst) if copy_input_list else input_lst
        self._delegate_fn = lambda func_id, *args: \
            ImmutableList._methods_impl(lst, func_id, *args)

    # All overridden methods.
    def __iter__(self): return self._delegate_fn(0)

    def __getitem__(self, index): return self._delegate_fn(1, index)

    def __len__(self): return self._delegate_fn(2)

    def __str__(self): return self._delegate_fn(3)

    def __gt__(self, other): return self._delegate_fn(4, other)

    def __lt__(self, other): return self._delegate_fn(5, other)

    def __ge__(self, other): return self._delegate_fn(6, other)

    def __le__(self, other): return self._delegate_fn(7, other)

    def __eq__(self, other): return self._delegate_fn(8, other)

    def __ne__(self, other): return self._delegate_fn(9, other)

    def __contains__(self, item): return self._delegate_fn(10, item)

    def __add__(self, other): return self._delegate_fn(11, other)

    def __mul__(self, other): return self._delegate_fn(12, other)

    def __radd__(self, other): return self._delegate_fn(13, other)

    def __rmul__(self, other): return self._delegate_fn(14, other)

    def copy(self): return self._delegate_fn(15)

    def count(self, value): return self._delegate_fn(16, value)

    def index(self, value, start=0, stop=0):
        return self._delegate_fn(17, value, start, stop)


def main():
    lst1 = ['a', 'b', 'c']
    lst2 = ['p', 'q', 'r', 's']

    imm1 = ImmutableList(lst1)
    imm2 = ImmutableList(lst2)

    print('Imm1 = ' + str(imm1))
    print('Imm2 = ' + str(imm2))

    add_lst1 = lst1 + imm1
    print('Liist + Immutable List: ' + str(add_lst1))
    add_lst2 = imm1 + lst2
    print('Immutable List + List: ' + str(add_lst2))
    add_lst3 = imm1 + imm2
    print('Immutable Liist + Immutable List: ' + str(add_lst3))

    is_in_list = 'a' in lst1
    print("Is 'a' in lst1 ? " + str(is_in_list))

    slice1 = imm1[2:]
    slice2 = imm2[2:4]
    slice3 = imm2[:3]
    print('Slice 1: ' + str(slice1))
    print('Slice 2: ' + str(slice2))
    print('Slice 3: ' + str(slice3))

    imm1_times_3 = imm1 * 3
    print('Imm1 Times 3 = ' + str(imm1_times_3))
    three_times_imm2 = 3 * imm2
    print('3 Times Imm2 = ' + str(three_times_imm2))

    # For loop
    print('Imm1 in For Loop: ', end=' ')
    for x in imm1:
        print(x, end=' ')
    print()

    print("3rd Element in Imm1: '" + imm1[2] + "'")

    # Compare lst1 and imm1
    lst1_eq_imm1 = lst1 == imm1
    print("Are lst1 and imm1 equal? " + str(lst1_eq_imm1))

    imm2_eq_lst1 = imm2 == lst1
    print("Are imm2 and lst1 equal? " + str(imm2_eq_lst1))

    imm2_not_eq_lst1 = imm2 != lst1
    print("Are imm2 and lst1 different? " + str(imm2_not_eq_lst1))

    # Finally print the immutable lists again.
    print("Imm1 = " + str(imm1))
    print("Imm2 = " + str(imm2))

    # The following statemetns will give errors.
    # imm1[3] = 'h'
    # print(imm1)
    # imm1.append('d')
    # print(imm1)

if __name__ == '__main__':
    main()