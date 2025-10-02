function Div(el)
  if el.classes:includes('page-break') then
    return pandoc.RawBlock('latex', '\\newpage')
  end
end

return { Div = Div}