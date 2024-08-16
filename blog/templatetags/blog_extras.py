import re

from django import template

register = template.Library()


def get_replies(data):
    text = '<ul>'
    for comment in data:
        text += f'<li>{comment.pk}</li>'
        if comment.replies_list:
            text += get_replies(comment.replies_list)  # recursively calling to get the lists
    text += "</ul>"
    return text


# @register.filter(is_safe=True, name='recursive')
# def recursive(comments):
#     text = get_replies(comments)
#     return mark_safe(text)


@register.filter(name='has_group')
def has_group(user, group_name):
    return bool(user.groups.filter(name=group_name).exists())


@register.filter(name='remove_empty_paragraphs')
def remove_empty_paragraphs(value):
    return re.sub(r'<p>&nbsp;</p>', '', value)
