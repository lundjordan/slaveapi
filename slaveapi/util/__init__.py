# general util helper methods


def normalize_truthiness(target_value):
    true_values = ['y', 'yes', '1', 'true']
    false_values = ['n', 'no', '0', 'false']

    # let's see if target_value is an accepted value first
    if not value_in_values(target_value, true_values + false_values):
        raise ValueError(
            "Unsupported value `%s` for truthiness. Accepted values: "
            "truthy - %s, falsy - %s" % (target_value, true_values, false_values)
        )

    if value_in_values(target_value, true_values):
        # target_value is a valid str and represents true
        return True
    else:
        # target_value is a valid str and represents false
        return False


def value_in_values(target_value, valid_values, case_sensitive=False):
    if not case_sensitive:
        # lower case all the things
        target_value = str(target_value).lower()
        valid_values = [str(valid_value).lower() for valid_value in valid_values]

    if target_value in valid_values:
        return True
    else:
        return False
