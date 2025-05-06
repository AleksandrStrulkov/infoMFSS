from django import template

register = template.Library()


@register.filter(name="is_group")
def is_group(user, group_name):
    return user.groups.filter(name=group_name).exists()
