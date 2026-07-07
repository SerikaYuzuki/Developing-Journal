function Pandoc(doc)
  if FORMAT ~= "docx" then
    return doc
  end

  doc.meta.date = nil

  local section_break = [[
<w:p>
  <w:pPr>
    <w:sectPr>
      <w:type w:val="continuous"/>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="720" w:footer="720" w:gutter="0"/>
      <w:cols w:space="720"/>
      <w:docGrid w:linePitch="320"/>
    </w:sectPr>
  </w:pPr>
</w:p>
]]

  table.insert(doc.blocks, 1, pandoc.RawBlock("openxml", section_break))
  return doc
end
