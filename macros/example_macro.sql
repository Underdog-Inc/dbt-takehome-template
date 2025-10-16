{% macro safe_cast(expr, type) -%}
  cast({{ expr }} as {{ type }})
{%- endmacro %} 