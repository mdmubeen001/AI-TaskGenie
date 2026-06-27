from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):

    if dictionary is None:

        return []

    return dictionary.get(key, [])


@register.filter
def get_all_items(dictionary):
    all_items = []
    if dictionary is not None:
        for key in dictionary:
            all_items.extend(dictionary[key])
    # Sort by deadline
    all_items.sort(key=lambda x: x.deadline)
    return all_items


@register.filter
def filter_tasks(tasks, status):
    return [task for task in tasks if task.status == status]


@register.filter
def filter_upcoming(tasks, today):
    return [task for task in tasks if task.deadline >= today]


@register.filter
def multiply(a, b):
    return a * b


@register.filter
def divide(a, b):
    if b == 0:
        return 0
    return a / b