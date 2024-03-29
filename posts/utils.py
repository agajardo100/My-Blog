import re
import datetime
import math

from django.utils.html import strip_tags

# Utility functions go here

def count_words(html_string):
    word_string = strip_tags(html_string)
    matching_words = re.findall(r'\w+', word_string)
    count = len(matching_words)
    return count

def get_read_time(html_string):
    count = count_words(html_string)
    read_time_min = math.ceil((count/200.00)) # Assuming Avg person reads 200 words per min
    return read_time_min
