def find_days_left(base_chore):
    """Take a chore and find all unclaimed occurances"""
    for chore in userchores:
        if chore.commitment == 'INIT':
            pass
        elif chore.commitment:
            for day in chore.commitment:
                days_left = days_left.remove(day)
    return days_left