{% for key, var in variables.items %}
    window.{{ key }} = "{{ var }}";
{% endfor %}
