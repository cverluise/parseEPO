from parseepo.exception import SingleAttrException, RowException


def single_attr(val, attr, publication_number):
    if len(val) == 1:  # Temporary check, might be discarded if no error
        pass
    else:
        raise SingleAttrException(
            f"{publication_number}: Number of values exceed expected number "
            f"of values for Attr {attr}"
        )


def row(row_):
    if len(row_) == 7:
        pass
    else:
        raise RowException(
            f"Length of row different from expected length for row {row_}"
        )
